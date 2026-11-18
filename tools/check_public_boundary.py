#!/usr/bin/env python3
"""Fail-closed public source-tree guard. Run before publishing free artifacts."""
from __future__ import annotations
import argparse
import ast
from pathlib import Path
import sys

BLOCKED_DIRS = {"pro", "premium", "enterprise", "proprietary", "private", "secrets", "licenses_private"}
BLOCKED_IMPORTS = ("ivivid_pro", "ivivid_private", "proprietary", "premium_engine")
BLOCKED_SUFFIXES = {".key", ".pem", ".p12", ".pfx"}


def check_tree(root):
    root = Path(root)
    problems = []
    for path in root.rglob("*"):
        rel = path.relative_to(root)
        if any(p in {".git", "__pycache__", ".venv", "venv"} for p in rel.parts):
            continue
        if any(part.lower() in BLOCKED_DIRS for part in rel.parts):
            problems.append(f"Private path present: {rel}")
        if not path.is_file():
            continue
        if path.suffix.lower() in BLOCKED_SUFFIXES:
            problems.append(f"Potential key material: {rel}")
        if path.suffix != ".py":
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(rel))
        except (SyntaxError, UnicodeError, OSError) as exc:
            problems.append(f"Unparseable Python: {rel}: {exc}")
            continue
        for node in ast.walk(tree):
            names = []
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module]
            for name in names:
                if any(name == prefix or name.startswith(prefix + ".") for prefix in BLOCKED_IMPORTS):
                    problems.append(f"Private import {name}: {rel}:{node.lineno}")
    return problems


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    problems = check_tree(Path(args.root))
    for item in problems:
        print("FAIL:", item)
    print("Public boundary:", "PASS" if not problems else "FAIL")
    return int(bool(problems))

if __name__ == "__main__":
    sys.exit(main())
