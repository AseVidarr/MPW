"""Preview 41: static build/installer safety contracts (no Windows runtime required)."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILD = (ROOT / 'scripts/build.ps1').read_text(encoding='utf-8-sig')
ISS = (ROOT / 'installer/MPW.iss').read_text(encoding='utf-8')
LAUNCH = (ROOT / 'scripts/Launch-Portable.ps1').read_text(encoding='utf-8-sig')

class ReleasePreflightTests(unittest.TestCase):
    def test_version_and_output_names_consistent(self):
        self.assertIn('#define AppVersion "2.2.0"', ISS)
        self.assertRegex(ISS, r'MPW_Setup_v2\.2\.0_Alpha21_Preview52_RC1')
        self.assertRegex(BUILD, r'MPW_Portable_v2\.2\.0_Alpha21_Preview52_RC1')
        self.assertNotIn('MPW_Setup_v2.1.0', ISS)
        self.assertNotIn('MPW_Portable_v2.1.0', BUILD)

    def test_selftests_before_and_after_build(self):
        self.assertIn("'workstation.py') --self-test", BUILD)
        self.assertIn('& $exe --self-test', BUILD)
        self.assertIn('function Assert-LastExit', BUILD)
        self.assertIn('Get-FileHash', BUILD)

    def test_installer_is_app_only_and_per_user(self):
        self.assertIn('PrivilegesRequired=lowest', ISS)
        self.assertIn('CloseApplications=yes', ISS)
        self.assertIn('dist\\MPW\\*', ISS)
        self.assertNotRegex(ISS, r'(?im)^Source:.*(?:workstation\.db|\\Data\\|\\media\\)')
        self.assertIn('RestartApplications=no', ISS)

    def test_portable_data_not_deleted_by_build(self):
        self.assertIn('Portable-Ziel existiert bereits', BUILD)
        self.assertIn('keine automatische Loeschung', BUILD)
        self.assertIn('Data', LAUNCH)
        self.assertNotRegex(BUILD, r'(?im)^\s*Remove-Item\b')

    def test_dependencies_and_build_inputs_present(self):
        for path in ['source/workstation.py','source/requirements.txt','scripts/Start-MPW-Portable.cmd','scripts/Launch-Portable.ps1','installer/MPW.iss']:
            self.assertTrue((ROOT/path).is_file(), path)
        requirements=(ROOT/'source/requirements.txt').read_text(encoding='utf-8')
        self.assertIn('PySide6', requirements)
        self.assertIn('mutagen', requirements)

if __name__ == '__main__':
    unittest.main()
