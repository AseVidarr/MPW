"""MPW im Browser (mpw_web.py): security, read/write API, shared save rule. Temporary data only."""
import atexit
from contextlib import closing
import json
import os
import shutil
from pathlib import Path
import sqlite3
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request

SOURCE_DIR = Path(__file__).resolve().parents[1] / 'source'


def load_modules():
    """Import with an isolated data root so the user's MPW data is never resolved."""
    if 'mpw_web' in sys.modules:
        return sys.modules['mpw_core'], sys.modules['mpw_web']
    root = tempfile.mkdtemp(prefix='mpw_webtest_root_')
    atexit.register(shutil.rmtree, root, True)  # removed when the test run ends
    os.environ['MPW_DATA_ROOT'] = root
    sys.path.insert(0, str(SOURCE_DIR))
    import mpw_core  # Qt-free: the browser GUI must not need PySide6
    import mpw_web
    return mpw_core, mpw_web


class WebServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ws, cls.web = load_modules()

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        with closing(self.ws.init_database(root)) as con:
            with con:
                con.execute("INSERT INTO bands(name,genre) VALUES ('Iron Delta','Blues')")
                con.execute("INSERT INTO projects(band_id,name) VALUES (1,'Rain Song')")
                con.execute("INSERT INTO songs(project_id,title,style,lyrics) VALUES (1,'Rain Song','alt','[Verse]\nalt')")
                con.execute("INSERT INTO instruments(band_id,category,details) VALUES (1,'Gitarre','Les Paul')")
        self.db = root / 'workstation.db'
        self.server = self.web.MPWWebServer(self.db)
        thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(self.server.server_close)
        self.addCleanup(self.server.shutdown)

    def call(self, method, path, body=None, token=True, host=None, content_type='application/json'):
        request = urllib.request.Request(f'http://127.0.0.1:{self.server.port}{path}', method=method,
                                         data=None if body is None else json.dumps(body).encode('utf-8'))
        if token:
            request.add_header('X-MPW-Token', self.server.token if token is True else token)
        if body is not None:
            request.add_header('Content-Type', content_type)
        if host:
            request.add_header('Host', host)
        try:
            with urllib.request.urlopen(request, timeout=10) as response:
                raw = response.read()
                return response.status, dict(response.headers), raw
        except urllib.error.HTTPError as exc:
            try:
                return exc.code, dict(exc.headers), exc.read()
            finally:
                exc.close()

    def json_call(self, *args, **kwargs):
        status, headers, raw = self.call(*args, **kwargs)
        return status, json.loads(raw or b'null')

    def payload(self, **changes):
        body = {'status': 'In Bearbeitung', 'distributor': '', 'platforms': '', 'style': 'alt', 'lyrics': '[Verse]\nalt'}
        body.update(changes)
        return body

    # --- security ---
    def test_only_loopback_and_token_in_fragment(self):
        self.assertEqual(self.server.server_address[0], '127.0.0.1')
        self.assertTrue(self.server.url.startswith(f'http://127.0.0.1:{self.server.port}/#t='))
        self.assertGreaterEqual(len(self.server.token), 24)

    def test_api_needs_token_and_correct_host(self):
        self.assertEqual(self.json_call('GET', '/api/info')[0], 200)
        self.assertEqual(self.json_call('GET', '/api/info', token=False)[0], 403)
        self.assertEqual(self.json_call('GET', '/api/info', token='wrong')[0], 403)
        self.assertEqual(self.json_call('GET', '/api/info', host='evil.example')[0], 403)  # DNS rebinding
        self.assertEqual(self.json_call('GET', '/', host=f'attacker.test:{self.server.port}')[0], 403)
        self.assertEqual(self.json_call('GET', '/api/info', host=f'localhost:{self.server.port}')[0], 200)

    def test_static_files_with_security_headers_and_no_traversal(self):
        status, headers, raw = self.call('GET', '/', token=False)
        self.assertEqual(status, 200)
        self.assertIn(b'<script src="app.js">', raw)
        self.assertIn("default-src 'self'", headers['Content-Security-Policy'])
        self.assertEqual(headers['X-Frame-Options'], 'DENY')
        self.assertNotIn('Access-Control-Allow-Origin', headers)
        for path in ('/app.js', '/app.css'):
            self.assertEqual(self.call('GET', path, token=False)[0], 200)
        for path in ('/../source/workstation.py', '/web/../mpw_web.py', '/%2e%2e/mpw_web.py', '/workstation.db'):
            self.assertEqual(self.call('GET', path, token=False)[0], 404, path)

    # --- read ---
    def test_read_bands_songs_versions(self):
        self.assertEqual(self.json_call('GET', '/api/bands')[1][0]['name'], 'Iron Delta')
        band = self.json_call('GET', '/api/bands/1')[1]
        self.assertEqual(band['instruments'], [{'category': 'Gitarre', 'details': 'Les Paul'}])
        self.assertEqual(self.json_call('GET', '/api/songs?band_id=1&q=rain')[1][0]['title'], 'Rain Song')
        self.assertEqual(self.json_call('GET', '/api/songs?q=nichts')[1], [])
        song = self.json_call('GET', '/api/songs/1')[1]
        self.assertEqual((song['style'], song['band']), ('alt', 'Iron Delta'))
        self.assertEqual(self.json_call('GET', '/api/songs/1/versions')[1], [])
        self.assertEqual(self.json_call('GET', '/api/songs/99')[0], 404)
        info = self.json_call('GET', '/api/info')[1]
        self.assertEqual(info['statuses'], ['In Bearbeitung', 'Fertig', 'Veröffentlicht'])

    # --- write ---
    def test_save_uses_shared_rule_with_backup_version(self):
        status, result = self.json_call('POST', '/api/songs/1', {**self.payload(style='neu', status='Fertig'),
                                                                  'expected': self.payload()})
        self.assertEqual(status, 200)
        self.assertIs(result['archived'], True)
        with closing(sqlite3.connect(self.db)) as con:
            self.assertEqual(con.execute('SELECT style,status FROM songs WHERE id=1').fetchone(), ('neu', 'Fertig'))
            self.assertEqual(con.execute('SELECT provider,style FROM prompt_versions').fetchall(),
                             [('MPW Sicherung', 'alt')])
        # unchanged prompt -> no extra backup
        status, result = self.json_call('POST', '/api/songs/1', self.payload(style='neu', status='Fertig'))
        self.assertIs(result['archived'], False)

    def test_conflict_when_changed_elsewhere(self):
        with closing(sqlite3.connect(self.db)) as con, con:
            con.execute("UPDATE songs SET style='Desktop' WHERE id=1")
        status, result = self.json_call('POST', '/api/songs/1', {**self.payload(style='Browser'), 'expected': self.payload()})
        self.assertEqual((status, result['error'], result['current']['style']), (409, 'conflict', 'Desktop'))
        with closing(sqlite3.connect(self.db)) as con:
            self.assertEqual(con.execute('SELECT style FROM songs WHERE id=1').fetchone()[0], 'Desktop')

    def test_validation(self):
        self.assertEqual(self.json_call('POST', '/api/songs/1', self.payload(style='x' * 1001))[1]['error'], 'too_long')
        self.assertEqual(self.json_call('POST', '/api/songs/1', self.payload(lyrics='x' * 5001))[0], 400)
        self.assertEqual(self.json_call('POST', '/api/songs/1', self.payload(status='Gelöscht'))[1]['error'], 'invalid_status')
        self.assertEqual(self.json_call('POST', '/api/songs/1', self.payload(style=5))[0], 400)
        self.assertEqual(self.json_call('POST', '/api/songs/1', self.payload(), content_type='text/plain')[0], 415)
        self.assertEqual(self.json_call('POST', '/api/songs/1', self.payload(), token=False)[0], 403)
        self.assertEqual(self.json_call('POST', '/api/songs/99', self.payload())[0], 404)
        self.assertEqual(self.json_call('POST', '/api/info', {})[0], 405)

    # --- stage 3: create bands (folder logic like the desktop app) ---
    def test_create_band_makes_folder_prompt_folder_and_row(self):
        bands_dir = Path(self.tmp.name) / 'Bands'
        status, result = self.json_call('POST', '/api/bands', {'name': ' Neon Harbour ', 'genre': 'Synthwave',
                                                               'second_genre': '', 'persona': 'Keine'})
        self.assertEqual(status, 200)
        self.assertIs(result['created'], True)
        self.assertIsNone(result['prompt_warning'])
        self.assertTrue((bands_dir / 'Neon Harbour').is_dir())
        self.assertTrue((bands_dir / 'Neon Harbour' / self.ws.BAND_PROMPT_FOLDER).is_dir())
        # project subfolders are only created with a project
        self.assertEqual(sorted(p.name for p in (bands_dir / 'Neon Harbour').iterdir()), [self.ws.BAND_PROMPT_FOLDER])
        band = self.json_call('GET', f"/api/bands/{result['id']}/full")[1]
        self.assertEqual((band['name'], band['genre'], band['persona']), ('Neon Harbour', 'Synthwave', 'Keine'))
        self.assertIn('Synthwave', self.json_call('GET', '/api/band-options')[1]['genres'])
        # same name in other case -> existing band, nothing new
        status, again = self.json_call('POST', '/api/bands', {'name': 'neon harbour'})
        self.assertEqual((status, again['error'], again['id']), (409, 'band_exists', result['id']))
        self.assertEqual(self.json_call('POST', '/api/bands', {'name': 'iron delta'})[1]['error'], 'band_exists')

    def test_create_band_takes_over_existing_folder_only_after_confirmation(self):
        folder = Path(self.tmp.name) / 'Bands' / 'Altes Projekt'
        (folder / 'Song A').mkdir(parents=True)
        (folder / 'notiz.txt').write_text('bleibt', encoding='utf-8')
        status, result = self.json_call('POST', '/api/bands', {'name': 'altes projekt'})
        self.assertEqual((status, result['error'], result['folder']), (409, 'folder_exists', 'Altes Projekt'))
        with closing(sqlite3.connect(self.db)) as con:
            self.assertEqual(con.execute('SELECT COUNT(*) FROM bands').fetchone()[0], 1)
        status, result = self.json_call('POST', '/api/bands', {'name': 'altes projekt', 'import_existing': True})
        self.assertEqual(status, 200)
        self.assertIs(result['created'], False)
        self.assertEqual(result['name'], 'Altes Projekt')  # band name follows the folder's spelling
        self.assertEqual((folder / 'notiz.txt').read_text(encoding='utf-8'), 'bleibt')
        self.assertTrue((folder / 'Song A').is_dir())

    def test_create_band_rejects_bad_names_without_touching_disk(self):
        bands_dir = Path(self.tmp.name) / 'Bands'
        for name in ('', '   ', 'a/b', 'x:y', 'CON', 'Ende.', '..', 'Tab\there'):
            status, result = self.json_call('POST', '/api/bands', {'name': name})
            self.assertEqual(status, 400, name)
            self.assertIn(result['error'], ('empty_field', 'invalid_name'), name)
        self.assertEqual(self.json_call('POST', '/api/bands', {'name': 'x' * 121})[1]['error'], 'too_long')
        self.assertEqual(self.json_call('POST', '/api/bands', {'name': 'Gut', 'persona': 'Boss'})[1]['error'], 'invalid_persona')
        self.assertEqual(self.json_call('POST', '/api/bands', {'name': 5})[1]['error'], 'invalid_field')
        self.assertFalse(bands_dir.exists() and any(bands_dir.iterdir()))
        (bands_dir).mkdir(exist_ok=True)
        (bands_dir / 'Datei').write_text('x', encoding='utf-8')  # name taken by a file
        self.assertEqual(self.json_call('POST', '/api/bands', {'name': 'datei'})[0], 500)
        with closing(sqlite3.connect(self.db)) as con:
            self.assertEqual(con.execute('SELECT COUNT(*) FROM bands').fetchone()[0], 1)

    # --- stage 2: bands editing ---
    def test_band_profile_update_keeps_name_and_fills_genre_catalog(self):
        status, band = self.json_call('POST', '/api/bands/1', {'genre': 'Delta Blues', 'second_genre': 'Folk Metal',
                                                                'persona': 'Individuell', 'name': 'Hacked'})
        self.assertEqual(status, 200)
        self.assertEqual((band['name'], band['genre'], band['persona']), ('Iron Delta', 'Delta Blues', 'Individuell'))
        self.assertIn('Folk Metal', band['genre_catalog'])
        self.assertEqual(self.json_call('POST', '/api/bands/1', {'genre': '', 'second_genre': '', 'persona': 'Boss'})[1]['error'],
                         'invalid_persona')
        self.assertEqual(self.json_call('POST', '/api/bands/99', {'genre': '', 'second_genre': '', 'persona': 'Keine'})[0], 404)

    def test_hardware_add_update_delete_and_choices(self):
        status, created = self.json_call('POST', '/api/bands/1/instruments', {'category': ' Mikrofon ', 'details': 'SM7B'})
        self.assertEqual(status, 200)
        band = self.json_call('GET', '/api/bands/1/full')[1]
        self.assertEqual([(i['category'], i['details']) for i in band['instruments']],
                         [('Gitarre', 'Les Paul'), ('Mikrofon', 'SM7B')])
        self.assertEqual(self.json_call('POST', f"/api/instruments/{created['id']}", {'category': 'Mikrofon', 'details': 'U87'})[0], 200)
        choices = self.json_call('GET', '/api/hardware/choices?category=mikrofon')[1]
        self.assertEqual((choices['groups'], choices['details']), (['Gitarre', 'Mikrofon'], ['U87']))
        self.assertEqual(self.json_call('POST', f"/api/instruments/{created['id']}/delete", {})[0], 200)
        self.assertEqual(self.json_call('POST', f"/api/instruments/{created['id']}/delete", {})[0], 404)
        self.assertEqual(self.json_call('POST', '/api/bands/1/instruments', {'category': '', 'details': 'x'})[1]['error'], 'empty_field')
        self.assertEqual(self.json_call('POST', '/api/bands/1/instruments', {'category': 'x', 'details': 'y' * 501})[1]['error'], 'too_long')
        self.assertEqual(self.json_call('POST', '/api/bands/1/instruments', {'category': 'x', 'details': 'y'}, token=False)[0], 403)

    def test_presets_save_add_and_replace_with_confirmation(self):
        status, saved = self.json_call('POST', '/api/bands/1/presets', {'name': 'Studio A'})
        self.assertEqual((status, saved['count']), (200, 1))
        self.assertEqual(self.json_call('POST', '/api/bands/1/presets', {'name': 'studio a'})[0], 409)   # exists
        self.assertEqual(self.json_call('POST', '/api/bands/1/presets', {'name': 'studio a', 'overwrite': True})[0], 200)
        with closing(sqlite3.connect(self.db)) as con, con:
            con.execute("INSERT INTO bands(name) VALUES ('Band B')")
            con.execute("INSERT INTO instruments(band_id,category,details) VALUES (2,'Drums','Tama')")
        pid = self.json_call('GET', '/api/presets')[1][0]['id']
        status, result = self.json_call('POST', f'/api/presets/{pid}/transfer', {'band_id': 2, 'mode': 'add'})
        self.assertEqual((status, result['added'], result['skipped']), (200, 1, 0))
        self.assertEqual(self.json_call('POST', f'/api/presets/{pid}/transfer', {'band_id': 2, 'mode': 'add'})[1]['skipped'], 1)
        # replacing needs an explicit confirmation flag
        self.assertEqual(self.json_call('POST', f'/api/presets/{pid}/transfer', {'band_id': 2, 'mode': 'replace'})[1]['error'],
                         'confirm_required')
        status, result = self.json_call('POST', f'/api/presets/{pid}/transfer', {'band_id': 2, 'mode': 'replace', 'confirm': True})
        self.assertEqual((status, result['removed'], result['added']), (200, 2, 1))
        band = self.json_call('GET', '/api/bands/2/full')[1]
        self.assertEqual([(i['category'], i['details']) for i in band['instruments']], [('Gitarre', 'Les Paul')])
        with closing(sqlite3.connect(self.db)) as con, con:
            con.execute("INSERT INTO hardware_presets(name,items_json) VALUES ('kaputt','{not json')")
        bad = self.json_call('GET', '/api/presets')[1]
        bad_id = next(p['id'] for p in bad if p['name'] == 'kaputt')
        self.assertEqual(self.json_call('POST', f'/api/presets/{bad_id}/transfer', {'band_id': 2, 'mode': 'add'})[1]['error'],
                         'preset_damaged')
        self.assertEqual(self.json_call('POST', '/api/bands/2/presets', {'name': ''})[1]['error'], 'empty_field')

    def test_language_from_mpw_configuration(self):
        # Own temp root: never read or write a configuration outside the test folder.
        saved_root = self.ws.ROOT
        self.ws.ROOT = Path(self.tmp.name)
        self.addCleanup(setattr, self.ws, 'ROOT', saved_root)
        config = self.ws.ROOT / 'app_configuration.json'
        config.write_text('﻿{"ui_language": "fr"}', encoding='utf-8')  # BOM tolerated
        self.assertEqual(self.web.ui_language(), 'fr')
        config.write_text('{"ui_language": "xx"}', encoding='utf-8')
        self.assertEqual(self.web.ui_language(), 'auto')


