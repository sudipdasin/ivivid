import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from release_auth import verify_package


class AuthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temp.name)
        for n in ('trusted', 'other'):
            subprocess.run(['openssl', 'genpkey', '-algorithm', 'RSA', '-pkeyopt', 'rsa_keygen_bits:2048', '-out', str(cls.root/(n+'.private'))], check=True, capture_output=True)
            subprocess.run(['openssl', 'pkey', '-in', str(cls.root/(n+'.private')), '-pubout', '-out', str(cls.root/(n+'.pem'))], check=True, capture_output=True)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def setUp(self):
        self.package = self.root/'ivivid_2.6.0-beta.1_amd64.deb'
        self.payload = b'synthetic package fixture'
        self.package.write_bytes(self.payload)
        self.manifest = self.root/'manifest.json'
        self.signature = self.root/'manifest.sig'
        self.data = dict(schema=1, repository='sudipdasin/ivivid', tag='v2.6.0-beta.1', architecture='amd64', assets={self.package.name: dict(size=len(self.payload), sha256=hashlib.sha256(self.payload).hexdigest())})
        self.sign()

    def sign(self, raw=None):
        self.manifest.write_bytes(json.dumps(self.data).encode() if raw is None else raw)
        subprocess.run(['openssl', 'dgst', '-sha256', '-sign', str(self.root/'trusted.private'), '-out', str(self.signature), str(self.manifest)], check=True, capture_output=True)

    def verify(self, key='trusted', tag='v2.6.0-beta.1', fmt='deb'):
        return verify_package(self.manifest, self.signature, self.root/(key+'.pem'), self.package, tag, fmt)

    def test_valid(self):
        self.assertEqual(self.verify(), hashlib.sha256(self.payload).hexdigest())

    def test_wrong_key(self):
        with self.assertRaises(ValueError): self.verify(key='other')

    def test_manifest_tamper(self):
        self.manifest.write_bytes(self.manifest.read_bytes()+b' ')
        with self.assertRaises(ValueError): self.verify()

    def test_package_tamper(self):
        self.package.write_bytes(b'x'*len(self.payload))
        with self.assertRaises(ValueError): self.verify()

    def test_truncated_package(self):
        self.package.write_bytes(self.payload[:-1])
        with self.assertRaises(ValueError): self.verify()

    def test_wrong_release(self):
        with self.assertRaises(ValueError): self.verify(tag='v2.7.0')

    def test_wrong_architecture(self):
        self.data['architecture'] = 'arm64'
        self.sign()
        with self.assertRaises(ValueError): self.verify()

    def test_wrong_format(self):
        with self.assertRaises(ValueError): self.verify(fmt='zip')

    def test_duplicate_key(self):
        self.sign(b'{"schema":1,"schema":1}')
        with self.assertRaises(ValueError): self.verify()

    def test_invalid_size(self):
        self.data['assets'][self.package.name]['size'] = True
        self.sign()
        with self.assertRaises(ValueError): self.verify()

    def test_symlink(self):
        target = self.root/'target'
        target.write_bytes(self.payload)
        self.package.unlink()
        self.package.symlink_to(target)
        try:
            with self.assertRaises(ValueError): self.verify()
        finally:
            self.package.unlink()


if __name__ == '__main__': unittest.main()
