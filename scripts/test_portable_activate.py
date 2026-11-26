import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from portable_activate import activate, rollback, FILES


class ActivationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root/'versions').mkdir(mode=0o700)
        for version in ('2.5.0', '2.6.0-beta.1', '2.6.0', '2.7.0'):
            tree = self.root/'versions'/version
            tree.mkdir(mode=0o700)
            (tree/'bin').mkdir(mode=0o700)
            for name in FILES:
                (tree/name).write_bytes(b'fixture')
        self.state = self.root/'active.json'

    def activate(self, version, check=lambda path: True):
        return activate(self.root, version, check)

    def test_initial_upgrade_rollback(self):
        self.activate('2.5.0')
        self.activate('2.6.0-beta.1')
        self.activate('2.6.0')
        self.assertEqual(rollback(self.root).name, '2.6.0-beta.1')
        self.assertEqual(json.loads(self.state.read_text()), dict(current='2.6.0-beta.1', previous=None, highest='2.6.0'))
        with self.assertRaises(ValueError): self.activate('2.6.0')
        self.activate('2.7.0')

    def test_failed_health(self):
        self.activate('2.5.0')
        before = self.state.read_bytes()
        with self.assertRaises(ValueError): self.activate('2.6.0', lambda path: False)
        self.assertEqual(self.state.read_bytes(), before)

    def test_replace_failure(self):
        self.activate('2.5.0')
        before = self.state.read_bytes()
        with patch('portable_activate.os.replace', side_effect=OSError('simulated failure')):
            with self.assertRaises(OSError): self.activate('2.6.0')
        self.assertEqual(self.state.read_bytes(), before)
        self.assertFalse(list(self.root.glob('.active-*')))

    def test_downgrade(self):
        self.activate('2.6.0')
        with self.assertRaises(ValueError): self.activate('2.5.0')

    def test_corrupt_state(self):
        self.state.write_text('{bad')
        with self.assertRaises(ValueError): self.activate('2.6.0')
        self.assertEqual(self.state.read_text(), '{bad')

    def test_missing_file(self):
        (self.root/'versions/2.6.0/bin/iVivid').unlink()
        with self.assertRaises(ValueError): self.activate('2.6.0')
        self.assertFalse(self.state.exists())

    def test_symlink(self):
        path = self.root/'versions/2.6.0/bin/iVivid'
        path.unlink()
        path.symlink_to(self.root/'versions/2.5.0/bin/iVivid')
        with self.assertRaises(ValueError): self.activate('2.6.0')

    def test_no_rollback(self):
        self.activate('2.5.0')
        with self.assertRaises(ValueError): rollback(self.root)

    def test_bad_version(self):
        with self.assertRaises(ValueError): self.activate('../escape')

    def test_public_root(self):
        self.root.chmod(0o755)
        with self.assertRaises(ValueError): self.activate('2.6.0')


if __name__ == '__main__': unittest.main()
