import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
BUILD = (ROOT / 'scripts' / 'build.ps1').read_text(encoding='utf-8')

class PortableZipPathTests(unittest.TestCase):
    def test_both_zip_entry_checks_normalize_windows_separators(self):
        checks = [line for line in BUILD.splitlines() if 'zipReader.Entries | Where-Object' in line]
        self.assertEqual(len(checks), 2)
        for check in checks:
            self.assertIn("$_.FullName -replace '\\\\', '/'", check)

    def test_windows_and_unix_zip_entry_names_match(self):
        expected = [r'(^|/)App/MPW\.exe$', r'(^|/)Start-MPW-Portable\.cmd$']
        for name in ('App/MPW.exe', r'App\MPW.exe'):
            self.assertRegex(name.replace('\\', '/'), expected[0])
        for name in ('Start-MPW-Portable.cmd', r'folder\Start-MPW-Portable.cmd'):
            self.assertRegex(name.replace('\\', '/'), expected[1])

if __name__ == '__main__':
    unittest.main()
