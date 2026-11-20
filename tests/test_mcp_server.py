"""MPW MCP server: protocol, read-only guarantee and the opt-in write tool. Uses temporary data only."""
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'source'
_SANDBOX = tempfile.TemporaryDirectory(prefix='mpw_mcp_unittest_')
# Must be set before workstation is imported: its data root is resolved at import time.
os.environ['MPW_DATA_ROOT'] = str(Path(_SANDBOX.name) / 'unused_root')
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
sys.path.insert(0, str(SOURCE))
import mpw_mcp_server as mcp  # noqa: E402
import mpw_core as ws  # noqa: E402  (Qt-free core)


def tearDownModule():
    _SANDBOX.cleanup()


def make_db(folder):
    root = Path(folder) / 'data'
    with closing(ws.init_database(root)) as con:
        con.execute("INSERT INTO bands(name,genre,second_genre,persona) VALUES('Iron Delta','Blues','Folk Metal','Keep Current')")
        con.execute("INSERT INTO projects(band_id,name) VALUES(1,'Rain Song')")
        con.execute("INSERT INTO projects(band_id,name) VALUES(1,'Ohne Song')")
        con.execute("INSERT INTO songs(project_id,title,style,lyrics) VALUES(1,'Rain Song','Delta Blues','[Verse 1]\nRegen')")
        con.execute("INSERT INTO instruments(band_id,category,details) VALUES(1,'Gitarre','Resonator')")
        con.execute("INSERT INTO hardware_presets(name,items_json) VALUES('Studio A', ?)", (json.dumps([['Mikrofon', 'SM7B']]),))
        con.execute("INSERT INTO prompt_versions(song_id,provider,model,style,lyrics,brief) VALUES(1,'Claude','x','S1','L1','Idee 1')")
        con.execute("INSERT INTO song_infos(song_id,html) VALUES(1,'<p>Tempo <b>72</b> BPM</p>')")
        con.commit()
    return root / 'workstation.db'


def request(server, method, params=None, msg_id=1):
    message = {'jsonrpc': '2.0', 'id': msg_id, 'method': method}
    if params is not None:
        message['params'] = params
    return server.handle(message)


def call(server, name, **args):
    result = request(server, 'tools/call', {'name': name, 'arguments': args})['result']
    text = result['content'][0]['text']
    return result['isError'], (text if result['isError'] else json.loads(text))


