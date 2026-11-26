"""Download a specific release into private staging, never execute it."""
import os
import shutil
import tempfile
import urllib.request
from pathlib import Path
from urllib.parse import urlsplit
from release_auth import TAG, MAX_PACKAGE, verify_package

BASE = 'https://github.com/sudipdasin/ivivid/releases/download/'
HOSTS = {'github.com', 'release-assets.githubusercontent.com', 'objects.githubusercontent.com'}


def allowed_url(url):
    try:
        p = urlsplit(url)
        return p.scheme == 'https' and p.hostname in HOSTS and p.port in (None, 443) and p.username is None and p.password is None and not p.fragment
    except ValueError:
        return False


class SafeRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if not allowed_url(newurl):
            raise ValueError('Untrusted release redirect')
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def download(url, destination, limit):
    if not allowed_url(url):
        raise ValueError('Untrusted release URL')
    opener = urllib.request.build_opener(SafeRedirect())
    request = urllib.request.Request(url, headers={'User-Agent': 'iVivid-update-stage', 'Accept-Encoding': 'identity'})
    with opener.open(request, timeout=15) as response, destination.open('xb') as output:
        if not allowed_url(response.geturl()):
            raise ValueError('Untrusted final release URL')
        count = 0
        while block := response.read(1024 * 1024):
            count += len(block)
            if count > limit:
                raise ValueError('Release download too large')
            output.write(block)
        if not count:
            raise ValueError('Empty release download')


def stage_release(tag, fmt, public_key, cache, fetch=download):
    if not isinstance(tag, str) or not TAG.fullmatch(tag) or fmt not in ('deb', 'zip'):
        raise ValueError('Invalid release identity')
    number = tag[1:]
    name = f'ivivid_{number}_amd64.deb' if fmt == 'deb' else f'ivivid-{number}-linux-amd64.zip'
    cache = Path(cache)
    if cache.is_symlink() or not cache.is_dir() or cache.stat().st_uid != os.getuid() or cache.stat().st_mode & 0o077:
        raise ValueError('Staging parent must be a private user-owned directory')
    stage = Path(tempfile.mkdtemp(prefix='ivivid-stage-', dir=cache))
    try:
        for filename, limit in [('manifest.json', 65536), ('manifest.sig', 8192), (name, MAX_PACKAGE)]:
            fetch(BASE + tag + '/' + filename, stage / filename, limit)
        verify_package(stage/'manifest.json', stage/'manifest.sig', public_key, stage/name, tag, fmt)
        return stage/name
    except BaseException:
        shutil.rmtree(stage)
        raise
