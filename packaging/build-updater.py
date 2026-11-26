#!/usr/bin/env python3
"""Build a deterministic, self-contained updater executable for DEB and ZIP."""
import argparse
import os
import tempfile
import zipfile
from pathlib import Path

MODULES = {
    'ivivid-update': 'ivivid_discovery.py',
    'update_prepare.py': 'update_prepare.py',
    'deb_identity.py': 'deb_identity.py',
    'portable_activate.py': 'portable_activate.py',
    'portable_stage.py': 'portable_stage.py',
    'release_stage.py': 'release_stage.py',
    'release_auth.py': 'release_auth.py',
}
ENTRY = b'''import sys
if len(sys.argv) > 1 and sys.argv[1] == "prepare":
    del sys.argv[1]
    from update_prepare import main
else:
    from ivivid_discovery import main
sys.exit(main())
'''


def build(source, output):
    source, output = Path(source), Path(output)
    contents = {'__main__.py': ENTRY}
    for name, destination in MODULES.items():
        path = source / name
        if path.is_symlink() or not path.is_file():
            raise ValueError('Missing or unsafe updater module: ' + name)
        data = path.read_bytes()
        compile(data, destination, 'exec')
        contents[destination] = data
    if output.is_symlink() or (output.exists() and not output.is_file()):
        raise ValueError('Unsafe output path')
    fd, temporary = tempfile.mkstemp(prefix='.updater-', dir=output.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(b'#!/usr/bin/env python3\n')
            with zipfile.ZipFile(stream, 'w', compression=zipfile.ZIP_STORED) as archive:
                for name, data in sorted(contents.items()):
                    info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
                    info.create_system = 3
                    info.external_attr = 0o100644 << 16
                    archive.writestr(info, data)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary, 0o755)
        os.replace(temporary, output)
    finally:
        Path(temporary).unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    build(args.source, args.output)


if __name__ == '__main__':
    main()