class McpProtocol(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='mpw_mcp_case_')
        self.db = make_db(self.tmp.name)
        self.server = mcp.MPWServer(db=self.db)

    def tearDown(self):
        self.tmp.cleanup()

    def test_initialize_negotiates_version_and_reports_tools_capability(self):
        reply = request(self.server, 'initialize', {'protocolVersion': '2025-06-18', 'capabilities': {},
                                                    'clientInfo': {'name': 'claude-code', 'version': '1'}})['result']
        self.assertEqual(reply['protocolVersion'], '2025-06-18')
        self.assertIn('tools', reply['capabilities'])
        self.assertEqual(reply['serverInfo']['name'], 'mpw')
        self.assertEqual(self.server.client, 'claude-code')
        future = request(self.server, 'initialize', {'protocolVersion': '2099-01-01'})['result']
        self.assertEqual(future['protocolVersion'], mcp.SUPPORTED_PROTOCOLS[0])

    def test_notifications_get_no_reply_and_unknown_methods_error(self):
        self.assertIsNone(self.server.handle({'jsonrpc': '2.0', 'method': 'notifications/initialized'}))
        self.assertEqual(request(self.server, 'nope')['error']['code'], -32601)
        self.assertEqual(self.server.handle_line('{kaputt')['error']['code'], -32700)
        self.assertEqual(request(self.server, 'ping')['result'], {})
        self.assertEqual(request(self.server, 'tools/call', {'name': 'gibtsnicht'})['error']['code'], -32602)

    def test_read_only_server_lists_no_write_tool(self):
        tools = request(self.server, 'tools/list')['result']['tools']
        names = {t['name'] for t in tools}
        self.assertEqual(names, set(mcp.READ_TOOLS))
        self.assertNotIn('save_prompt_version', names)
        for tool in tools:
            self.assertTrue(tool['annotations']['readOnlyHint'], tool['name'])
            self.assertEqual(tool['inputSchema']['type'], 'object')

    def test_read_tools_return_mpw_data(self):
        err, bands = call(self.server, 'list_bands')
        self.assertFalse(err)
        self.assertEqual((bands[0]['name'], bands[0]['projects'], bands[0]['songs']), ('Iron Delta', 2, 1))
        err, band = call(self.server, 'get_band', band_name='iron delta')
        self.assertEqual(band['instruments'], [{'category': 'Gitarre', 'details': 'Resonator'}])
        self.assertEqual(len(band['projects']), 2)
        err, songs = call(self.server, 'list_songs', query='rain')
        self.assertEqual((songs[0]['title'], songs[0]['prompt_versions']), ('Rain Song', 1))
        err, song = call(self.server, 'get_song', song_id=1)
        self.assertEqual((song['style'], song['notes']), ('Delta Blues', 'Tempo 72 BPM'))
        err, versions = call(self.server, 'list_prompt_versions', song_id=1)
        self.assertNotIn('style', versions[0])
        err, version = call(self.server, 'get_prompt_version', version_id=versions[0]['id'])
        self.assertEqual((version['style'], version['lyrics']), ('S1', 'L1'))
        err, presets = call(self.server, 'list_hardware_presets')
        self.assertEqual(presets[0]['items'], [{'category': 'Mikrofon', 'details': 'SM7B'}])
        err, genres = call(self.server, 'search_genres', query='blues', limit=5)
        self.assertFalse(err)
        self.assertTrue(genres)

    def test_briefing_matches_launcher_request(self):
        err, data = call(self.server, 'get_suno_briefing', song_id=1, song_idea='Regen im Delta', hardware_preset_id=1)
        self.assertFalse(err)
        with closing(sqlite3.connect(self.db)) as con:
            expected = ws.suno_prompt_request(con, 1, 1, 'Regen im Delta')
        self.assertEqual(data['briefing'], expected)
        self.assertIn('Hardware-Preset: Studio A', expected)
        self.assertIn('Mikrofon: SM7B', expected)

    def test_invalid_arguments_are_tool_errors(self):
        for name, args in [('get_song', {}), ('get_song', {'song_id': 'abc'}), ('get_song', {'song_id': 999}),
                           ('get_band', {}), ('list_bands', {'x': 1})]:
            with self.subTest(name=name, args=args):
                err, text = call(self.server, name, **args)
                self.assertTrue(err)
                self.assertIsInstance(text, str)

    def test_reading_never_changes_or_creates_database(self):
        before = self.db.read_bytes()
        for name, args in [('list_bands', {}), ('get_song', {'song_id': 1}), ('get_suno_briefing', {'song_id': 1})]:
            call(self.server, name, **args)
        self.assertEqual(self.db.read_bytes(), before)
        missing = Path(self.tmp.name) / 'leer' / 'workstation.db'
        err, text = call(mcp.MPWServer(db=missing), 'list_bands')
        self.assertTrue(err)
        self.assertIn('nicht gefunden', text)
        self.assertFalse(missing.exists())
        self.assertFalse(missing.parent.exists())

    def test_read_connection_is_really_read_only(self):
        with closing(mcp.open_read(self.db)) as con:
            with self.assertRaises(sqlite3.OperationalError):
                con.execute("DELETE FROM bands")


