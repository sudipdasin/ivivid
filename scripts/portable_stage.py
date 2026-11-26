"""Extract an already authenticated iVivid ZIP without touching an installation."""
import os
import re
import shutil
import stat
import tempfile
import zipfile
from pathlib import Path

VERSION = re.compile(r'(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(-beta\.(0|[1-9][0-9]*))?\Z')
FILES = {'bin/iVivid': 0o755, 'bin/ivivid-play': 0o755,
         'bin/ivivid-update': 0o755, 'iVivid.desktop': 0o644, 'README.txt': 0o644}
LIMIT = 256 * 1024 * 1024


def extract_portable(package, version, cache):
    if not isinstance(version, str) or not VERSION.fullmatch(version):
        raise ValueError('Invalid version')
    root = 'ivivid-' + version + '-linux-amd64'
    package, cache = Path(package), Path(cache)
    if package.name != root + '.zip' or package.is_symlink() or not package.is_file():
        raise ValueError('Incorrect archive')
    if cache.is_symlink() or not cache.is_dir() or cache.stat().st_uid != os.getuid() or cache.stat().st_mode & 0o077:
        raise ValueError('Private cache required')
    with zipfile.ZipFile(package) as archive:
        seen = set()
        entries = {}
        total = 0
        for item in archive.infolist():
            name = item.filename
            mode = item.external_attr >> 16
            kind = stat.S_IFMT(mode)
            if name in seen or item.flag_bits & 1:
                raise ValueError('Duplicate or encrypted archive entry')
            seen.add(name)
            if name in (root + '/', root + '/bin/') and item.is_dir() and kind in (0, stat.S_IFDIR):
                continue
            relative = name.removeprefix(root + '/')
            if name == relative or relative not in FILES or item.is_dir() or kind not in (0, stat.S_IFREG):
                raise ValueError('Unexpected archive entry')
            total += item.file_size
            if not item.file_size or total > LIMIT:
                raise ValueError('Invalid extracted size')
            entries[relative] = item
        if set(entries) != set(FILES):
            raise ValueError('Incomplete portable bundle')
        stage = Path(tempfile.mkdtemp(prefix='ivivid-portable-', dir=cache))
        try:
            (stage / 'bin').mkdir(mode=0o700)
            for relative, item in entries.items():
                target = stage / relative
                count = 0
                with archive.open(item) as source, target.open('xb') as output:
                    while block := source.read(1024 * 1024):
                        count += len(block)
                        if count > item.file_size:
                            raise ValueError('Entry exceeds declared size')
                        output.write(block)
                if count != item.file_size:
                    raise ValueError('Truncated entry')
                target.chmod(FILES[relative])
            return stage
        except BaseException:
            shutil.rmtree(stage)
            raise
