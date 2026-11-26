import importlib.machinery
import importlib.util
from pathlib import Path
import unittest

loader = importlib.machinery.SourceFileLoader('updater', str(Path(__file__).with_name('ivivid-update')))
spec = importlib.util.spec_from_loader(loader.name, loader)
u = importlib.util.module_from_spec(spec)
loader.exec_module(u)


def release(v, **changes):
    tag = 'v' + v
    names = [f'ivivid_{v}_amd64.deb', f'ivivid-{v}-linux-amd64.zip', 'manifest.json', 'manifest.sig', 'SHA256SUMS']
    value = dict(tag_name=tag, draft=False, prerelease='-beta.' in v, assets=[dict(name=n, browser_download_url=u.BASE+'download/'+tag+'/'+n, state='uploaded') for n in names])
    value.update(changes)
    return value


class UpdateTests(unittest.TestCase):
    def test_numeric_beta_order(self):
        self.assertGreater(u.version('2.6.0-beta.10'), u.version('2.6.0-beta.2'))
        self.assertGreater(u.version('2.6.0'), u.version('2.6.0-beta.99'))

    def test_latest_and_channels(self):
        rows = [release('2.6.0-beta.2'), release('2.5.0'), release('2.6.0-beta.10')]
        self.assertEqual(u.select_release(rows, '2.4.0', 'beta', 'deb'), '2.6.0-beta.10')
        self.assertEqual(u.select_release(rows, '2.4.0', 'stable', 'zip'), '2.5.0')

    def test_no_downgrade(self):
        self.assertIsNone(u.select_release([release('2.5.0')], '2.6.0-beta.1', 'stable', 'deb'))

    def test_draft_and_inconsistent_flags(self):
        rows = [release('3.0.0', draft=True), release('4.0.0-beta.1', prerelease=False)]
        self.assertIsNone(u.select_release(rows, '2.4.0', 'beta', 'deb'))

    def test_missing_package_or_checksum(self):
        row = release('2.6.0')
        row['assets'].pop()
        self.assertIsNone(u.select_release([row], '2.4.0', 'stable', 'deb'))
        row = release('2.6.0')
        row['assets'].pop(0)
        self.assertIsNone(u.select_release([row], '2.4.0', 'stable', 'deb'))
        self.assertEqual(u.select_release([row], '2.4.0', 'stable', 'zip'), '2.6.0')

    def test_untrusted_url_and_duplicate_asset(self):
        row = release('2.6.0')
        row['assets'][0]['browser_download_url'] = 'https://example.org/evil.deb'
        self.assertIsNone(u.select_release([row], '2.4.0', 'stable', 'deb'))
        row = release('2.6.0')
        row['assets'].append(row['assets'][0].copy())
        self.assertIsNone(u.select_release([row], '2.4.0', 'stable', 'deb'))

    def test_malformed_version_and_response(self):
        for value in ('2.6.0-rc.1', '02.6.0', '2.6.0/../../bad', None):
            with self.assertRaises(ValueError):
                u.version(value)
        with self.assertRaises(ValueError):
            u.select_release({}, '2.4.0', 'stable', 'deb')

    def test_signed_metadata_required(self):
        for missing in ('manifest.json', 'manifest.sig'):
            row = release('2.7.0')
            row['assets'] = [a for a in row['assets'] if a['name'] != missing]
            self.assertEqual(u.select_release([row, release('2.6.0')], '2.5.0', 'stable', 'deb'), '2.6.0')

    def test_signed_metadata_url_and_state(self):
        for field, value in [('browser_download_url', 'https://example.org/manifest.sig'), ('state', 'new')]:
            row = release('2.6.0')
            next(a for a in row['assets'] if a['name'] == 'manifest.sig')[field] = value
            self.assertIsNone(u.select_release([row], '2.5.0', 'stable', 'zip'))


if __name__ == '__main__':
    unittest.main()
