#!/usr/bin/env python3
"""Create signed update metadata from completed iVivid release artifacts."""
import argparse
import hashlib
import json
import re
import subprocess
import tempfile
from pathlib import Path

TAG = re.compile(r'v(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(?:-beta\.(0|[1-9][0-9]*))?\Z', re.ASCII)
MAX_PACKAGE = 1024 * 1024 * 1024


def sign_release(tag, artifacts, private_key, output):
    if not TAG.fullmatch(tag):
        raise ValueError('Invalid release tag')
    artifacts, private_key, output = map(Path, (artifacts, private_key, output))
    if not artifacts.is_dir() or not private_key.is_file():
        raise ValueError('Missing artifacts or signing key')
    number = tag[1:]
    names = (f'ivivid_{number}_amd64.deb', f'ivivid-{number}-linux-amd64.zip')
    assets = {}
    for name in names:
        path = artifacts / name
        if path.is_symlink() or not path.is_file():
            raise ValueError('Missing or unsafe package: ' + name)
        digest = hashlib.sha256()
        size = 0
        with path.open('rb') as stream:
            while block := stream.read(1024 * 1024):
                size += len(block)
                if size > MAX_PACKAGE:
                    raise ValueError('Package too large')
                digest.update(block)
        if not size:
            raise ValueError('Empty package')
        assets[name] = dict(size=size, sha256=digest.hexdigest())
    manifest = dict(schema=1, repository='sudipdasin/ivivid', tag=tag, architecture='amd64', assets=assets)
    raw = (json.dumps(manifest, sort_keys=True, separators=(',', ':')) + '\n').encode()
    # Stage outside the output directory; never replace existing release metadata.
    with tempfile.TemporaryDirectory(prefix='ivivid-sign-') as tmp:
        root = Path(tmp)
        (root/'manifest.json').write_bytes(raw)
        subprocess.run(['openssl', 'dgst', '-sha256', '-sign', str(private_key.resolve()), '-out', str(root/'manifest.sig'), str(root/'manifest.json')], check=True, timeout=30, stdin=subprocess.DEVNULL)
        signature = (root/'manifest.sig').read_bytes()
        if not signature or len(signature) > 8192:
            raise ValueError('Invalid signature size')
        output.mkdir(mode=0o700, parents=False, exist_ok=False)
        try:
            (output/'manifest.json').write_bytes(raw)
            (output/'manifest.sig').write_bytes(signature)
        except BaseException:
            for name in ('manifest.json', 'manifest.sig'):
                (output/name).unlink(missing_ok=True)
            output.rmdir()
            raise
    return manifest


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--tag', required=True)
    p.add_argument('--artifacts', required=True)
    p.add_argument('--key', required=True, help='Externally managed private signing key; never commit it')
    p.add_argument('--output', required=True, help='New directory for signed metadata')
    a = p.parse_args()
    try:
        sign_release(a.tag, a.artifacts, a.key, a.output)
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        p.exit(1, 'Release signing failed: ' + str(error) + '\n')
    print('Signed metadata created; publication remains a separate step.')


if __name__ == '__main__':
    main()
