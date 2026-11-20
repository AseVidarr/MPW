"""Platform neutrality of the Qt-free core (Windows, macOS, Linux layouts simulated on any OS)."""
import atexit
from contextlib import closing
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / 'source'


def load_core():
    if 'mpw_core' not in sys.modules:
        root = tempfile.mkdtemp(prefix='mpw_platform_root_')
        atexit.register(shutil.rmtree, root, True)
        os.environ.setdefault('MPW_DATA_ROOT', root)
        sys.path.insert(0, str(SOURCE_DIR))
    import mpw_core
    return mpw_core


core = load_core()


class PortableLayouts(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)

    def make(self, *parts, marker_at=None):
        exe = self.base.joinpath(*parts)
        exe.parent.mkdir(parents=True, exist_ok=True)
        exe.write_bytes(b'')
        if marker_at is not None:
            (self.base / marker_at / core.PORTABLE_MARKER).write_text('test')
        return exe

    def test_windows_and_linux_app_folder(self):
        for name in ('MPW-Web.exe', 'MPW-Web', 'MPW-MCP'):
            with self.subTest(name=name):
                exe = self.make('Portable', 'App', name, marker_at='Portable')
                self.assertEqual(core.portable_root_for(exe), self.base / 'Portable')

    def test_macos_app_bundle_next_to_marker_and_inside_app_folder(self):
        exe = self.make('MPW', 'MPW-Web.app', 'Contents', 'MacOS', 'MPW-Web', marker_at='MPW')
        self.assertEqual(core.portable_root_for(exe), self.base / 'MPW')
        exe = self.make('P2', 'App', 'MPW-Web.app', 'Contents', 'MacOS', 'MPW-Web', marker_at='P2')
        self.assertEqual(core.portable_root_for(exe), self.base / 'P2')

    def test_no_marker_or_other_layout_is_not_portable(self):
        self.assertIsNone(core.portable_root_for(self.make('Portable', 'App', 'MPW-Web')))
        self.assertIsNone(core.portable_root_for(self.make('Programs', 'MPW', 'MPW-Web', marker_at='Programs')))

    def test_macos_app_translocation_is_refused_with_hint(self):
        exe = Path('/private/var/folders/xy/T/AppTranslocation/ABC/d/MPW/App/MPW-Web')
        with self.assertRaises(core.TranslocatedError) as ctx:
            core.portable_root_for(exe)
        self.assertIn('xattr -dr com.apple.quarantine', str(ctx.exception))


class CliSearch(unittest.TestCase):
    def test_windows_locations(self):
        paths = core.cli_search_paths('claude', system='win32', home='C:/Users/U', env={'APPDATA': 'C:/AppData'})
        self.assertEqual([p.as_posix() for p in paths], ['C:/Users/U/.local/bin/claude.exe', 'C:/AppData/npm/claude.cmd'])

    def test_macos_and_linux_locations(self):
        with tempfile.TemporaryDirectory() as home:
            for version in ('v20.1.0', 'v22.3.0'):
                (Path(home) / '.nvm' / 'versions' / 'node' / version / 'bin').mkdir(parents=True)
            for system in ('darwin', 'linux'):
                paths = [p.as_posix() for p in core.cli_search_paths('gemini', system=system, home=home,
                                                                     env={'NPM_CONFIG_PREFIX': '/opt/npm'})]
                h = Path(home).as_posix()
                self.assertEqual(paths[0], '/opt/npm/bin/gemini')
                for expected in (f'{h}/.local/bin/gemini', '/opt/homebrew/bin/gemini', '/usr/local/bin/gemini',
                                 f'{h}/.npm-global/bin/gemini'):
                    self.assertIn(expected, paths)
                nvm = [p for p in paths if '/.nvm/' in p]
                self.assertEqual(nvm, [f'{h}/.nvm/versions/node/v22.3.0/bin/gemini',
                                       f'{h}/.nvm/versions/node/v20.1.0/bin/gemini'])  # newest first
                self.assertFalse(any(p.endswith(('.exe', '.cmd')) for p in paths))

    def test_cli_folder_first_in_path_for_node_scripts(self):
        folder = str(Path('/opt/x/bin'))
        env = core.cli_environment(str(Path(folder) / 'gemini'), base={'PATH': os.pathsep.join(['/usr/bin', '/bin'])})
        self.assertEqual(env['PATH'].split(os.pathsep)[0], folder)
        self.assertEqual(env['NO_COLOR'], '1')
        again = core.cli_environment(str(Path(folder) / 'codex'), base=env)
        self.assertEqual(again['PATH'].split(os.pathsep).count(folder), 1)

    def test_program_names(self):
        self.assertEqual(core.program_name('MPW-MCP'), 'MPW-MCP.exe' if os.name == 'nt' else 'MPW-MCP')


class StartScripts(unittest.TestCase):
    def test_unix_scripts_use_lf_and_check_marker(self):
        for name in ('Start-MPW-Web.command', 'start-mpw-web.sh'):
            raw = (ROOT / 'scripts' / name).read_bytes()
            with self.subTest(name=name):
                self.assertNotIn(b'\r\n', raw, 'Windows line endings break the script on macOS/Linux')
                self.assertTrue(raw.startswith(b'#!/bin/sh\n'))
                self.assertIn(b'.mpw-portable-v2', raw)
                self.assertIn(b'./App/MPW-Web', raw)
                self.assertIsNone(__import__('re').search(rb'(^|[;&|]\s*|\s)rm\s', raw))  # never deletes anything

    def test_readme_for_macos_linux(self):
        text = (ROOT / 'scripts' / 'LIESMICH_MAC_LINUX.txt').read_text(encoding='utf-8')
        for needle in ('xattr -dr com.apple.quarantine', 'chmod +x', '"Data"'):
            self.assertIn(needle, text)


class WebCreatesDatabase(unittest.TestCase):
    """On macOS/Linux the browser GUI is the only MPW program: it must prepare the database."""

    def test_main_initialises_missing_database_like_the_desktop(self):
        import mpw_web
        with tempfile.TemporaryDirectory() as folder:
            saved = core.ROOT, core.DB, mpw_web.MPWWebServer
            core.ROOT, core.DB = Path(folder), Path(folder) / 'workstation.db'

            started = []

            class FakeServer:
                url = 'http://127.0.0.1:1/#t=x'

                def __init__(self, db, port=0):
                    self.db = db

                def start_auto_backup(self):  # due automatic backups also without the desktop app
                    started.append(True)

                def serve_forever(self):
                    raise KeyboardInterrupt

                def server_close(self):
                    pass
            mpw_web.MPWWebServer = FakeServer
            try:
                self.assertEqual(mpw_web.main(['--no-browser']), 0)
                self.assertEqual(started, [True])
                self.assertTrue(core.DB.is_file())
                with closing(__import__('sqlite3').connect(core.DB)) as con:
                    tables = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
                self.assertTrue({'bands', 'songs', 'prompt_versions'} <= tables)
            finally:
                core.ROOT, core.DB, mpw_web.MPWWebServer = saved


if __name__ == '__main__':
    unittest.main()