class WebFilesTests(unittest.TestCase):
    def test_all_five_languages_have_all_keys(self):
        text = (SOURCE_DIR / 'web' / 'app.js').read_text(encoding='utf-8')
        block = text[text.index('const I18N = {'):text.index('\n};', text.index('const I18N = {'))]
        languages = {}
        for lang in ('de', 'en', 'fr', 'es', 'it'):
            start = block.index(f'\n  {lang}: {{')
            end = block.index('\n  },', start)
            # strip string literals first, so words like "ersetzt:" inside texts are not taken for keys
            body = __import__('re').sub(r"'(?:\\.|[^'\\])*'|\"(?:\\.|[^\"\\])*\"", '""', block[start + 6:end])
            languages[lang] = set(__import__('re').findall(r'\b([a-z_0-9]+): ', body))
        for lang, keys in languages.items():
            self.assertEqual(keys, languages['de'], lang)
        html = (SOURCE_DIR / 'web' / 'index.html').read_text(encoding='utf-8')
        used = set(__import__('re').findall(r'data-i18n(?:-placeholder)?="([a-z_0-9]+)"', html))
        self.assertFalse(used - languages['de'], used - languages['de'])

    def test_no_html_injection_paths_in_frontend(self):
        text = (SOURCE_DIR / 'web' / 'app.js').read_text(encoding='utf-8')
        for unsafe in ('innerHTML', 'outerHTML', 'insertAdjacentHTML', 'document.write', 'eval('):
            self.assertNotIn(unsafe, text, unsafe)
        html = (SOURCE_DIR / 'web' / 'index.html').read_text(encoding='utf-8')
        self.assertNotIn('<script>', html)  # CSP: no inline scripts
        self.assertNotIn('style="', html)


if __name__ == '__main__':
    unittest.main()
