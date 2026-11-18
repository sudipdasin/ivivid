"""Pure stdlib tests: python3 -m unittest discover -s tests -v"""
import tempfile
import unittest
from pathlib import Path
from ivivid_core.editions import FREE, require_public_feature
from ivivid_core.extension_contract import API_VERSION, Capability, ExtensionManifest
from tools.check_public_boundary import check_tree


class EditionTests(unittest.TestCase):
    def test_free_features(self):
        self.assertFalse(FREE.proprietary)
        require_public_feature("igpu_detection")
        with self.assertRaises(ValueError):
            require_public_feature("proprietary_render")

    def test_manifest_validation(self):
        good = ExtensionManifest(API_VERSION, "vendor-pro", "Pro", (Capability("x", "X", "Description"),))
        self.assertEqual(good.validate(), good)
        with self.assertRaises(ValueError):
            ExtensionManifest(99, "x", "X", ()).validate()
        with self.assertRaises(ValueError):
            ExtensionManifest(API_VERSION, "x", "X", (Capability("x", "", ""), Capability("x", "", ""))).validate()

    def test_private_import_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            (Path(temp) / "app.py").write_text("import ivivid_pro.secret\\n".replace("\\n", "\n"))
            self.assertTrue(check_tree(temp))

    def test_public_module_allowed(self):
        with tempfile.TemporaryDirectory() as temp:
            (Path(temp) / "app.py").write_text("from ivivid_core import editions\n")
            self.assertFalse(check_tree(temp))


if __name__ == "__main__":
    unittest.main()
