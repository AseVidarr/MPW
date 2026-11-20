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
import time
import unittest
from unittest import mock
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

    # --- stage 4: AI Prompt Launcher (no network: the provider call is replaced) ---
    def wait_job(self, job_id):
        for _ in range(100):
            status, job = self.json_call('GET', f'/api/ai/jobs/{job_id}')
            self.assertEqual(status, 200)
            if job['status'] != 'running':
                return job
            time.sleep(0.05)
        self.fail('AI job did not finish')

    def fake_provider(self, answer=None, error=None):
        calls = []
        original = self.ws.call_provider

        def fake(provider, model, key, prompt):
            calls.append((provider, model, key, prompt))
            if error:
                raise error
            return answer
        self.ws.call_provider = fake
        self.addCleanup(setattr, self.ws, 'call_provider', original)
        return calls

    def test_ai_options_targets_and_song_entry(self):
        with mock.patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'sk-env-secret'}, clear=False):
            options = self.json_call('GET', '/api/ai/options')[1]
        self.assertEqual(options['providers'], ['ChatGPT', 'Gemini', 'Claude'])
        self.assertIs(options['key_in_env']['Claude'], True)
        self.assertNotIn('sk-env-secret', json.dumps(options))  # only whether a key exists, never the key
        self.assertEqual(set(options['error_texts']), {'de', 'en', 'fr', 'es', 'it'})
        with closing(sqlite3.connect(self.db)) as con, con:
            con.execute("INSERT INTO projects(band_id,name) VALUES (1,'Neues Lied')")
        targets = self.json_call('GET', '/api/ai/targets?band_id=1')[1]
        self.assertEqual([(t['name'], t['song_id']) for t in targets], [('Neues Lied', None), ('Rain Song', 1)])
        project = targets[0]['project_id']
        self.assertEqual(self.json_call('POST', f'/api/projects/{project}/song', {})[1]['error'], 'confirm_required')
        status, result = self.json_call('POST', f'/api/projects/{project}/song', {'confirm': True})
        self.assertEqual((status, result['created']), (200, True))
        self.assertIs(self.json_call('POST', f'/api/projects/{project}/song', {'confirm': True})[1]['created'], False)
        self.assertEqual(self.json_call('POST', '/api/projects/99/song', {'confirm': True})[0], 404)

    def test_ai_generate_via_api_splits_answer_and_never_returns_the_key(self):
        calls = self.fake_provider(answer='{"style": "Delta Blues, slide", "lyrics": "[Verse 1]\\nRain"}')
        body = {'song_id': 1, 'provider': 'Claude', 'mode': 'api', 'model': 'claude-sonnet-5-5',
                'api_key': ' sk-typed-secret ', 'brief': 'Regen im Delta', 'preset_id': None}
        status, started = self.json_call('POST', '/api/ai/generate', body)
        self.assertEqual(status, 200)
        job = self.wait_job(started['job'])
        self.assertEqual((job['status'], job['style'], job['lyrics']), ('done', 'Delta Blues, slide', '[Verse 1]\nRain'))
        self.assertNotIn('sk-typed-secret', json.dumps(job))
        provider, model, key, prompt = calls[0]
        self.assertEqual((provider, model, key), ('Claude', 'claude-sonnet-5-5', 'sk-typed-secret'))
        self.assertIn('Band: Iron Delta', prompt)
        self.assertIn('Gitarre: Les Paul', prompt)
        self.assertIn('Songidee: Regen im Delta', prompt)

    def test_ai_generate_errors(self):
        body = {'song_id': 1, 'provider': 'Claude', 'mode': 'api', 'model': 'claude-sonnet-5-5', 'brief': ''}
        with mock.patch.dict(os.environ, {'ANTHROPIC_API_KEY': ''}, clear=False):
            status, result = self.json_call('POST', '/api/ai/generate', body)
        self.assertEqual((status, result['error'], result['env']), (400, 'key_missing', 'ANTHROPIC_API_KEY'))
        self.assertEqual(self.json_call('POST', '/api/ai/generate', {**body, 'model': 'x; rm'})[1]['error'], 'invalid_model')
        self.assertEqual(self.json_call('POST', '/api/ai/generate', {**body, 'provider': 'Other'})[1]['error'], 'invalid_provider')
        self.assertEqual(self.json_call('POST', '/api/ai/generate', {**body, 'song_id': 99, 'api_key': 'k'})[0], 404)
        self.assertEqual(self.json_call('POST', '/api/ai/generate', {**body, 'song_id': None})[1]['error'], 'no_song')
        status, result = self.json_call('POST', '/api/ai/generate', {**body, 'mode': 'cli', 'cli_command': 'mpw-no-such-cli-xyz'})
        self.assertEqual((status, result['error'], result['kind']), (400, 'provider', 'cli_missing'))
        self.assertEqual(self.json_call('POST', '/api/ai/generate', {**body, 'mode': 'cli', 'cli_command': 'claude & calc'})[1]['kind'],
                         'cli_invalid')
        # provider failure -> stable kind for the translated message; the key never leaks
        self.fake_provider(error=self.ws.ProviderError('auth', 'Claude', 401, 'invalid x-api-key'))
        job = self.wait_job(self.json_call('POST', '/api/ai/generate', {**body, 'api_key': 'sk-bad'})[1]['job'])
        self.assertEqual((job['status'], job['error']['kind'], job['error']['code']), ('failed', 'auth', '401'))
        self.fake_provider(answer='Hier ist dein Song, viel Spaß!')
        job = self.wait_job(self.json_call('POST', '/api/ai/generate', {**body, 'api_key': 'k'})[1]['job'])
        self.assertEqual(job['error']['kind'], 'split')
        self.assertEqual(self.json_call('GET', '/api/ai/jobs/0123456789abcdef')[0], 404)

    def test_ai_only_one_request_at_a_time(self):
        release = threading.Event()
        original = self.ws.call_provider
        self.ws.call_provider = lambda *args: (release.wait(5), '{"style":"s","lyrics":"l"}')[1]
        self.addCleanup(setattr, self.ws, 'call_provider', original)
        self.addCleanup(release.set)
        body = {'song_id': 1, 'provider': 'Gemini', 'mode': 'api', 'model': 'gemini-2.5-flash', 'api_key': 'k', 'brief': ''}
        first = self.json_call('POST', '/api/ai/generate', body)[1]['job']
        self.assertEqual(self.json_call('POST', '/api/ai/generate', body)[1]['error'], 'ai_busy')
        release.set()
        self.assertEqual(self.wait_job(first)['status'], 'done')

    def test_ai_request_text_and_parse(self):
        status, result = self.json_call('POST', '/api/ai/request-text', {'song_id': 1, 'provider': 'Gemini', 'brief': 'Idee'})
        self.assertEqual(status, 200)
        self.assertEqual(result['url'], 'https://gemini.google.com/')
        self.assertIn('Copy-Box', result['text'])
        self.assertNotIn('ausschließlich als JSON-Objekt', result['text'])
        parsed = self.json_call('POST', '/api/ai/parse', {'text': 'STYLE\n[STYLE]\nFolk\n[/STYLE]\n[LYRICS]\nText\n[/LYRICS]'})[1]
        self.assertEqual((parsed['style'], parsed['lyrics']), ('Folk', 'Text'))
        self.assertEqual(self.json_call('POST', '/api/ai/parse', {'text': 'nur Plauderei'})[1]['error'], 'no_structure')

    def test_ai_save_version_with_text_archive(self):
        band_folder = Path(self.tmp.name) / 'Bands' / 'Iron Delta'
        body = {'provider': 'Claude', 'model': 'claude-sonnet-5-5', 'style': ' Blues ', 'lyrics': '[Verse]\nneu', 'brief': 'Idee'}
        # without band folder: version is saved, the text file is reported as not possible
        status, result = self.json_call('POST', '/api/songs/1/prompt-versions', body)
        self.assertEqual(status, 200)
        self.assertIsNone(result['file'])
        self.assertTrue(result['file_error'])
        band_folder.mkdir(parents=True)
        result = self.json_call('POST', '/api/songs/1/prompt-versions', body)[1]
        self.assertIsNone(result['file_error'])
        archived = Path(result['file'])
        self.assertEqual(archived.parent, band_folder / self.ws.BAND_PROMPT_FOLDER)
        self.assertIn('[STYLE]\nBlues\n[/STYLE]', archived.read_text(encoding='utf-8'))
        with closing(sqlite3.connect(self.db)) as con:
            self.assertEqual(con.execute('SELECT provider,model,style,brief FROM prompt_versions ORDER BY id').fetchall(),
                             [('Claude', 'claude-sonnet-5-5', 'Blues', 'Idee')] * 2)
            self.assertEqual(con.execute('SELECT style FROM songs WHERE id=1').fetchone()[0], 'alt')  # active prompt unchanged
        self.assertEqual(self.json_call('POST', '/api/songs/1/prompt-versions', {**body, 'style': 'x' * 1001})[1]['error'], 'too_long')
        self.assertEqual(self.json_call('POST', '/api/songs/1/prompt-versions', {**body, 'lyrics': ' '})[1]['error'], 'empty_field')
        self.assertEqual(self.json_call('POST', '/api/songs/99/prompt-versions', body)[0], 404)

    # --- stage 8: Backup (temp data only) ---
    def wait_backup(self, job_id):
        for _ in range(200):
            job = self.json_call('GET', f'/api/backup/jobs/{job_id}')[1]
            if job['status'] != 'running':
                return job
            time.sleep(0.05)
        self.fail('backup job did not finish')

    def use_backup_folder(self):
        folder = Path(self.tmp.name) / 'Sicherungen'
        self.assertEqual(self.json_call('POST', '/api/backup/folder', {'folder': str(folder)})[1]['error'], 'confirm_required')
        self.assertEqual(self.json_call('POST', '/api/backup/folder', {'folder': 'relativ', 'confirm': True})[1]['error'],
                         'folder_not_absolute')
        self.assertEqual(self.json_call('POST', '/api/backup/folder', {'folder': str(folder), 'confirm': True})[0], 200)
        return folder

    def test_backup_folder_settings_and_status(self):
        info = self.json_call('GET', '/api/backup')[1]
        self.assertIs(info['reachable'], False)  # default <data>/backups does not exist yet
        folder = self.use_backup_folder()
        info = self.json_call('GET', '/api/backup')[1]
        self.assertEqual((info['reachable'], info['folder'], info['backups']), (True, str(folder), []))
        self.assertEqual(self.json_call('POST', '/api/backup/settings', {'interval': 2, 'keep': 10})[0], 400)
        self.assertEqual(self.json_call('POST', '/api/backup/settings', {'interval': 7, 'keep': 4})[0], 400)
        self.assertEqual(self.json_call('POST', '/api/backup/settings', {'interval': 7, 'keep': 20})[0], 200)
        info = self.json_call('GET', '/api/backup')[1]
        self.assertEqual((info['interval'], info['keep']), (7, 20))
        self.assertIsNotNone(info['next_due'])  # no automatic backup yet: due at the next desktop start
        settings = json.loads((Path(self.tmp.name) / 'backup_settings.json').read_text(encoding='utf-8'))
        self.assertEqual((settings['automatic_interval_days'], settings['backup_directory']), (7, str(folder)))
        self.assertIs(self.json_call('POST', '/api/backup/integrity', {})[1]['ok'], True)
        test = self.json_call('POST', '/api/backup/test', {})[1]
        self.assertIs(test['ok'], True)
        self.assertEqual(list(folder.iterdir()), [])  # the write test leaves nothing behind

    def test_backup_create_validate_and_log(self):
        folder = self.use_backup_folder()
        self.assertEqual(self.json_call('POST', '/api/backup/create', {})[1]['error'], 'confirm_required')
        job = self.wait_backup(self.json_call('POST', '/api/backup/create', {'confirm': True})[1]['job'])
        self.assertEqual(job['status'], 'done')
        self.assertTrue((folder / job['file']).is_file())
        self.ws.validate_backup(folder / job['file'])
        (folder / 'kaputt.zip').write_bytes(b'not a zip')
        result = self.wait_backup(self.json_call('POST', '/api/backup/validate', {})[1]['job'])
        self.assertEqual({r['name']: r['ok'] for r in result['results']}, {job['file']: True, 'kaputt.zip': False})
        single = self.wait_backup(self.json_call('POST', '/api/backup/validate', {'name': job['file']})[1]['job'])
        self.assertEqual([r['ok'] for r in single['results']], [True])
        for bad in ('../workstation.db', 'x/../y.zip', 'fehlt.zip', 'backup_settings.json'):
            self.assertIn(self.json_call('POST', '/api/backup/validate', {'name': bad})[0], (400, 404), bad)
        info = self.json_call('GET', '/api/backup')[1]
        self.assertEqual((info['stats']['ok'], info['stats']['failed']), (1, 0))
        self.assertEqual([b['name'] for b in info['backups']][:1], ['kaputt.zip'])  # newest first
        self.assertEqual(self.json_call('GET', '/api/backup/log')[1]['entries'][0]['status'], 'OK')

    def test_backup_restore_needs_two_confirmations_and_makes_safety_backup(self):
        folder = self.use_backup_folder()
        backup = self.wait_backup(self.json_call('POST', '/api/backup/create', {'confirm': True})[1]['job'])['file']
        with closing(sqlite3.connect(self.db)) as con, con:
            con.execute("INSERT INTO bands(name) VALUES ('Nach dem Backup')")
        body = {'name': backup, 'confirm': True, 'confirm_text': 'WIEDERHERSTELLEN'}
        self.assertEqual(self.json_call('POST', '/api/backup/restore', {**body, 'confirm': False})[1]['error'], 'confirm_required')
        self.assertEqual(self.json_call('POST', '/api/backup/restore', {**body, 'confirm_text': 'ja'})[1]['error'], 'confirm_text')
        self.assertEqual(self.json_call('POST', '/api/backup/restore', {**body, 'name': '../workstation.db'})[0], 400)
        with closing(sqlite3.connect(self.db)) as con:  # nothing changed so far
            self.assertEqual(con.execute('SELECT COUNT(*) FROM bands').fetchone()[0], 2)
        job = self.wait_backup(self.json_call('POST', '/api/backup/restore', body)[1]['job'])
        self.assertEqual((job['status'], job['ok']), ('done', True))
        self.assertTrue(job['safety'].startswith('MPW_vor_Wiederherstellung_'))
        self.assertTrue((folder / job['safety']).is_file())
        with closing(sqlite3.connect(self.db)) as con:
            self.assertEqual([r[0] for r in con.execute('SELECT name FROM bands')], ['Iron Delta'])
        # the safety backup still holds the state before the restore
        with tempfile.TemporaryDirectory() as tmp:
            import zipfile
            with zipfile.ZipFile(folder / job['safety']) as archive:
                archive.extract('workstation.db', tmp)
            with closing(sqlite3.connect(Path(tmp) / 'workstation.db')) as con:
                self.assertEqual(con.execute('SELECT COUNT(*) FROM bands').fetchone()[0], 2)

    # --- automatic backup (shared by desktop start and MPW-Web) ---
    def auto_backup(self):
        with closing(sqlite3.connect(self.db)) as con:
            return self.ws.run_due_automatic_backup(con, Path(self.tmp.name))

    def test_automatic_backup_due_lock_and_retention(self):
        root = Path(self.tmp.name)
        self.assertIsNone(self.auto_backup())  # disabled by default
        folder = root / 'Sicherungen'
        self.ws.save_backup_settings(root, automatic_interval_days=1, automatic_keep_count=3,
                                     backup_directory=str(folder))
        with self.assertRaises(OSError):  # backup drive missing: reported, nothing created
            self.auto_backup()
        folder.mkdir()
        first = self.auto_backup()
        self.assertTrue(first['file'].startswith('MPW_auto_') and (folder / first['file']).is_file())
        self.assertIsNone(self.auto_backup())  # not due again within the interval
        self.assertFalse((folder / self.ws.AUTO_BACKUP_LOCK).exists())
        # older automatic backups beyond the retention count are removed – manual ones never
        old = time.time() - 10 * 86400
        for i in range(4):
            path = folder / f'MPW_auto_2020010{i}_000000_000000.zip'
            path.write_bytes(b'x')
            os.utime(path, (old - i * 3600, old - i * 3600))
        manual = folder / 'MPW_backup_20200101_000000_000000.zip'
        manual.write_bytes(b'x')
        os.utime(manual, (old - 99 * 86400,) * 2)
        os.utime(folder / first['file'], (old + 3600,) * 2)  # make the newest one due again
        second = self.auto_backup()
        autos = sorted(p.name for p in folder.glob('MPW_auto_*.zip'))
        self.assertEqual(len(autos), 3)
        self.assertIn(second['file'], autos)
        self.assertEqual(len(second['deleted']), 3)
        self.assertTrue(manual.is_file())
        # another MPW program holds the lock: nothing is done; a lock from a crash is replaced
        os.utime(folder / second['file'], (old,) * 2)
        lock = folder / self.ws.AUTO_BACKUP_LOCK
        lock.write_text('123 other program', encoding='utf-8')
        self.assertIsNone(self.auto_backup())
        self.assertTrue(lock.exists())
        os.utime(lock, (old,) * 2)
        self.assertIsNotNone(self.auto_backup())
        self.assertFalse(lock.exists())

    def test_mpw_web_runs_due_automatic_backup_and_reports_it(self):
        root = Path(self.tmp.name)
        self.ws.save_backup_settings(root, automatic_interval_days=7, backup_directory=str(root / 'fehlt'))
        status = self.web.run_auto_backup_check(self.server)
        self.assertEqual(status['state'], 'failed')
        self.assertEqual(self.json_call('GET', '/api/backup')[1]['auto_run']['state'], 'failed')
        (root / 'fehlt').mkdir()
        thread = self.server.start_auto_backup(interval=60)
        for _ in range(100):
            if (self.server.auto_backup or {}).get('state') == 'created':
                break
            time.sleep(0.05)
        info = self.json_call('GET', '/api/backup')[1]
        self.assertEqual(info['auto_run']['state'], 'created')
        self.assertEqual([b['name'] for b in info['backups']], [info['auto_run']['file']])
        self.assertIsNotNone(info['last_automatic'])
        self.server._stop_auto_backup.set()
        thread.join(5)
        self.assertFalse(thread.is_alive())

    # --- stage 7: Medien & Releases ---
    def test_media_links_add_and_delete_with_confirmation(self):
        body = {'platform': 'Spotify', 'url': 'https://open.spotify.com/track/x', 'label': 'Single'}
        status, created = self.json_call('POST', '/api/songs/1/media-links', body)
        self.assertEqual(status, 200)
        self.assertEqual(self.json_call('POST', '/api/songs/1/media-links', body)[1]['error'], 'link_exists')
        for url in ('javascript:alert(1)', 'ftp://x/y', 'https://user:pw@host/x', ''):
            self.assertEqual(self.json_call('POST', '/api/songs/1/media-links', {**body, 'url': url})[0], 400, url)
        media = self.json_call('GET', '/api/songs/1/media')[1]
        self.assertEqual([(l['platform'], l['label']) for l in media['links']], [('Spotify', 'Single')])
        path = f"/api/songs/1/media-links/{created['id']}/delete"
        self.assertEqual(self.json_call('POST', path, {})[1]['error'], 'confirm_required')
        self.assertEqual(self.json_call('POST', '/api/songs/2/media-links/%d/delete' % created['id'], {'confirm': True})[0], 404)
        self.assertEqual(self.json_call('POST', path, {'confirm': True})[0], 200)
        self.assertEqual(self.json_call('GET', '/api/songs/1/media')[1]['links'], [])

    def test_media_files_served_only_with_their_id_and_allowed_types(self):
        project = Path(self.tmp.name) / 'Bands' / 'Iron Delta' / 'Rain Song'
        (project / 'Audio').mkdir(parents=True)
        (project / 'Dokumente').mkdir()
        (project / 'Audio' / 'mix.mp3').write_bytes(b'ID3' + bytes(range(256)) * 4)
        (project / 'Dokumente' / 'notes.txt').write_text('Notizen', encoding='utf-8')
        (project / 'Dokumente' / 'page.html').write_text('<script>alert(1)</script>', encoding='utf-8')
        media = self.json_call('GET', '/api/songs/1/media')[1]
        files = {f['name']: f for f in media['files']}
        self.assertEqual(set(files), {'mix.mp3', 'notes.txt', 'page.html'})
        self.assertNotIn('path', files['mix.mp3'])  # no file system paths to the browser
        self.assertIsNone(files['page.html']['url'])  # not a previewable type: never delivered
        url = files['mix.mp3']['url']
        status, headers, raw = self.call('GET', url, token=False)  # the id itself is the key
        self.assertEqual((status, headers['Content-Type'], len(raw)), (200, 'audio/mpeg', 3 + 1024))
        self.assertIn('sandbox', headers['Content-Security-Policy'])
        request = urllib.request.Request(f'http://127.0.0.1:{self.server.port}{url}', headers={'Range': 'bytes=3-10'})
        with urllib.request.urlopen(request, timeout=10) as response:
            self.assertEqual((response.status, response.headers['Content-Range'], response.read()),
                             (206, 'bytes 3-10/1027', bytes(range(8))))
        self.assertEqual(self.call('GET', files['notes.txt']['url'], token=False)[2].decode(), 'Notizen')
        self.assertEqual(self.call('GET', '/media/1/' + '0' * 32, token=False)[0], 404)
        self.assertEqual(self.call('GET', url.replace('/media/1/', '/media/2/'), token=False)[0], 404)
        self.assertEqual(self.call('GET', url, token=False, host='evil.example')[0], 403)

    def test_releases_checklist_save_isrc_match_and_platforms(self):
        info = self.json_call('GET', '/api/songs/1/releases')[1]
        self.assertEqual(info['releases'], [])
        self.assertIn('DistroKid', info['distributors'])
        body = {'distributor': 'DistroKid', 'release_date': '2026-12-24', 'isrc': 'de-abc-26-00001', 'upc': '4006381333931'}
        items = self.json_call('POST', '/api/songs/1/releases/check', body)[1]['items']
        self.assertEqual([i[0] for i in items], ['ok'] * 5)
        self.assertEqual(items[2], ['ok', 'Veröffentlichungsdatum angegeben: ', {'date': '24.12.2026'}])
        bad = self.json_call('POST', '/api/songs/1/releases/check', {**body, 'isrc': 'X', 'upc': '4006381333932'})[1]['items']
        self.assertIn(['issue', 'ISRC hat kein gültiges 12-stelliges Format.', {}], bad)
        self.assertIn(['issue', 'UPC/EAN-Prüfziffer stimmt nicht.', {}], bad)
        status, saved = self.json_call('POST', '/api/songs/1/releases', body)
        self.assertEqual((status, saved['created']), (200, True))
        # same ISRC again: the user must choose the record and confirm the update
        status, result = self.json_call('POST', '/api/songs/1/releases', {**body, 'distributor': 'TuneCore'})
        self.assertEqual((status, result['error'], [m['id'] for m in result['matches']]), (409, 'isrc_exists', [saved['id']]))
        self.assertEqual(self.json_call('POST', '/api/songs/1/releases', {**body, 'update_id': saved['id']})[1]['error'],
                         'confirm_required')
        status, updated = self.json_call('POST', '/api/songs/1/releases',
                                         {**body, 'distributor': 'TuneCore', 'update_id': saved['id'], 'confirm': True})
        self.assertEqual((status, updated['created']), (200, False))
        self.assertEqual(self.json_call('POST', '/api/songs/1/releases', {**body, 'isrc': 'ABC'})[1]['error'], 'invalid_isrc')
        self.assertEqual(self.json_call('POST', '/api/songs/1/releases', {**body, 'release_date': '24.12.2026', 'isrc': ''})[1]['error'],
                         'invalid_date')
        self.assertEqual(self.json_call('POST', '/api/songs/1/releases', {**body, 'distributor': ' ', 'isrc': ''})[1]['error'],
                         'empty_field')
        path = f"/api/releases/{saved['id']}/platforms"
        self.assertEqual(self.json_call('POST', path, {'platform': 'Spotify', 'status': 'Eingereicht', 'url': ''})[0], 200)
        self.assertEqual(self.json_call('POST', path, {'platform': 'Spotify', 'status': 'Veröffentlicht',
                                                       'url': 'https://open.spotify.com/x'})[0], 200)
        self.assertEqual(self.json_call('POST', path, {'platform': 'Myspace', 'status': 'Geplant', 'url': ''})[1]['error'],
                         'invalid_platform')
        self.assertEqual(self.json_call('POST', path, {'platform': 'Spotify', 'status': 'Published', 'url': ''})[1]['error'],
                         'invalid_status')
        releases = self.json_call('GET', '/api/songs/1/releases')[1]['releases']
        self.assertEqual((releases[0]['distributor'], releases[0]['isrc'], releases[0]['platforms']),
                         ('TuneCore', 'DEABC2600001', [{'platform': 'Spotify', 'status': 'Veröffentlicht',
                                                        'url': 'https://open.spotify.com/x'}]))

    # --- stage 6: KI-Verbindungen (no real CLI commands: every helper is replaced) ---
    def patch_ws(self, **replacements):
        for name, value in replacements.items():
            self.addCleanup(setattr, self.ws, name, getattr(self.ws, name))
            setattr(self.ws, name, value)

    def wait_check(self, job_id):
        for _ in range(100):
            job = self.json_call('GET', f'/api/connections/jobs/{job_id}')[1]
            if job['status'] != 'running':
                return job
            time.sleep(0.05)
        self.fail('check did not finish')

    def test_connections_info_and_status_check(self):
        info = self.json_call('GET', '/api/connections')[1]
        self.assertEqual([c['id'] for c in info['clients']], ['claude', 'gemini', 'codex'])
        self.assertEqual(set(info['texts']), {'de', 'en', 'fr', 'es', 'it'})
        self.assertTrue(all(url.startswith('https://') for url in info['links'].values()))
        result = {'claude': r'C:\x\claude.exe', 'gemini': None, 'codex': None, 'node': None, 'claude_logged_in': True,
                  'keys': {'Claude': True, 'ChatGPT': False, 'Gemini': False},
                  'mcp': {'claude': {'mpw': 'connected', 'suno': 'needs_auth'}},
                  'tls': {'api.anthropic.com': {'error': None, 'intercepted': 'O=Norton Web/Mail Shield'},
                          'api.suno.com': {'error': None, 'intercepted': None}}}
        self.patch_ws(check_ai_connections=lambda: result)
        job = self.wait_check(self.json_call('POST', '/api/connections/check', {})[1]['job'])
        self.assertIs(job['intercepted'], True)
        self.assertEqual(job['lines']['claude_login'], ['logged_in', {}])
        self.assertEqual(job['lines']['mcp_suno_claude'], ['cli_line', {'name': 'Claude Code', 'status': ['mcp_needs_auth', {}]}])
        self.assertEqual(job['lines']['key_ChatGPT'], ['key_missing', {'env': 'OPENAI_API_KEY'}])
        # the same lines render to the desktop texts
        de = self.ws.AI_CONNECTION_TEXTS['de']
        self.assertEqual(self.ws.render_ai_connection_line(de, job['lines']['mcp_mpw_claude']), 'Claude Code: ✔ verbunden')

    def test_connections_setup_needs_confirmation_and_runs_fixed_commands(self):
        ran = []
        self.patch_ws(find_cli=lambda c: f'C:\\bin\\{c}.exe' if c != 'codex' else None,
                      run_helper_tool=lambda args, timeout=90, cwd=None: (ran.append(args), (0, 'ok'))[1])
        body = {'server': 'suno', 'action': 'add', 'client': 'claude'}
        self.assertEqual(self.json_call('POST', '/api/connections/setup', body)[1]['error'], 'confirm_required')
        self.assertEqual(ran, [])
        self.assertIs(self.json_call('POST', '/api/connections/setup', {**body, 'confirm': True})[1]['ok'], True)
        self.assertEqual(ran[-1], ['C:\\bin\\claude.exe', 'mcp', 'add', '--scope', 'user', '--transport', 'http',
                                   'suno', 'https://api.suno.com/mcp'])
        status, result = self.json_call('POST', '/api/connections/setup', {**body, 'client': 'codex', 'confirm': True})
        self.assertEqual((status, result['error'], result['name']), (400, 'need_cli', 'Codex CLI'))
        self.assertEqual(self.json_call('POST', '/api/connections/setup', {**body, 'client': 'evil', 'confirm': True})[0], 400)
        self.assertEqual(self.json_call('POST', '/api/connections/setup', {**body, 'server': 'x', 'confirm': True})[0], 400)
        self.patch_ws(mpw_mcp_server_command=lambda: ['C:\\nowhere\\MPW-MCP.exe'])
        result = self.json_call('POST', '/api/connections/setup', {'server': 'mpw', 'action': 'add', 'client': 'gemini',
                                                                   'confirm': True})[1]
        self.assertEqual(result['error'], 'mcp_exe_missing')
        self.patch_ws(run_helper_tool=lambda args, timeout=90, cwd=None: (1, 'boom'))
        result = self.json_call('POST', '/api/connections/setup', {**body, 'action': 'remove', 'confirm': True})[1]
        self.assertEqual((result['ok'], result['detail']), (False, 'boom'))

    def test_connections_login_and_desktop_config(self):
        self.patch_ws(find_cli=lambda c: None)
        self.assertEqual(self.json_call('POST', '/api/connections/login', {'target': 'claude'})[1]['error'], 'need_claude')
        self.patch_ws(find_cli=lambda c: f'/usr/bin/{c}')
        with mock.patch('subprocess.Popen') as popen, mock.patch.object(self.web.sys, 'platform', 'linux'):
            result = self.json_call('POST', '/api/connections/login', {'target': 'suno', 'client': 'codex'})[1]
        popen.assert_not_called()  # no console elsewhere: the command is shown instead
        self.assertEqual((result['started'], result['command']), (False, '/usr/bin/codex mcp login suno'))
        with mock.patch('subprocess.Popen') as popen, mock.patch.object(self.web.sys, 'platform', 'win32'):
            result = self.json_call('POST', '/api/connections/login', {'target': 'claude'})[1]
        self.assertEqual((result['started'], result['message']), (True, 'login_started'))
        self.assertEqual(popen.call_args[0][0], ['/usr/bin/claude', 'auth', 'login'])
        text = self.json_call('GET', '/api/connections/desktop-config')[1]['text']
        self.assertIn('"mpw"', text)

    # --- stage 5: An Suno senden (no Claude Code, no credits: the send is replaced) ---
    def fake_suno(self, clips=None, change=None, error=None):
        sent = []
        originals = (self.ws.call_suno_via_claude, self.ws.resolve_cli_executable)

        def fake(command, arguments):
            sent.append(arguments)
            if error:
                raise error
            given = dict(arguments, **(change or {}))
            return {'mcp_status': 'connected', 'create_inputs': [given], 'create_result': None, 'errors': [],
                    'wait_result': {'clips': clips if clips is not None else [
                        {'id': 'c1', 'title': 'Rain Song', 'status': 'streaming', 'song_url': 'https://suno.com/song/c1'},
                        {'id': 'c2', 'title': 'Rain Song', 'status': 'streaming', 'song_url': 'javascript:alert(1)'}]}}
        self.ws.call_suno_via_claude = fake
        self.ws.resolve_cli_executable = lambda provider, command: 'claude.exe'
        self.addCleanup(setattr, self.ws, 'call_suno_via_claude', originals[0])
        self.addCleanup(setattr, self.ws, 'resolve_cli_executable', originals[1])
        return sent

    def test_suno_info_lists_saved_prompts(self):
        with closing(sqlite3.connect(self.db)) as con, con:
            con.execute("INSERT INTO prompt_versions(song_id,provider,model,style,lyrics,brief) VALUES (1,'Claude','m','v-style','v-lyrics','')")
        info = self.json_call('GET', '/api/songs/1/suno')[1]
        self.assertEqual(info['title'], 'Rain Song')
        self.assertEqual([(c['version_id'], c['style']) for c in info['choices']], [(None, 'alt'), (1, 'v-style')])
        self.assertEqual(set(info['texts']), {'de', 'en', 'fr', 'es', 'it'})
        self.assertEqual(self.json_call('GET', '/api/songs/99/suno')[0], 404)

    def test_suno_send_uses_saved_prompt_needs_confirmation_and_saves_links(self):
        sent = self.fake_suno()
        body = {'version_id': None, 'title': ' Rain Song ', 'style': 'FROM BROWSER', 'lyrics': 'FROM BROWSER'}
        self.assertEqual(self.json_call('POST', '/api/songs/1/suno/send', body)[1]['error'], 'confirm_required')
        self.assertEqual(sent, [])  # nothing sent without the explicit yes
        status, started = self.json_call('POST', '/api/songs/1/suno/send', {**body, 'confirm': True})
        self.assertEqual(status, 200)
        job = self.wait_job(started['job'])
        # the saved prompt from the database is sent, never text supplied by the browser
        self.assertEqual((sent[0]['title'], sent[0]['style'], sent[0]['lyrics']), ('Rain Song', 'alt', '[Verse]\nalt'))
        self.assertTrue(sent[0]['idempotency_key'].startswith('mpw-'))
        self.assertEqual((job['outcome'], job['values'], job['notes']), ('done', {'count': 2}, []))
        self.assertEqual([c['url'] for c in job['clips']], ['https://suno.com/song/c1', ''])  # non-Suno link dropped
        self.assertNotIn('_private', job)
        # links: only from this server's finished job, for this song
        self.assertEqual(self.json_call('POST', '/api/songs/2/suno/links', {'job': started['job']})[0], 400)
        self.assertEqual(self.json_call('POST', '/api/songs/1/suno/links', {'job': '0123456789abcdef'})[0], 404)
        self.assertEqual(self.json_call('POST', '/api/songs/1/suno/links', {'job': started['job'], 'lang': 'en'})[1]['added'], 1)
        self.assertEqual(self.json_call('POST', '/api/songs/1/suno/links', {'job': started['job']})[1]['added'], 0)  # kept, not doubled
        with closing(sqlite3.connect(self.db)) as con:
            self.assertEqual(con.execute('SELECT platform,url,label FROM media_links').fetchall(),
                             [('Suno', 'https://suno.com/song/c1', 'Suno – Rain Song (1/1)')])

    def test_suno_send_reports_problems(self):
        sent = self.fake_suno(change={'lyrics': 'geändert'})
        job = self.wait_job(self.json_call('POST', '/api/songs/1/suno/send', {'title': 'X', 'confirm': True})[1]['job'])
        self.assertEqual(job['notes'], ['mismatch'])
        self.assertEqual(self.json_call('POST', '/api/songs/1/suno/send', {'version_id': 7, 'title': 'X', 'confirm': True})[1]['error'],
                         'version_missing')
        self.assertEqual(self.json_call('POST', '/api/songs/1/suno/send', {'title': 'x' * 257, 'confirm': True})[1]['error'],
                         'suno_too_long')
        with closing(sqlite3.connect(self.db)) as con, con:
            con.execute("UPDATE songs SET lyrics='' WHERE id=1")
        self.assertEqual(self.json_call('POST', '/api/songs/1/suno/send', {'title': 'X', 'confirm': True})[1]['error'], 'suno_empty')
        self.assertEqual(len(sent), 1)
        with closing(sqlite3.connect(self.db)) as con, con:
            con.execute("UPDATE songs SET lyrics='[Verse]\nneu' WHERE id=1")
        self.fake_suno(error=self.ws.ProviderError('cli_timeout', 'Claude', detail='600'))
        job = self.wait_job(self.json_call('POST', '/api/songs/1/suno/send', {'title': 'X', 'confirm': True})[1]['job'])
        self.assertEqual((job['outcome'], job['values']), ('timeout', {'minutes': 10}))
        original = self.ws.resolve_cli_executable
        self.ws.resolve_cli_executable = lambda provider, command: (_ for _ in ()).throw(
            self.ws.ProviderError('cli_missing', 'Claude', detail='claude'))
        self.addCleanup(setattr, self.ws, 'resolve_cli_executable', original)
        status, result = self.json_call('POST', '/api/songs/1/suno/send', {'title': 'X', 'confirm': True})
        self.assertEqual((status, result['kind']), (400, 'cli_missing'))

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
