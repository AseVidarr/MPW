import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]

class ReleaseCandidateChecks(unittest.TestCase):
    def test_rc_build_identifiers(self):
        build = (ROOT / 'scripts/build.ps1').read_text(encoding='utf-8')
        iss = (ROOT / 'installer/MPW.iss').read_text(encoding='utf-8')
        self.assertIn('MPW_Portable_v2.2.0_Alpha21_Preview52_RC1', build)
        self.assertIn('MPW_Setup_v2.2.0_Alpha21_Preview52_RC1', iss)
    def test_release_audit_is_read_only(self):
        script = (ROOT / 'scripts/verify-release-candidate.ps1').read_text(encoding='utf-8')
        self.assertIn('OpenRead($zip)', script)
        self.assertIn('PortableSHA256', script)
        self.assertIn('manual_check_required', script)
        self.assertNotIn('Remove-Item', script)
        self.assertNotIn('Start-Process', script)
    def test_portable_build_refuses_overwrite(self):
        build = (ROOT / 'scripts/build.ps1').read_text(encoding='utf-8')
        self.assertIn('Portable-Ziel existiert bereits', build)
        self.assertIn('Portable-ZIP existiert bereits', build)

if __name__ == '__main__': unittest.main()
