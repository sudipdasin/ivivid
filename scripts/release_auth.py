"""Verify a staged iVivid package against an independently trusted RSA signing key."""
import hashlib
import json
import re
import stat
import subprocess
import tempfile
from pathlib import Path

TAG = re.compile(r'v(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(?:-beta\.(0|[1-9][0-9]*))?\Z', re.ASCII)
HEX = re.compile(r'[0-9a-f]{64}\Z', re.ASCII)
MAX_PACKAGE = 1024 * 1024 * 1024


def bounded(path, limit):
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise ValueError('Not a regular file')
    with path.open('rb') as stream:
        data = stream.read(limit + 1)
    if not data or len(data) > limit:
        raise ValueError('Invalid file size')
    return data


def unique_object(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError('Duplicate JSON key')
        obj[key] = value
    return obj


def verify_manifest(manifest, signature, public_key, expected_tag, expected_format):
    """Authenticate metadata before allocating package download bandwidth."""
    if not isinstance(expected_tag, str) or not TAG.fullmatch(expected_tag):
        raise ValueError('Invalid expected tag')
    if expected_format not in ('deb', 'zip'):
        raise ValueError('Invalid package format')
    number = expected_tag[1:]
    name = f'ivivid_{number}_amd64.deb' if expected_format == 'deb' else f'ivivid-{number}-linux-amd64.zip'
    raw = bounded(manifest, 65536)
    sig = bounded(signature, 8192)
    key = bounded(public_key, 16384)
    with tempfile.TemporaryDirectory(prefix='ivivid-auth-') as tmp:
        root = Path(tmp)
        for filename, contents in [('manifest', raw), ('signature', sig), ('key.pem', key)]:
            (root / filename).write_bytes(contents)
        result = subprocess.run(['openssl', 'dgst', '-sha256', '-verify', str(root/'key.pem'), '-signature', str(root/'signature'), str(root/'manifest')], capture_output=True, timeout=10, check=False)
        if result.returncode != 0:
            raise ValueError('Release signature verification failed')
    data = json.loads(raw, object_pairs_hook=unique_object)
    if not isinstance(data, dict) or set(data) != {'schema', 'repository', 'tag', 'architecture', 'assets'} or type(data['schema']) is not int or data['schema'] != 1 or data['repository'] != 'sudipdasin/ivivid' or data['tag'] != expected_tag or data['architecture'] != 'amd64':
        raise ValueError('Manifest identity mismatch')
    assets = data['assets']
    if not isinstance(assets, dict) or name not in assets:
        raise ValueError('Package missing in signed manifest')
    asset = assets[name]
    if not isinstance(asset, dict) or set(asset) != {'size', 'sha256'} or type(asset['size']) is not int or not 0 < asset['size'] <= MAX_PACKAGE or not isinstance(asset['sha256'], str) or not HEX.fullmatch(asset['sha256']):
        raise ValueError('Invalid asset metadata')
    return name, asset['size'], asset['sha256']


def verify_payload(package, metadata):
    name, size, sha256 = metadata
    package = Path(package)
    if package.name != name or package.is_symlink() or not stat.S_ISREG(package.stat().st_mode):
        raise ValueError('Incorrect package file')
    digest = hashlib.sha256()
    count = 0
    with package.open('rb') as stream:
        while block := stream.read(1024 * 1024):
            count += len(block)
            if count > size:
                raise ValueError('Package size mismatch')
            digest.update(block)
    if count != size or digest.hexdigest() != sha256:
        raise ValueError('Package integrity mismatch')
    return digest.hexdigest()


def verify_package(manifest, signature, public_key, package, expected_tag, expected_format):
    """Verify signed metadata and package bytes against the trusted key."""
    return verify_payload(package, verify_manifest(manifest, signature, public_key, expected_tag, expected_format))
