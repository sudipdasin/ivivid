import subprocess
import tempfile
import unittest
from pathlib import Path
from deb_identity import verify_deb_identity


class DebTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.package = self.root / 'ivivid_2.6.0-beta.1_amd64.deb'

    def build(self, name='ivivid', arch='amd64', version='2.6.0~beta.1'):
        control = self.root / 'tree/DEBIAN/control'
        control.parent.mkdir(parents=True, exist_ok=True)
        control.write_text(f'Package: {name}\nVersion: {version}\nArchitecture: {arch}\nMaintainer: Test <test@example.invalid>\nDescription: Test fixture\n')
        subprocess.run(['dpkg-deb', '--build', str(control.parent.parent), str(self.package)], check=True, capture_output=True)

    def verify(self):
        return verify_deb_identity(self.package, '2.6.0-beta.1')

    def test_correct(self):
        self.build()
        self.assertEqual(self.verify()['Package'], 'ivivid')

    def test_wrong_package(self):
        self.build(name='other')
        with self.assertRaises(ValueError): self.verify()

    def test_wrong_arch(self):
        self.build(arch='arm64')
        with self.assertRaises(ValueError): self.verify()

    def test_wrong_version(self):
        self.build(version='2.5.0')
        with self.assertRaises(ValueError): self.verify()

    def test_legacy_beta_order(self):
        self.build(version='2.6.0-beta.1')
        with self.assertRaises(ValueError): self.verify()

    def test_corrupt(self):
        self.package.write_bytes(b'invalid deb')
        with self.assertRaises(ValueError): self.verify()

    def test_symlink(self):
        self.build()
        target = self.root / 'target.deb'
        self.package.rename(target)
        self.package.symlink_to(target)
        with self.assertRaises(ValueError): self.verify()

    def test_bad_version(self):
        with self.assertRaises(ValueError): verify_deb_identity(self.package, '../bad')


if __name__ == '__main__': unittest.main()
