import hashlib
import unittest
from test_release_sign import SigningTests
from release_auth import verify_package


class SignedRoundTrip(SigningTests):
    def check_package(self, path, fmt, tag='v2.6.0-beta.1'):
        return verify_package(self.output/'manifest.json', self.output/'manifest.sig', self.public, path, tag, fmt)

    def test_both_packages(self):
        self.sign()
        for path, fmt in ((self.deb, 'deb'), (self.zip, 'zip')):
            self.assertEqual(self.check_package(path, fmt), hashlib.sha256(path.read_bytes()).hexdigest())

    def test_payload_mutation(self):
        self.sign()
        self.zip.write_bytes(b'zip attack!')
        with self.assertRaises(ValueError): self.check_package(self.zip, 'zip')

    def test_wrong_version(self):
        self.sign()
        with self.assertRaises(ValueError): self.check_package(self.deb, 'deb', 'v2.7.0')

    def test_wrong_package(self):
        self.sign()
        with self.assertRaises(ValueError): self.check_package(self.zip, 'deb')


if __name__ == '__main__':
    unittest.main(defaultTest='SignedRoundTrip')
