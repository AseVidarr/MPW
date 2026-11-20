import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class InstallerAcceptanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.script=(ROOT/'scripts/verify-windows-install.ps1').read_text(encoding='utf-8')
        cls.iss=(ROOT/'installer/MPW.iss').read_text(encoding='utf-8')
        cls.build=(ROOT/'scripts/build.ps1').read_text(encoding='utf-8')
    def test_requires_explicit_install_opt_in(self):
        self.assertIn('if ($RunInstall)',self.script)
        self.assertIn('if ($RunUninstall -and -not $RunInstall)',self.script)
    def test_existing_install_protected(self):
        self.assertIn('Installationsziel existiert bereits',self.script)
    def test_exitcodes_and_selftest(self):
        self.assertIn('$proc.ExitCode -ne 0',self.script)
        self.assertIn('$unproc.ExitCode -ne 0',self.script)
        self.assertIn('--self-test',self.script)
    def test_installer_does_not_declare_user_data_deletion(self):
        self.assertNotIn('[UninstallDelete]',self.iss)
        self.assertIn('PrivilegesRequired=lowest',self.iss)
    def test_version_consistency(self):
        self.assertIn('Preview52_RC1',self.iss)
        self.assertIn('Preview52_RC1',self.build)
        self.assertIn('Get-FileHash',self.script)
if __name__=='__main__': unittest.main()
