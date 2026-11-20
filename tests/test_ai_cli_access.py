"""CLI access of the AI Prompt Launcher; no real CLI is started, subprocess.run is replaced."""
import ast
import json
import os
import re
import shutil
import subprocess
import tempfile
import types
import unittest
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / 'source' / 'workstation.py'
CORE = Path(__file__).resolve().parents[1] / 'source' / 'mpw_core.py'  # Qt-free core (module-level functions)
TEXT = CORE.read_text(encoding='utf-8') + '\n' + SOURCE.read_text(encoding='utf-8')
TREE = ast.parse(TEXT)
NAMES = ('ProviderError', 'find_cli', 'resolve_cli_executable', 'cli_arguments', '_cli_detail', 'cli_answer_json', 'call_cli',
         'codex_disable_mcp_overrides', 'codex_mcp_server_names', 'cli_search_paths', 'cli_environment')
CONSTANTS = ('CLI_DEFAULT_COMMANDS', 'CLI_TIMEOUT_SECONDS', '_CLI_UNSAFE_CHARS')


def load():
    nodes = [n for n in TREE.body
             if (isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name in NAMES)
             or (isinstance(n, ast.Assign) and any(getattr(t, 'id', '') in CONSTANTS for t in n.targets))]
    ns = {'json': json, 're': re, 'os': os, 'shutil': shutil, 'tempfile': tempfile, 'Path': Path,
          'subprocess': subprocess, 'sys': __import__('sys')}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(SOURCE), 'exec'), ns)
    return ns


FN = load()
ProviderError = FN['ProviderError']
ANSWER = json.dumps({'style': 'Blues Rock', 'lyrics': '[Verse 1]\nText'})


class FakeSubprocess(types.SimpleNamespace):
    """Records the call and returns a prepared CompletedProcess."""

    def __init__(self, returncode=0, stdout=ANSWER, stderr='', raise_exc=None, write_answer=None):
        super().__init__(PIPE=subprocess.PIPE, TimeoutExpired=subprocess.TimeoutExpired,
                         CREATE_NO_WINDOW=0x08000000)
        self.result = (returncode, stdout, stderr)
        self.raise_exc, self.write_answer, self.calls = raise_exc, write_answer, []

    def run(self, args, **kwargs):
        self.calls.append((args, kwargs))
        if self.raise_exc:
            raise self.raise_exc
        if self.write_answer is not None:
            Path(args[args.index('--output-last-message') + 1]).write_text(self.write_answer, encoding='utf-8')
        code, out, err = self.result
        return subprocess.CompletedProcess(args, code, out.encode('utf-8'), err.encode('utf-8'))


class FindCliFallback(unittest.TestCase):
    def test_install_folder_used_when_path_is_not_updated_yet(self):
        with tempfile.TemporaryDirectory() as home:
            # Windows: claude.exe; macOS/Linux: executable file without extension
            exe = Path(home) / '.local' / 'bin' / ('claude.exe' if os.name == 'nt' else 'claude')
            exe.parent.mkdir(parents=True)
            exe.write_bytes(b'')
            exe.chmod(0o755)
            saved = FN['shutil'], FN['Path']
            FN['shutil'] = types.SimpleNamespace(which=lambda c: None)
            FN['Path'] = type('P', (type(Path()),), {'home': staticmethod(lambda: Path(home))})
            try:
                self.assertEqual(FN['find_cli']('claude'), str(exe))
                self.assertIsNone(FN['find_cli']('gemini-gibts-nicht'))
            finally:
                FN['shutil'], FN['Path'] = saved


class CodexMcpShield(unittest.TestCase):
    def test_configured_servers_switched_off_for_mpw_runs(self):
        args = FN['cli_arguments']('ChatGPT', 'codex.cmd', '', None, ['mpw', 'suno', 'odd name'])
        self.assertEqual(args[1:7], ['exec', '--skip-git-repo-check', '--sandbox', 'read-only', '--color', 'never'])
        self.assertEqual(args[7:13], ['-c', 'mcp_servers.mpw.enabled=false', '-c', 'mcp_servers.suno.enabled=false',
                                      '-c', 'mcp_servers."odd name".enabled=false'])
        self.assertEqual(FN['cli_arguments']('ChatGPT', 'codex.cmd')[1:], ['exec', '--skip-git-repo-check', '--sandbox',
                                                                             'read-only', '--color', 'never', '-'])

    def test_server_names_read_from_codex_config(self):
        with tempfile.TemporaryDirectory() as home:
            (Path(home) / 'config.toml').write_text(
                'model = "x"\n[mcp_servers.suno]\nurl = "https://api.suno.com/mcp"\n'
                '[mcp_servers.mpw]\ncommand = "C:\\\\MPW\\\\MPW-MCP.exe"\n', encoding='utf-8')
            saved = os.environ.get('CODEX_HOME')
            os.environ['CODEX_HOME'] = home
            try:
                self.assertEqual(FN['codex_mcp_server_names'](), ['mpw', 'suno'])
                (Path(home) / 'config.toml').write_text('not = [valid', encoding='utf-8')
                self.assertEqual(FN['codex_mcp_server_names'](), [])
            finally:
                if saved is None:
                    os.environ.pop('CODEX_HOME', None)
                else:
                    os.environ['CODEX_HOME'] = saved