class McpWriteTool(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='mpw_mcp_write_')
        self.db = make_db(self.tmp.name)
        bands = Path(self.tmp.name) / 'Bands'
        (bands / 'Iron Delta').mkdir(parents=True)
        self._old_root = mcp.prompt_band_root
        mcp.prompt_band_root = lambda: bands  # never touch real band folders
        self.server = mcp.MPWServer(allow_write=True, db=self.db)
        self.server.client = 'claude-code'

    def tearDown(self):
        mcp.prompt_band_root = self._old_root
        self.tmp.cleanup()

    def test_write_only_with_explicit_opt_in(self):
        self.assertFalse(mcp.write_enabled([], {}))
        self.assertTrue(mcp.write_enabled(['--allow-write'], {}))
        self.assertTrue(mcp.write_enabled([], {'MPW_MCP_ALLOW_WRITE': '1'}))
        names = {t['name'] for t in request(self.server, 'tools/list')['result']['tools']}
        self.assertIn('save_prompt_version', names)

    def test_save_adds_version_and_archive_without_touching_active_prompt(self):
        err, data = call(self.server, 'save_prompt_version', song_id=1, style='Neu', lyrics='[Chorus]\nNeu', brief='Idee')
        self.assertFalse(err, data)
        self.assertEqual((data['provider'], data['model']), ('MCP', 'claude-code'))
        archive = Path(data['archive_file'])
        self.assertTrue(archive.is_file())
        self.assertEqual(archive.parent.name, 'Song-Prompts')
        self.assertIn('[STYLE]\nNeu\n[/STYLE]', archive.read_text(encoding='utf-8'))
        with closing(sqlite3.connect(self.db)) as con:
            self.assertEqual(con.execute('SELECT style, lyrics FROM songs WHERE id=1').fetchone(),
                             ('Delta Blues', '[Verse 1]\nRegen'))
            self.assertEqual(con.execute('SELECT COUNT(*) FROM prompt_versions').fetchone()[0], 2)
            self.assertEqual(con.execute("SELECT style FROM prompt_versions WHERE provider='Claude'").fetchone()[0], 'S1')

    def test_save_rejects_limits_and_unknown_song(self):
        cases = [dict(song_id=1, style='x' * 1001, lyrics='y'), dict(song_id=1, style='x', lyrics='y' * 5001),
                 dict(song_id=1, style='  ', lyrics='y'), dict(song_id=999, style='x', lyrics='y')]
        for args in cases:
            with self.subTest(args={k: str(v)[:10] for k, v in args.items()}):
                err, _text = call(self.server, 'save_prompt_version', **args)
                self.assertTrue(err)
        with closing(sqlite3.connect(self.db)) as con:
            self.assertEqual(con.execute('SELECT COUNT(*) FROM prompt_versions').fetchone()[0], 1)


class McpStdio(unittest.TestCase):
    def test_stdio_session_writes_only_json_lines_to_stdout(self):
        with tempfile.TemporaryDirectory(prefix='mpw_mcp_stdio_') as tmp:
            db = make_db(tmp)
            env = dict(os.environ, MPW_DATA_ROOT=str(db.parent), QT_QPA_PLATFORM='offscreen')
            env.pop('MPW_MCP_ALLOW_WRITE', None)
            lines = [
                {'jsonrpc': '2.0', 'id': 1, 'method': 'initialize',
                 'params': {'protocolVersion': '2025-06-18', 'capabilities': {}, 'clientInfo': {'name': 't', 'version': '1'}}},
                {'jsonrpc': '2.0', 'method': 'notifications/initialized'},
                {'jsonrpc': '2.0', 'id': 2, 'method': 'tools/list'},
                {'jsonrpc': '2.0', 'id': 3, 'method': 'tools/call',
                 'params': {'name': 'get_song', 'arguments': {'song_id': 1}}},
            ]
            payload = ''.join(json.dumps(m, ensure_ascii=False) + '\n' for m in lines).encode('utf-8')
            proc = subprocess.run([sys.executable, str(SOURCE / 'mpw_mcp_server.py')], input=payload,
                                  capture_output=True, env=env, timeout=120)
            self.assertEqual(proc.returncode, 0, proc.stderr.decode('utf-8', 'replace'))
            replies = [json.loads(line) for line in proc.stdout.decode('utf-8').splitlines()]
            self.assertEqual([r['id'] for r in replies], [1, 2, 3])
            self.assertIn('Delta Blues', replies[2]['result']['content'][0]['text'])
            self.assertIn('Schreibzugriff: aus', proc.stderr.decode('utf-8', 'replace'))


class McpBuildIntegration(unittest.TestCase):
    def test_build_produces_mcp_executable(self):
        build = (ROOT / 'scripts' / 'build.ps1').read_text(encoding='utf-8-sig')
        spec = (ROOT / 'installer' / 'MPW.spec').read_text(encoding='utf-8')
        self.assertIn("mpw_mcp_server.py", spec)
        self.assertIn("name='MPW-MCP'", spec)
        self.assertIn('console=True', spec)
        self.assertIn("Assert-NonEmptyFile $mcpExe 'MPW-MCP.exe'", build)
        self.assertIn("Assert-LastExit 'MCP-Selbsttest'", build)

    def test_gui_and_mcp_share_one_prompt_builder(self):
        text = (SOURCE / 'workstation.py').read_text(encoding='utf-8') + (SOURCE / 'mpw_core.py').read_text(encoding='utf-8')
        self.assertIn('def suno_prompt_request(con, sid, preset_id=None, brief=', text)
        self.assertIn('return suno_prompt_request(self.con, sid', text)
        self.assertNotIn('_removed_ai_prompt_body', text)


if __name__ == '__main__':
    unittest.main()
