import hashlib
import shutil
import subprocess
import unittest
import zipfile
from test_release_sign import SigningTests
from release_sign import sign_release
from portable_stage import FILES
from update_prepare import prepare


class PrepareTests(unittest.TestCase):
    setUpClass = classmethod(SigningTests.setUpClass.__func__)
    tearDownClass = classmethod(SigningTests.tearDownClass.__func__)
    sign = SigningTests.sign

    def setUp(self):
        SigningTests.setUp(self)
        control = self.rootcase / 'deb/DEBIAN/control'
        control.parent.mkdir(parents=True)
        control.write_text('Package: ivivid\nVersion: 2.6.0~beta.1\nArchitecture: amd64\nMaintainer: Test <test@example.invalid>\nDescription: fixture\n')
        subprocess.run(['dpkg-deb', '--build', str(control.parent.parent), str(self.deb)], check=True, capture_output=True)
        with zipfile.ZipFile(self.zip, 'w') as z:
            for name in FILES:
                z.writestr('ivivid-2.6.0-beta.1-linux-amd64/' + name, b'fixture')
        self.sign()
        self.cache = self.rootcase / 'cache'
        self.cache.mkdir(mode=0o700)
        self.fingerprint = hashlib.sha256(self.public.read_bytes()).hexdigest()
        self.requests = []

    def fetch(self, url, dest, limit):
        self.requests.append(url)
        source = (self.output if dest.name.startswith('manifest.') else self.artifacts) / dest.name
        self.assertLessEqual(source.stat().st_size, limit)
        shutil.copyfile(source, dest)

    def prepare(self, fmt='deb', current='2.5.0', channel='beta', fingerprint=None):
        return prepare(current, '2.6.0-beta.1', channel, fmt, self.public, fingerprint or self.fingerprint, self.cache, self.fetch)

    def test_real_deb(self):
        result = self.prepare()
        self.assertIsNone(result['portable_tree'])
        self.assertEqual(result['version'], '2.6.0-beta.1')

    def test_zip(self):
        from pathlib import Path
        result = self.prepare('zip')
        self.assertEqual((Path(result['portable_tree']) / 'bin/iVivid').read_bytes(), b'fixture')

    def test_downgrade(self):
        with self.assertRaises(ValueError): self.prepare(current='2.6.0')
        self.assertFalse(self.requests)

    def test_stable_channel(self):
        with self.assertRaises(ValueError): self.prepare(channel='stable')
        self.assertFalse(self.requests)

    def test_wrong_fingerprint(self):
        with self.assertRaises(ValueError): self.prepare(fingerprint='0'*64)
        self.assertFalse(self.requests)

    def test_signed_invalid_deb(self):
        self.deb.write_bytes(b'not a Debian package')
        shutil.rmtree(self.output)
        self.sign()
        with self.assertRaises(ValueError): self.prepare()
        self.assertFalse(list(self.cache.iterdir()))

    def test_signed_invalid_zip(self):
        self.zip.write_bytes(b'not a ZIP')
        shutil.rmtree(self.output)
        self.sign()
        with self.assertRaises(zipfile.BadZipFile): self.prepare('zip')
        self.assertFalse(list(self.cache.iterdir()))


if __name__ == '__main__': unittest.main(defaultTest='PrepareTests')
