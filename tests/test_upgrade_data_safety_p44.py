import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class UpgradeSafetyP44(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s=(ROOT/'scripts/verify-upgrade-data.ps1').read_text(encoding='utf-8')
        cls.iss=(ROOT/'installer/MPW.iss').read_text(encoding='utf-8')
        cls.app=(ROOT/'source/workstation.py').read_text(encoding='utf-8')+(ROOT/'source/mpw_core.py').read_text(encoding='utf-8')
    def test_manifest_requires_explicit_data_paths(self):
        self.assertIn('[string[]]$DataPaths',self.s)
        self.assertIn('Datenpfad fehlt',self.s)
    def test_hash_and_size_comparison(self):
        self.assertIn('Get-FileHash',self.s)
        self.assertIn('SHA256',self.s)
        self.assertIn('Length',self.s)
        self.assertIn('$Verify',self.s)
    def test_no_mutating_data_operations(self):
        for token in ('Remove-Item','Copy-Item','Move-Item','Start-Process','sqlite3'):
            self.assertNotIn(token,self.s)
        self.assertIn('Manifest existiert bereits',self.s)
    def test_no_install_uninstall_data_deletion(self):
        self.assertNotIn('[UninstallDelete]',self.iss)
        self.assertNotIn('[InstallDelete]',self.iss)
    def test_version_and_manifest_guard(self):
        self.assertIn("APP_VERSION = '2.2.0 RC2'",self.app)
        self.assertIn('v2.2.0_RC2',self.iss)
        self.assertIn('Manifest darf nicht im Datenbestand liegen',self.s)
if __name__=='__main__': unittest.main()
