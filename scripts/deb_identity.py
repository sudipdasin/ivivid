"""Check authenticated Debian packages without installing or elevating."""
import re
import subprocess
from pathlib import Path

VERSION = re.compile(r'(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(?:-beta\.(0|[1-9][0-9]*))?\Z', re.ASCII)


def verify_deb_identity(package, version):
    if not isinstance(version, str) or not VERSION.fullmatch(version):
        raise ValueError('Invalid application version')
    package = Path(package)
    if package.name != f'ivivid_{version}_amd64.deb' or package.is_symlink() or not package.is_file():
        raise ValueError('Invalid package path')
    expected = {'Package': 'ivivid', 'Architecture': 'amd64', 'Version': version.replace('-beta.', '~beta.')}
    for field, value in expected.items():
        result = subprocess.run(['dpkg-deb', '-f', str(package.resolve()), field], capture_output=True, text=True, timeout=10, check=False)
        if result.returncode != 0 or result.stdout.rstrip('\n') != value:
            raise ValueError('Debian metadata mismatch: ' + field)
    return expected
