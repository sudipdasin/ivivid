"""Atomic selection of preverified portable versions; no execution or elevation."""
import fcntl
import json
import os
import re
import tempfile
from contextlib import contextmanager
from pathlib import Path

VERSION = re.compile(r'(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(?:-beta\.(0|[1-9][0-9]*))?\Z', re.ASCII)
FILES = ('bin/iVivid', 'bin/ivivid-play', 'bin/ivivid-update', 'iVivid.desktop', 'README.txt')


def order(value):
    match = VERSION.fullmatch(value) if isinstance(value, str) else None
    if not match:
        raise ValueError('Invalid version')
    a, b, c, beta = match.groups()
    return int(a), int(b), int(c), beta is None, int(beta or 0)


def private_dir(path):
    if path.is_symlink() or not path.is_dir() or path.stat().st_uid != os.getuid() or path.stat().st_mode & 0o077:
        raise ValueError('Private user-owned directory required')


@contextmanager
def locked(root):
    private_dir(root)
    private_dir(root / 'versions')
    fd = os.open(root / '.activation.lock', os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW | os.O_NONBLOCK, 0o600)
    with os.fdopen(fd, 'r+b') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        yield


def validate_tree(root, version):
    order(version)
    tree = root / 'versions' / version
    private_dir(tree)
    private_dir(tree / 'bin')
    for name in FILES:
        path = tree / name
        if path.is_symlink() or not path.is_file() or path.stat().st_uid != os.getuid() or path.stat().st_mode & 0o022 or not path.stat().st_size:
            raise ValueError('Invalid staged file: ' + name)
    return tree


def read_state(root):
    path = root / 'active.json'
    if path.is_symlink():
        raise ValueError('Unsafe activation state')
    if not path.exists():
        return None
    if not path.is_file() or path.stat().st_size > 4096:
        raise ValueError('Invalid activation state')
    state = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(state, dict) or set(state) != {'current', 'previous', 'highest'}:
        raise ValueError('Invalid activation state')
    current, previous, highest = state['current'], state['previous'], state['highest']
    if order(current) > order(highest) or (previous is not None and (order(previous) >= order(current))):
        raise ValueError('Invalid activation history')
    return state


def save_state(root, state):
    fd, temp = tempfile.mkstemp(prefix='.active-', dir=root)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as output:
            json.dump(state, output, sort_keys=True)
            output.flush()
            os.fsync(output.fileno())
        os.replace(temp, root / 'active.json')
        dirfd = os.open(root, os.O_DIRECTORY)
        try:
            os.fsync(dirfd)
        finally:
            os.close(dirfd)
    finally:
        Path(temp).unlink(missing_ok=True)


def activate(root, version, health_check):
    """Caller authenticates and stages files in versions/VERSION before calling.

    The callback must return True after a bounded health check; this module
    never executes the staged files itself. Call after the old app exits.
    """
    root = Path(root)
    with locked(root):
        state = read_state(root)
        if state is not None and order(version) <= order(state['highest']):
            raise ValueError('Version is not newer than the activation high-water mark')
        tree = validate_tree(root, version)
        if health_check(tree) is not True:
            raise ValueError('Health check failed')
        save_state(root, dict(current=version, previous=state['current'] if state else None, highest=version))
        return tree


def rollback(root):
    root = Path(root)
    with locked(root):
        state = read_state(root)
        if state is None or state['previous'] is None:
            raise ValueError('No previous version')
        tree = validate_tree(root, state['previous'])
        save_state(root, dict(current=state['previous'], previous=None, highest=state['highest']))
        return tree
