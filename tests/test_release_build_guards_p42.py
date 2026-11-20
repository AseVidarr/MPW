"""Preview 42: static release pipeline guardrails; not a Windows execution test."""
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BUILD=(ROOT/'scripts/build.ps1').read_text(encoding='utf-8-sig')
ISS=(ROOT/'installer/MPW.iss').read_text(encoding='utf-8')
class ReleaseBuildGuards(unittest.TestCase):
    def test_version(self):
        self.assertRegex(BUILD, r'Preview52_RC1')
        self.assertRegex(ISS, r'MPW_Setup_v2\.2\.0_Alpha21_Preview52_RC1')
    def test_dependencies_and_python(self):
        self.assertIn('sys.version_info >= (3,10)', BUILD)
        self.assertIn('import PyInstaller, PySide6, mutagen', BUILD)
        self.assertIn("Assert-LastExit 'Build-Abhaengigkeiten'", BUILD)
    def test_executable_checks(self):
        self.assertIn("Assert-NonEmptyFile $exe 'MPW.exe'", BUILD)
        self.assertIn("Assert-LastExit 'EXE-Selbsttest'", BUILD)
        self.assertIn("Assert-NonEmptyFile (Join-Path $portable 'App/MPW.exe')", BUILD)
    def test_zip_validation(self):
        self.assertIn('ZipFile]::OpenRead', BUILD)
        self.assertIn('Portable-ZIP enthaelt keine App/MPW.exe', BUILD)
        self.assertIn('Portable-ZIP enthaelt keinen Start-Launcher', BUILD)
    def test_installer_and_checksum(self):
        self.assertIn("'Installer-EXE'", BUILD)
        self.assertIn("Assert-NonEmptyFile $checksumPath 'SHA256SUMS.txt'", BUILD)
        self.assertNotIn('Remove-Item', BUILD)
if __name__=='__main__': unittest.main()
