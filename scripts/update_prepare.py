"""Prepare an authenticated upgrade for review; never install or execute it."""
import argparse
import hashlib
import json
import platform
import shutil
import sys
import tempfile
from pathlib import Path

from deb_identity import verify_deb_identity
from portable_activate import order
from portable_stage import extract_portable
from release_stage import stage_release, download
from release_auth import bounded


def prepare(current, target, channel, fmt, public_key, fingerprint, cache, fetch=download):
    if channel not in ('stable', 'beta') or fmt not in ('deb', 'zip'):
        raise ValueError('Invalid update channel or format')
    if order(target) <= order(current) or (channel == 'stable' and '-beta.' in target):
        raise ValueError('Update is not eligible for this version/channel')
    if platform.machine() not in ('x86_64', 'amd64'):
        raise ValueError('Unsupported architecture')
    key = Path(public_key)
    key_bytes = bounded(key, 16384)
    if hashlib.sha256(key_bytes).hexdigest() != fingerprint:
        raise ValueError('Trusted key fingerprint mismatch')
    # Pin the exact checked bytes for this transaction, not a mutable path.
    with tempfile.TemporaryDirectory(prefix='ivivid-trust-') as directory:
        snapshot = Path(directory) / 'trusted.pem'
        snapshot.write_bytes(key_bytes)
        snapshot.chmod(0o600)
        package = stage_release('v' + target, fmt, snapshot, cache, fetch=fetch)
    try:
        if fmt == 'deb':
            verify_deb_identity(package, target)
            return {'version': target, 'package': str(package), 'portable_tree': None}
        tree = extract_portable(package, target, package.parent)
        return {'version': target, 'package': str(package), 'portable_tree': str(tree)}
    except BaseException:
        shutil.rmtree(package.parent)
        raise


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for arg in ('current', 'target', 'public-key', 'fingerprint', 'cache'):
        p.add_argument('--' + arg, required=True)
    p.add_argument('--channel', choices=('stable', 'beta'), required=True)
    p.add_argument('--format', choices=('deb', 'zip'), required=True)
    a = p.parse_args()
    try:
        result = prepare(a.current, a.target, a.channel, a.format, a.public_key, a.fingerprint, a.cache)
    except Exception as error:
        print('Update preparation failed: ' + str(error), file=sys.stderr)
        return 1
    print(json.dumps(result))
    return 0


if __name__ == '__main__':
    sys.exit(main())
