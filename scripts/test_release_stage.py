import shutil
import unittest
from test_release_sign import SigningTests
from release_stage import allowed_url, stage_release, SafeRedirect


class StageTests(unittest.TestCase):
    setUpClass = classmethod(SigningTests.setUpClass.__func__)
    tearDownClass = classmethod(SigningTests.tearDownClass.__func__)
    sign = SigningTests.sign
    def setUp(self):
        SigningTests.setUp(self)
        self.sign()
        self.cache = self.rootcase/'cache'
        self.cache.mkdir(mode=0o700)
        self.requests = []

    def fetch(self, url, dest, limit):
        self.requests.append(url)
        src = (self.output if dest.name.startswith('manifest.') else self.artifacts)/dest.name
        self.assertLessEqual(src.stat().st_size, limit)
        shutil.copyfile(src, dest)

    def stage(self, fmt='deb', key=None, fetch=None, tag='v2.6.0-beta.1'):
        return stage_release(tag, fmt, key or self.public, self.cache, fetch or self.fetch)

    def test_stage_both(self):
        for fmt, src in [('deb', self.deb), ('zip', self.zip)]:
            result = self.stage(fmt)
            self.assertEqual(result.read_bytes(), src.read_bytes())
            self.assertEqual(result.parent.stat().st_mode & 0o777, 0o700)
        self.assertEqual(len(self.requests), 6)

    def test_tampered_download_cleanup(self):
        self.deb.write_bytes(b'evil bytes')
        with self.assertRaises(ValueError): self.stage()
        self.assertEqual(list(self.cache.iterdir()), [])

    def test_network_failure_cleanup(self):
        def failed(url, dest, limit):
            self.fetch(url, dest, limit)
            raise OSError('offline')
        with self.assertRaises(OSError): self.stage(fetch=failed)
        self.assertEqual(list(self.cache.iterdir()), [])

    def test_invalid_identity(self):
        with self.assertRaises(ValueError): self.stage(tag='v2.6.0/evil')
        with self.assertRaises(ValueError): self.stage(fmt='exe')
        self.assertFalse(self.requests)

    def test_public_cache_rejected(self):
        self.cache.chmod(0o755)
        with self.assertRaises(ValueError): self.stage()
        self.assertFalse(self.requests)

    def test_untrusted_urls(self):
        for url in ['http://github.com/a', 'https://github.com.evil.org/a', 'https://evil@github.com/a', 'https://github.com:444/a', 'https://github.com/a#x']:
            self.assertFalse(allowed_url(url))
            with self.assertRaises(ValueError): SafeRedirect().redirect_request(None,None,302,'',{},url)
        self.assertTrue(allowed_url('https://release-assets.githubusercontent.com/a?token=fixture'))


if __name__ == '__main__': unittest.main(defaultTest='StageTests')
