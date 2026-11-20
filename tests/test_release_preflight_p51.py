import subprocess,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class ReleasePreflightP51(unittest.TestCase):
    def test_preflight_passes(self):
        result=subprocess.run([sys.executable,str(ROOT/'scripts/release-preflight.py')],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
    def test_build_names_are_current(self):
        b=(ROOT/'scripts/build.ps1').read_text(encoding='utf-8')
        self.assertNotIn('Preview47',b)
        self.assertIn('MPW_Portable_v2.2.0_Alpha21_Preview52_RC1',b)
    def test_installer_name_is_current(self):
        s=(ROOT/'installer/MPW.iss').read_text(encoding='utf-8')
        self.assertIn('MPW_Setup_v2.2.0_Alpha21_Preview52_RC1',s)

if __name__ == '__main__':
    unittest.main()
