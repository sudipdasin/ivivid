import stat
import tempfile
import unittest
import warnings
import zipfile
from pathlib import Path
from portable_stage import extract_portable, FILES


class PortableTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.cache = Path(self.tmp.name)
        self.root = 'ivivid-2.6.0-beta.1-linux-amd64'
        self.package = self.cache / (self.root + '.zip')

    def make(self, omit=None, extra=None, symlink=None):
        with zipfile.ZipFile(self.package, 'w') as z:
            for name in FILES:
                if name == omit:
                    continue
                info = zipfile.ZipInfo(self.root + '/' + name)
                info.create_system = 3
                info.external_attr = ((stat.S_IFLNK if name == symlink else stat.S_IFREG) | 0o777) << 16
                z.writestr(info, b'fixture')
            if extra:
                with warnings.catch_warnings():
                    warnings.simplefilter('ignore', UserWarning)
                    z.writestr(extra, b'bad')

    def extract(self):
        return extract_portable(self.package, '2.6.0-beta.1', self.cache)

    def rejected(self):
        with self.assertRaises(ValueError):
            self.extract()
        self.assertEqual(list(self.cache.iterdir()), [self.package])

    def test_valid(self):
        self.make()
        result = self.extract()
        for name, mode in FILES.items():
            self.assertEqual((result/name).read_bytes(), b'fixture')
            self.assertEqual((result/name).stat().st_mode & 0o777, mode)

    def test_traversal(self):
        self.make(extra=self.root+'/../../outside')
        self.rejected()

    def test_absolute(self):
        self.make(extra='/tmp/outside')
        self.rejected()

    def test_duplicate(self):
        self.make(extra=self.root+'/bin/iVivid')
        self.rejected()

    def test_symlink(self):
        self.make(symlink='bin/iVivid')
        self.rejected()

    def test_missing(self):
        self.make(omit='bin/ivivid-update')
        self.rejected()

    def test_wrong_version(self):
        self.make()
        with self.assertRaises(ValueError):
            extract_portable(self.package, '2.7.0', self.cache)

    def test_public_cache(self):
        self.make()
        self.cache.chmod(0o755)
        self.rejected()


if __name__ == '__main__': unittest.main()
