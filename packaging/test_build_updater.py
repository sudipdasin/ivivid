import importlib.util
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

spec = importlib.util.spec_from_file_location('builder', Path(__file__).with_name('build-updater.py'))
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class BundleTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source = self.root / 'source'
        self.source.mkdir()
        self.output = self.root / 'ivivid-update'
        for name in builder.MODULES:
            (self.source / name).write_text('VALUE = 1\n')
        (self.source / 'ivivid-update').write_text('import sys\ndef main():\n print("check", *sys.argv[1:]); return 0\n')
        (self.source / 'update_prepare.py').write_text('import sys\nfrom release_auth import VALUE\ndef main():\n print("prepare", VALUE, *sys.argv[1:]); return 0\n')

    def build(self):
        builder.build(self.source, self.output)

    def run_helper(self, *args):
        return subprocess.check_output([sys.executable, str(self.output), *args], text=True, cwd=self.root).strip()

    def test_dispatch_and_self_contained(self):
        self.build()
        shutil.rmtree(self.source)
        self.assertEqual(self.run_helper('--current', '2.5.0'), 'check --current 2.5.0')
        self.assertEqual(self.run_helper('prepare', '--target', '2.6.0'), 'prepare 1 --target 2.6.0')
        self.assertEqual(self.output.stat().st_mode & 0o777, 0o755)

    def test_deterministic(self):
        self.build()
        before = self.output.read_bytes()
        self.build()
        self.assertEqual(before, self.output.read_bytes())

    def test_exact_archive_members(self):
        self.build()
        with zipfile.ZipFile(self.output) as archive:
            self.assertEqual(set(archive.namelist()), set(builder.MODULES.values()) | {'__main__.py'})
            self.assertIsNone(archive.testzip())

    def test_missing_source_preserves_output(self):
        self.build()
        before = self.output.read_bytes()
        (self.source / 'release_auth.py').unlink()
        with self.assertRaises(ValueError): self.build()
        self.assertEqual(before, self.output.read_bytes())

    def test_invalid_python(self):
        (self.source / 'release_auth.py').write_text('def broken(')
        with self.assertRaises(SyntaxError): self.build()
        self.assertFalse(self.output.exists())

    def test_symlink_source(self):
        path = self.source / 'release_auth.py'
        path.unlink()
        path.symlink_to(self.source / 'deb_identity.py')
        with self.assertRaises(ValueError): self.build()

    def test_symlink_destination(self):
        target = self.root / 'untouched'
        target.write_bytes(b'keep')
        self.output.symlink_to(target)
        with self.assertRaises(ValueError): self.build()
        self.assertEqual(target.read_bytes(), b'keep')


if __name__ == '__main__':
    unittest.main()
