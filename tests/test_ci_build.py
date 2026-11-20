"""GitHub Actions workflow and macOS/Linux build files (structure checks; no YAML library needed)."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / '.github' / 'workflows' / 'build.yml'


class Workflow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = WORKFLOW.read_bytes()
        cls.text = cls.raw.decode('utf-8')

    def test_plain_yaml_layout(self):
        self.assertNotIn(b'\t', self.raw, 'YAML must not contain tabs')
        self.assertNotIn(b'\r\n', self.raw)
        for number, line in enumerate(self.text.splitlines(), 1):
            indent = len(line) - len(line.lstrip(' '))
            self.assertEqual(indent % 2, 0, f'line {number}: odd indentation')

    def test_jobs_cover_all_three_systems_and_four_scenarios(self):
        for job in ('\n  test:', '\n  windows:', '\n  unix:', '\n  release:'):
            self.assertIn(job, self.text)
        self.assertIn('os: [windows-latest, macos-latest, ubuntu-latest]', self.text)
        self.assertIn('run: ./build.ps1', self.text)                 # Windows setup + portable
        self.assertIn('run: sh scripts/build-unix.sh', self.text)    # macOS + Linux portable
        self.assertIn('label: macOS', self.text)
        self.assertIn('label: Linux', self.text)

    def test_current_action_majors(self):
        uses = set(re.findall(r'uses: (\S+)', self.text))
        self.assertEqual(uses, {'actions/checkout@v7', 'actions/setup-python@v7', 'actions/upload-artifact@v7',
                                'actions/download-artifact@v8', 'softprops/action-gh-release@v3'})

    def test_safe_defaults(self):
        self.assertIn('permissions:\n  contents: read', self.text)          # read-only by default
        self.assertIn('draft: true', self.text)                              # release is never published automatically
        self.assertIn("if: startsWith(github.ref, 'refs/tags/v')", self.text)
        self.assertIn('MPW_DATA_ROOT: ${{ runner.temp }}/mpw-selftest', self.text)
        self.assertNotIn('secrets.', self.text)                              # no keys needed or exposed

    def test_tests_include_scripts_without_testcase(self):
        self.assertIn("grep -q 'unittest.TestCase'", self.text)
        self.assertIn('python -m unittest discover -s tests -p "test_*.py"', self.text)


class UnixBuildFiles(unittest.TestCase):
    def test_build_script(self):
        raw = (ROOT / 'scripts' / 'build-unix.sh').read_bytes()
        text = raw.decode('utf-8')
        self.assertNotIn(b'\r\n', raw)
        self.assertTrue(text.startswith('#!/bin/sh\n'))
        self.assertIn('set -eu', text)
        self.assertIsNone(re.search(r'(^|[;&|]\s*|\s)rm\s', text))            # never deletes anything
        self.assertIn('Ziel existiert bereits', text)
        for needed in ('installer/MPW-Web.spec', 'Start-MPW-Web.command', 'start-mpw-web.sh',
                       'LIESMICH_MAC_LINUX.txt', '.mpw-portable-v2', '--self-test', 'tar -C'):
            self.assertIn(needed, text)
        for path in ('installer/MPW-Web.spec', 'scripts/Start-MPW-Web.command', 'scripts/start-mpw-web.sh',
                     'scripts/LIESMICH_MAC_LINUX.txt', 'source/mpw_web.py', 'source/mpw_mcp_server.py'):
            self.assertTrue((ROOT / path).is_file(), path)

    def test_web_spec_without_qt(self):
        spec = (ROOT / 'installer' / 'MPW-Web.spec').read_text(encoding='utf-8')
        self.assertIn("NO_QT = ['PySide6', 'shiboken6']", spec)
        self.assertEqual(spec.count('excludes=NO_QT'), 2)
        self.assertIn("name='MPW-Web'", spec)
        self.assertIn("name='MPW-MCP'", spec)
        self.assertIn("name='App'", spec)
        self.assertIn("(os.path.join(SRC, 'web'), 'web')", spec)

    def test_git_files_protect_user_data_and_line_endings(self):
        ignore = (ROOT / '.gitignore').read_text(encoding='utf-8').splitlines()
        for entry in ('Data/', '*.db', 'dist/', 'build/', 'app_configuration.json'):
            self.assertIn(entry, ignore)
        attributes = (ROOT / '.gitattributes').read_text(encoding='utf-8')
        for line in ('*.sh       text eol=lf', '*.command  text eol=lf', '*.ps1      text eol=crlf'):
            self.assertIn(line, attributes)


if __name__ == '__main__':
    unittest.main()
