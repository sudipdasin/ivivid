#!/usr/bin/env python3
"""Real Git and data-only DEB/ZIP fixtures; not native iVivid compilation."""
import os, pathlib, shutil, subprocess, tempfile, unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
FIXTURE=r'''#!/usr/bin/env bash
set -euo pipefail
out=$1; mkdir "$out"; tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT
mkdir -p "$tmp/pkg/DEBIAN" "$tmp/pkg/usr/share/ivivid"
printf 'fixture only\n' > "$tmp/pkg/usr/share/ivivid/fixture"
cat > "$tmp/pkg/DEBIAN/control" <<CONTROL
Package: ${FIXTURE_PACKAGE:-ivivid}
Version: 2.6.0~beta.1
Architecture: amd64
Maintainer: Fixture <fixture@example.invalid>
Description: Data-only test fixture
CONTROL
deb=ivivid_2.6.0-beta.1_amd64.deb; portable=ivivid-2.6.0-beta.1-linux-amd64.zip
dpkg-deb --build --root-owner-group "$tmp/pkg" "$out/$deb"
(cd "$tmp"; zip -q "$out/$portable" pkg/usr/share/ivivid/fixture)
(cd "$out"; sha256sum -- "$deb" "$portable" > SHA256SUMS)
printf '%s\n' "${FIXTURE_PIN:-$(git rev-parse HEAD)}" > "$out/SOURCE_COMMIT"
case ${FIXTURE_MODE:-ok} in
 missing) rm "$out/$portable";;
 tamper) printf 'tampered' >> "$out/$deb";;
 symlink) mv "$out/$portable" "$out/other.zip"; ln -s other.zip "$out/$portable";;
 manifest) printf 'unexpected\n' >> "$out/SHA256SUMS";;
 fail) exit 17;;
esac
'''
class Tests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.repo=pathlib.Path(self.temp.name)
  (self.repo/'packaging').mkdir();shutil.copy(ROOT/'packaging/appveyor-preview.sh',self.repo/'packaging/appveyor-preview.sh');(self.repo/'packaging/build-release.sh').write_text(FIXTURE)
  self.git('init','-q');self.git('config','user.email','fixture@example.invalid');self.git('config','user.name','Fixture');self.git('add','.');self.git('commit','-qm','fixture')
  self.pin=self.git('rev-parse','HEAD').strip();self.env=dict(os.environ,APPVEYOR='True',APPVEYOR_REPO_NAME='sudipdasin/ivivid',APPVEYOR_REPO_BRANCH='build/appveyor-2.6-preview',APPVEYOR_REPO_COMMIT=self.pin,APPVEYOR_REPO_TAG='false',APPVEYOR_PULL_REQUEST_NUMBER='')
 def git(self,*a):return subprocess.check_output(['git',*a],cwd=self.repo,text=True)
 def run_builder(self,**overrides):return subprocess.run(['bash','packaging/appveyor-preview.sh','build'],cwd=self.repo,env=dict(self.env,**overrides),capture_output=True,text=True,timeout=30)
 def reject(self,**overrides):
  r=self.run_builder(**overrides);self.assertNotEqual(r.returncode,0,r.stdout+r.stderr);self.assertFalse((self.repo/'ivivid-ci-artifacts').exists())
 def test_valid(self):
  r=self.run_builder();self.assertEqual(r.returncode,0,r.stdout+r.stderr);self.assertEqual(len(list((self.repo/'ivivid-ci-artifacts').iterdir())),5)
 def test_wrong_repo(self):self.reject(APPVEYOR_REPO_NAME='other/repo')
 def test_wrong_branch(self):self.reject(APPVEYOR_REPO_BRANCH='main')
 def test_wrong_pin(self):self.reject(APPVEYOR_REPO_COMMIT='0'*40)
 def test_pr(self):self.reject(APPVEYOR_PULL_REQUEST_NUMBER='1')
 def test_tag(self):self.reject(APPVEYOR_REPO_TAG='true')
 def test_dirty(self):(self.repo/'untracked').write_text('x');self.reject()
 def test_wrong_artifact_pin(self):self.reject(FIXTURE_PIN='0'*40)
 def test_missing_artifact(self):self.reject(FIXTURE_MODE='missing')
 def test_tamper(self):self.reject(FIXTURE_MODE='tamper')
 def test_symlink(self):self.reject(FIXTURE_MODE='symlink')
 def test_manifest(self):self.reject(FIXTURE_MODE='manifest')
 def test_builder_failure(self):self.reject(FIXTURE_MODE='fail')
 def test_wrong_package(self):self.reject(FIXTURE_PACKAGE='wrong-package')
if __name__=='__main__':unittest.main(verbosity=2)
