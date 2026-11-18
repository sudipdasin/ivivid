"""Stable data-only interface for optional independently distributed extensions.

No private implementation, license keys, or hidden feature algorithms belong here.
The public app must work without any extension installed.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Mapping, Tuple

API_VERSION = 1

@dataclass(frozen=True)
class Capability:
    identifier: str
    label: str
    description: str

@dataclass(frozen=True)
class ExtensionManifest:
    api_version: int
    extension_id: str
    display_name: str
    capabilities: Tuple[Capability, ...]

    def validate(self):
        if self.api_version != API_VERSION:
            raise ValueError("Unsupported extension API version")
        if not self.extension_id or not self.extension_id.replace("-", "").replace("_", "").isalnum():
            raise ValueError("Invalid extension ID")
        if not self.display_name.strip():
            raise ValueError("Display name required")
        ids = [c.identifier for c in self.capabilities]
        if any(not x or not x.replace("_", "").isalnum() for x in ids) or len(ids) != len(set(ids)):
            raise ValueError("Invalid or duplicate capability IDs")
        return self


def public_extension_manifest():
    return ExtensionManifest(API_VERSION, "ivivid-free", "iVivid Free", (
        Capability("mpv_presets", "mpv presets", "Open-source local playback configuration"),
    )).validate()