class AICliAccess(unittest.TestCase):
    def setUp(self):
        self.which = FN['shutil']
        FN['shutil'] = types.SimpleNamespace(which=lambda c: r'C:\Tools\\' + c + '.cmd')
        real_names = FN['codex_mcp_server_names']
        FN['codex_mcp_server_names'] = lambda: []  # independent of a Codex config on this PC
        self.addCleanup(FN.__setitem__, 'codex_mcp_server_names', real_names)

    def tearDown(self):
        FN['shutil'] = self.which
        FN['subprocess'] = subprocess

    def run_cli(self, provider='Claude', model='', **fake):
        FN['subprocess'] = proc = FakeSubprocess(**fake)
        return FN['call_cli'](provider, FN['CLI_DEFAULT_COMMANDS'][provider], model, 'Prompt äöü'), proc

    def test_claude_prompt_goes_via_stdin_in_empty_temp_folder(self):
        answer, proc = self.run_cli('Claude', 'sonnet')
        self.assertEqual(json.loads(answer)['style'], 'Blues Rock')
        args, kwargs = proc.calls[0]
        # --strict-mcp-config: the user's MCP servers (e.g. Suno) are never started by MPW.
        self.assertEqual(args[1:], ['-p', '--output-format', 'text', '--strict-mcp-config', '--model', 'sonnet'])
        self.assertEqual(kwargs['input'], 'Prompt äöü'.encode('utf-8'))
        self.assertNotIn('shell', kwargs)
        self.assertIn('mpw_cli_', kwargs['cwd'])
        self.assertFalse(Path(kwargs['cwd']).exists(), 'temporary folder must be removed')

    def test_codex_uses_read_only_sandbox_and_answer_file(self):
        answer, proc = self.run_cli('ChatGPT', stdout='progress …', write_answer=ANSWER)
        args = proc.calls[0][0]
        self.assertEqual(args[1], 'exec')
        self.assertIn('read-only', args)
        self.assertEqual(args[-1], '-')
        self.assertEqual(answer, ANSWER)

    def test_gemini_without_model_has_no_extra_arguments(self):
        _answer, proc = self.run_cli('Gemini')
        self.assertEqual(len(proc.calls[0][0]), 1)

    def test_json_is_extracted_from_surrounding_text(self):
        answer, _ = self.run_cli(stdout='Hier ist dein Prompt:\n' + ANSWER + '\nViel Spaß!')
        self.assertEqual(answer, ANSWER)

    def test_errors_have_stable_kinds(self):
        cases = [
            (dict(returncode=1, stderr='\x1b[31mnot logged in\x1b[0m'), 'cli_failed'),
            (dict(stdout='   '), 'empty'),
            (dict(raise_exc=subprocess.TimeoutExpired('claude', 300)), 'cli_timeout'),
            (dict(raise_exc=OSError('denied')), 'cli_start'),
        ]
        for fake, kind in cases:
            with self.subTest(kind=kind), self.assertRaises(ProviderError) as ctx:
                self.run_cli(**fake)
            self.assertEqual(ctx.exception.kind, kind)
        self.assertEqual(ctx.exception.code, '')

    def test_failed_detail_strips_ansi_and_keeps_exit_code(self):
        with self.assertRaises(ProviderError) as ctx:
            self.run_cli(returncode=2, stderr='\x1b[31mnot logged in\x1b[0m')
        self.assertEqual((ctx.exception.code, ctx.exception.detail), ('2', 'not logged in'))

    def test_missing_and_unsafe_commands_never_start_a_process(self):
        FN['subprocess'] = proc = FakeSubprocess()
        FN['shutil'] = types.SimpleNamespace(which=lambda c: None)
        real_find = FN['find_cli']
        FN['find_cli'] = lambda c: None  # independent of a CLI installed on this PC
        self.addCleanup(FN.__setitem__, 'find_cli', real_find)
        with self.assertRaises(ProviderError) as ctx:
            FN['call_cli']('Claude', 'claude', '', 'x')
        self.assertEqual(ctx.exception.kind, 'cli_missing')
        for command, model in [('claude & del x', ''), ('claude|x', ''), ('', ''), ('claude', 'a b')]:
            with self.subTest(command=command, model=model), self.assertRaises(ProviderError) as ctx:
                FN['call_cli']('Claude', command, model, 'x')
            self.assertEqual(ctx.exception.kind, 'cli_invalid')
        self.assertEqual(proc.calls, [])

    def test_gui_wiring_and_translations(self):
        self.assertIn("QPushButton('Prompt erstellen (CLI)')", TEXT)
        self.assertIn('self.ai_cli_generate.clicked.connect(self.generate_ai_cli)', TEXT)
        self.assertIn("form.addRow('CLI-Befehl', cli_row)", TEXT)
        for kind in ('cli_invalid', 'cli_missing', 'cli_start', 'cli_failed', 'cli_timeout'):
            self.assertEqual(TEXT.count(f"'{kind}': "), 5, kind)


if __name__ == '__main__':
    unittest.main()
