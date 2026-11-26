import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from release_sign import sign_release


class SigningTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.tmp.name)
        cls.key = cls.root/'private.pem'
        cls.public = cls.root/'public.pem'
        subprocess.run(['openssl','genpkey','-algorithm','RSA','-pkeyopt','rsa_keygen_bits:2048','-out',str(cls.key)],check=True,capture_output=True)
        subprocess.run(['openssl','pkey','-in',str(cls.key),'-pubout','-out',str(cls.public)],check=True,capture_output=True)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def setUp(self):
        self.case = tempfile.TemporaryDirectory(dir=self.root)
        self.addCleanup(self.case.cleanup)
        self.rootcase = Path(self.case.name)
        self.artifacts = self.rootcase/'dist'
        self.artifacts.mkdir()
        self.output = self.rootcase/'signed'
        self.deb = self.artifacts/'ivivid_2.6.0-beta.1_amd64.deb'
        self.zip = self.artifacts/'ivivid-2.6.0-beta.1-linux-amd64.zip'
        self.deb.write_bytes(b'deb fixture')
        self.zip.write_bytes(b'zip fixture')

    def sign(self, tag='v2.6.0-beta.1', key=None):
        return sign_release(tag,self.artifacts,key or self.key,self.output)

    def verify(self):
        return subprocess.run(['openssl','dgst','-sha256','-verify',str(self.public),'-signature',str(self.output/'manifest.sig'),str(self.output/'manifest.json')],capture_output=True).returncode

    def test_roundtrip(self):
        data = self.sign()
        self.assertEqual(self.verify(),0)
        self.assertEqual(json.loads((self.output/'manifest.json').read_bytes()),data)
        for path in (self.deb,self.zip):
            self.assertEqual(data['assets'][path.name],dict(size=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
        self.assertEqual(sorted(p.name for p in self.output.iterdir()),['manifest.json','manifest.sig'])

    def test_manifest_tamper(self):
        self.sign()
        path = self.output/'manifest.json'
        path.write_bytes(path.read_bytes()+b' ')
        self.assertNotEqual(self.verify(),0)

    def test_existing_output(self):
        self.output.mkdir()
        sentinel = self.output/'manifest.json'
        sentinel.write_bytes(b'keep')
        with self.assertRaises(FileExistsError): self.sign()
        self.assertEqual(sentinel.read_bytes(),b'keep')

    def test_missing_package(self):
        self.zip.unlink()
        with self.assertRaises(ValueError): self.sign()
        self.assertFalse(self.output.exists())

    def test_empty_package(self):
        self.deb.write_bytes(b'')
        with self.assertRaises(ValueError): self.sign()
        self.assertFalse(self.output.exists())

    def test_symlink(self):
        self.deb.unlink()
        self.deb.symlink_to(self.zip)
        with self.assertRaises(ValueError): self.sign()

    def test_invalid_tag(self):
        with self.assertRaises(ValueError): self.sign(tag='v2.6.0/evil')

    def test_bad_key(self):
        bad = self.rootcase/'bad.pem'
        bad.write_bytes(b'not a key')
        with self.assertRaises(subprocess.CalledProcessError): self.sign(key=bad)
        self.assertFalse(self.output.exists())


if __name__ == '__main__': unittest.main()
