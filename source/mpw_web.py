"""MPW im Browser: lokaler Webserver für die Browser-Oberfläche.

Läuft nur auf diesem PC (127.0.0.1) und nutzt denselben Datenordner wie die installierte
bzw. portable MPW (gleiche Datenpfad-Ermittlung wie MPW.exe und MPW-MCP.exe).
Desktop-App und Browser dürfen gleichzeitig geöffnet sein.

Start:  py -3 source\\mpw_web.py            (öffnet den Browser)
        MPW-Web.exe [--port 8765] [--no-browser]
Test:   MPW-Web.exe --self-test             (nur Temp-Daten)

Sicherheit: Server nur auf 127.0.0.1; pro Start ein Zufallsschlüssel, ohne den die
Daten-Schnittstelle nichts liefert; fremde Host-Namen werden abgewiesen (Schutz gegen
DNS-Rebinding), keine CORS-Freigaben. Nur Standardbibliothek.
"""
import argparse
import hmac
import json
import os
import re
import secrets
import sqlite3
import sys
import tempfile
import threading
import urllib.error
import urllib.request
import webbrowser
from contextlib import closing
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import mpw_core as ws  # Qt-free MPW core: runs on Windows, macOS and Linux without PySide6
import mpw_mcp_server as core

LANGUAGES = ('de', 'en', 'fr', 'es', 'it')
STATIC_FILES = {'/': 'index.html', '/index.html': 'index.html', '/app.js': 'app.js', '/app.css': 'app.css'}
CONTENT_TYPES = {'.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8',
                 '.css': 'text/css; charset=utf-8'}
SECURITY_HEADERS = {
    'Content-Security-Policy': "default-src 'self'; img-src 'self' data:; frame-ancestors 'none'; base-uri 'none'; form-action 'none'",
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'Referrer-Policy': 'no-referrer',
    'Cache-Control': 'no-store',
}
MAX_BODY = 64 * 1024
TEXT_LIMITS = {'style': 1000, 'lyrics': 5000, 'distributor': 500, 'platforms': 500}
SONG_FIELDS = ('status', 'distributor', 'platforms', 'style', 'lyrics')


def web_directory():
    """Static files: next to this script, or inside the PyInstaller bundle."""
    base = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parent))
    return base / 'web'


def ui_language():
    """Language chosen in MPW › Konfiguration ('auto' lets the browser decide)."""
    try:
        # utf-8-sig: tolerate a BOM if the file was edited with another tool
        data = json.loads((ws.ROOT / 'app_configuration.json').read_text(encoding='utf-8-sig'))
        value = data.get('ui_language', 'auto') if isinstance(data, dict) else 'auto'
    except (OSError, ValueError):
        value = 'auto'
    return value if value in LANGUAGES else 'auto'


class ApiError(Exception):
    def __init__(self, status, message, extra=None):
        super().__init__(message)
        self.status, self.message, self.extra = status, message, extra or {}


# --------------------------------------------------------------------------- API handlers

def api_info(server, query, body):
    return {'version': ws.APP_VERSION, 'language': ui_language(), 'database': str(server.db_path),
            'statuses': list(ws.SONG_STATUS_KEYS), 'limits': TEXT_LIMITS}


def _read(server, func, args):
    try:
        with closing(core.open_read(server.db_path)) as con:
            return func(con, args)
    except core.ToolError as exc:
        raise ApiError(404, str(exc)) from exc
    except sqlite3.OperationalError as exc:  # e.g. the desktop app is writing right now
        raise ApiError(503, 'database_busy', {'detail': str(exc)}) from exc


def api_bands(server, query, body):
    return _read(server, core.tool_list_bands, {})


def api_band(server, query, body, band_id):
    return _read(server, core.tool_get_band, {'band_id': int(band_id)})


def api_songs(server, query, body):
    args = {'limit': core.MAX_LIMIT}
    if query.get('band_id', [''])[0].isdigit():
        args['band_id'] = int(query['band_id'][0])
    if query.get('q', [''])[0].strip():
        args['query'] = query['q'][0].strip()[:200]
    return _read(server, core.tool_list_songs, args)


def api_song(server, query, body, song_id):
    return _read(server, core.tool_get_song, {'song_id': int(song_id)})


def api_versions(server, query, body, song_id):
    return _read(server, core.tool_list_prompt_versions, {'song_id': int(song_id), 'limit': 200})


def api_version(server, query, body, version_id):
    return _read(server, core.tool_get_prompt_version, {'version_id': int(version_id)})


def clean_song_payload(body):
    """Validate a save request; returns the five song fields."""
    if not isinstance(body, dict):
        raise ApiError(400, 'invalid_body')
    values = {}
    for field in SONG_FIELDS:
        value = body.get(field, '')
        if not isinstance(value, str):
            raise ApiError(400, 'invalid_field', {'field': field})
        values[field] = value
    if values['status'] not in ws.SONG_STATUS_KEYS:
        raise ApiError(400, 'invalid_status')
    for field, limit in TEXT_LIMITS.items():
        if len(values[field]) > limit:
            raise ApiError(400, 'too_long', {'field': field, 'limit': limit})
    return values


def api_save_song(server, query, body, song_id):
    """Save like the desktop's „Song speichern“; refuses if the song changed meanwhile."""
    values = clean_song_payload(body)
    expected = body.get('expected')
    try:
        with closing(core.open_write(server.db_path)) as con:
            row = con.execute('SELECT status,distributor,platforms,style,lyrics FROM songs WHERE id=?',
                              (int(song_id),)).fetchone()
            if row is None:
                raise ApiError(404, 'song_missing')
            current = {field: row[field] or '' for field in SONG_FIELDS}
            if isinstance(expected, dict) and any((expected.get(f) or '') != current[f] for f in SONG_FIELDS):
                raise ApiError(409, 'conflict', {'current': current})
            archived = ws.save_song_record(con, int(song_id), values['status'], values['distributor'],
                                           values['platforms'], values['style'], values['lyrics'])
            if archived is None:
                raise ApiError(404, 'song_missing')
            return {'saved': True, 'archived': archived, 'song': core.tool_get_song(con, {'song_id': int(song_id)})}
    except core.ToolError as exc:
        raise ApiError(404, str(exc)) from exc
    except sqlite3.OperationalError as exc:  # e.g. database locked for longer than the timeout
        raise ApiError(503, 'database_busy', {'detail': str(exc)}) from exc


# --------------------------------------------------------------------------- Bands (stage 2)

def _write(server, func, *args):
    """Run a core write function; BandDataError -> 400/404/409 with a stable code."""
    try:
        with closing(core.open_write(server.db_path)) as con:
            return func(con, *args)
    except ws.BandDataError as exc:
        status = (404 if exc.code.endswith('_missing') else
                  409 if exc.code in ('preset_exists', 'band_exists', 'folder_exists') else
                  500 if exc.code == 'folder_error' else 400)
        raise ApiError(status, exc.code, exc.values) from exc
    except core.ToolError as exc:
        raise ApiError(404, str(exc)) from exc
    except sqlite3.IntegrityError as exc:  # e.g. the same band created at the same moment elsewhere
        raise ApiError(409, 'band_exists', {}) from exc
    except sqlite3.OperationalError as exc:
        raise ApiError(503, 'database_busy', {'detail': str(exc)}) from exc


def api_band_full(server, query, body, band_id):
    """Band detail plus instrument ids (for editing), genre catalog and personas."""
    def read(con, args):
        band = core.tool_get_band(con, args)
        band['instruments'] = ws.band_instruments(con, band['id'])
        band['genre_catalog'] = [r[0] for r in con.execute('SELECT name FROM genre_catalog ORDER BY name COLLATE NOCASE')]
        band['personas'] = list(ws.PERSONAS)
        return band
    return _read(server, read, {'band_id': int(band_id)})


def api_band_options(server, query, body):
    """Genre catalog and personas for the „Neue Band“ form."""
    return _read(server, lambda con, _args: {
        'genres': [r[0] for r in con.execute('SELECT name FROM genre_catalog ORDER BY name COLLATE NOCASE')],
        'personas': list(ws.PERSONAS)}, {})


def api_hardware_choices(server, query, body):
    category = query.get('category', [''])[0][:200]
    return _read(server, lambda con, _args: dict(zip(('groups', 'details'), ws.saved_hardware_choices(con, category))), {})


def api_presets(server, query, body):
    return _read(server, core.tool_list_hardware_presets, {})


def _body_text(body, key):
    if not isinstance(body, dict):
        raise ApiError(400, 'invalid_body')
    return body.get(key, '')


def api_create_band(server, query, body):
    """Create a band (folder + database + prompt folder) like the desktop „Band anlegen“."""
    import_existing = bool(isinstance(body, dict) and body.get('import_existing') is True)
    return _write(server, ws.create_band, _body_text(body, 'name'), _body_text(body, 'genre'),
                  _body_text(body, 'second_genre'), _body_text(body, 'persona') or 'Keep Current',
                  ws.band_root_directory(server.db_path.parent), import_existing)


def api_update_band(server, query, body, band_id):
    _write(server, ws.update_band_profile, int(band_id), _body_text(body, 'genre'),
           _body_text(body, 'second_genre'), _body_text(body, 'persona'))
    return api_band_full(server, query, None, band_id)


def api_add_instrument(server, query, body, band_id):
    new_id = _write(server, ws.add_instrument, int(band_id), _body_text(body, 'category'), _body_text(body, 'details'))
    return {'id': new_id}


def api_update_instrument(server, query, body, instrument_id):
    _write(server, ws.update_instrument, int(instrument_id), _body_text(body, 'category'), _body_text(body, 'details'))
    return {'saved': True}


def api_delete_instrument(server, query, body, instrument_id):
    _write(server, ws.delete_instrument, int(instrument_id))
    return {'deleted': True}


def api_save_preset(server, query, body, band_id):
    preset_id, count = _write(server, ws.save_band_hardware_as_preset, int(band_id), _body_text(body, 'name'),
                              bool(isinstance(body, dict) and body.get('overwrite') is True))
    return {'id': preset_id, 'count': count}


def api_transfer_preset(server, query, body, preset_id):
    mode = _body_text(body, 'mode')
    band_id = body.get('band_id') if isinstance(body, dict) else None
    if not isinstance(band_id, int):
        raise ApiError(400, 'invalid_field', {'field': 'band_id'})
    if mode == 'replace' and body.get('confirm') is not True:  # replacing hardware needs an explicit yes
        raise ApiError(400, 'confirm_required')
    return _write(server, ws.transfer_preset_to_band, int(preset_id), band_id, mode)


# --------------------------------------------------------------------------- AI Prompt Launcher (stage 4)

AI_JOBS_KEPT = 20
AI_PARSE_LIMIT = 60000  # pasted/imported AI answers


class AiJobs:
    """Background AI requests (API: up to 3 min, CLI: up to 5 min); the browser polls the result.

    One request at a time, like the desktop tab. API keys are used for the request only and
    never stored, logged or returned.
    """

    def __init__(self):
        self.lock = threading.Lock()
        self.jobs = {}

    def start(self, provider, func, secret='', finish=None, private=None):
        """``finish`` turns the worker's answer into the job result (default: split Style/Lyrics).
        ``private`` is kept server-side only (never returned by get)."""
        with self.lock:
            if any(job['status'] == 'running' for job in self.jobs.values()):
                raise ApiError(409, 'ai_busy')
            job_id = secrets.token_hex(8)
            self.jobs[job_id] = {'status': 'running', 'provider': provider, '_private': private or {}}
            finished = [k for k, job in self.jobs.items() if job['status'] != 'running']
            for old in finished[:max(0, len(self.jobs) - AI_JOBS_KEPT)]:
                del self.jobs[old]
        threading.Thread(target=self._run, args=(job_id, provider, func, secret, finish or self._split),
                         daemon=True).start()
        return job_id

    @staticmethod
    def _split(answer):
        try:
            style, lyrics = ws.extract_prompt(answer)
            return {'status': 'done', 'style': style, 'lyrics': lyrics}
        except ValueError:
            return {'status': 'failed', 'error': {'kind': 'split', 'code': '', 'detail': ''}}

    def _run(self, job_id, provider, func, secret, finish):
        try:
            result = finish(func())
        except ws.ProviderError as exc:
            result = {'status': 'failed', 'error': {'kind': exc.kind, 'code': exc.code, 'detail': exc.detail}}
        except Exception as exc:  # never let a worker thread take the server down
            ws.LOGGER.exception('MPW-Web: unerwarteter Fehler bei der KI-Anfrage')
            detail = str(exc).replace(secret, '***') if secret else str(exc)
            result = {'status': 'failed', 'error': {'kind': 'unexpected', 'code': '', 'detail': detail[:300]}}
        with self.lock:
            self.jobs[job_id].update(result)

    def get(self, job_id):
        with self.lock:
            job = self.jobs.get(job_id)
            return {k: v for k, v in job.items() if k != '_private'} if job else None

    def private(self, job_id):
        with self.lock:
            job = self.jobs.get(job_id)
            return (job['status'], job['_private'], job.get('clips') or []) if job else None


def _ai_provider(body):
    provider = _body_text(body, 'provider')
    if provider not in ws.AI_PROVIDERS:
        raise ApiError(400, 'invalid_provider')
    return provider


def _optional_int(body, key):
    value = body.get(key) if isinstance(body, dict) else None
    if value in (None, ''):
        return None
    if not isinstance(value, int) or isinstance(value, bool):
        raise ApiError(400, 'invalid_field', {'field': key})
    return value


def _ai_request_prompt(server, body):
    """The same Suno request the desktop tab builds (band, genres, persona, hardware, song idea)."""
    song_id = _optional_int(body, 'song_id')
    if song_id is None:
        raise ApiError(400, 'no_song')
    brief = _body_text(body, 'brief')
    if not isinstance(brief, str) or len(brief) > ws.BRIEF_LIMIT:
        raise ApiError(400, 'too_long' if isinstance(brief, str) else 'invalid_field', {'field': 'brief'})
    preset_id = _optional_int(body, 'preset_id')

    def build(con, _args):
        try:
            return ws.suno_prompt_request(con, song_id, preset_id, brief.strip())
        except ValueError as exc:
            if str(exc) == 'Song nicht gefunden.':
                raise ApiError(404, 'song_missing') from exc
            raise ApiError(400, 'prompt_error', {'detail': str(exc)}) from exc
    return _read(server, build, {})


def _provider_error(exc):
    return ApiError(400, 'provider', {'kind': exc.kind, 'code': exc.code, 'detail': exc.detail})


def api_ai_options(server, query, body):
    """Everything the launcher form needs; for API keys only *whether* the environment has one."""
    presets = _read(server, core.tool_list_hardware_presets, {})
    return {'providers': list(ws.AI_PROVIDERS), 'models': ws.AI_DEFAULT_MODELS,
            'cli_commands': ws.CLI_DEFAULT_COMMANDS, 'key_env': ws.API_KEY_ENV,
            'key_in_env': {p: bool(os.environ.get(env, '').strip()) for p, env in ws.API_KEY_ENV.items()},
            'platform_urls': ws.AI_PLATFORM_URLS,
            'error_texts': ws.AI_ERROR_TEXTS,  # same provider/CLI messages as the desktop tab
            'limits': {'style': ws.STYLE_LIMIT, 'lyrics': ws.LYRICS_LIMIT, 'brief': ws.BRIEF_LIMIT},
            'presets': [{'id': p['id'], 'name': p['name'], 'count': len(p['items'])}
                        for p in presets if isinstance(p, dict)]}


def api_ai_targets(server, query, body):
    """Projects of a band with their song entry (the AI target), like the desktop tab."""
    band = query.get('band_id', [''])[0]
    if not band.isdigit():
        raise ApiError(400, 'invalid_field', {'field': 'band_id'})
    return _read(server, lambda con, _args: [
        {'project_id': r[0], 'name': r[1], 'song_id': r[2]} for r in con.execute(
            'SELECT p.id, p.name, (SELECT s.id FROM songs s WHERE s.project_id=p.id ORDER BY s.id LIMIT 1) '
            'FROM projects p WHERE p.band_id=? ORDER BY p.name COLLATE NOCASE', (int(band),))], {})


def api_project_song(server, query, body, project_id):
    if not (isinstance(body, dict) and body.get('confirm') is True):  # creating a song entry needs a yes
        raise ApiError(400, 'confirm_required')
    song_id, created = _write(server, ws.ensure_project_song, int(project_id))
    return {'song_id': song_id, 'created': created}


def api_ai_generate(server, query, body):
    provider = _ai_provider(body)
    mode = _body_text(body, 'mode')
    prompt = _ai_request_prompt(server, body)
    if mode == 'api':
        model = _body_text(body, 'model')
        if not isinstance(model, str) or not ws.API_MODEL_PATTERN.fullmatch(model.strip()):
            raise ApiError(400, 'invalid_model')
        key = _body_text(body, 'api_key')
        if not isinstance(key, str) or len(key) > 500:
            raise ApiError(400, 'invalid_field', {'field': 'api_key'})
        key = key.strip() or os.environ.get(ws.API_KEY_ENV[provider], '').strip()
        if not key:
            raise ApiError(400, 'key_missing', {'env': ws.API_KEY_ENV[provider]})
        model = model.strip()
        job = server.ai_jobs.start(provider, lambda: ws.call_provider(provider, model, key, prompt), secret=key)
    elif mode == 'cli':
        command, model = _body_text(body, 'cli_command'), _body_text(body, 'model')
        if not isinstance(command, str) or not isinstance(model, str):
            raise ApiError(400, 'invalid_field', {'field': 'cli_command'})
        command = command.strip() or ws.CLI_DEFAULT_COMMANDS[provider]
        try:  # report a missing CLI at once instead of after a background run
            ws.resolve_cli_executable(provider, command)
        except ws.ProviderError as exc:
            raise _provider_error(exc) from exc
        cli_prompt = ws.ai_cli_prompt(prompt)
        job = server.ai_jobs.start(provider, lambda: ws.call_cli(provider, command, model.strip(), cli_prompt))
    else:
        raise ApiError(400, 'invalid_field', {'field': 'mode'})
    return {'job': job}


def api_ai_job(server, query, body, job_id):
    job = server.ai_jobs.get(job_id)
    if job is None:
        raise ApiError(404, 'job_missing')
    return job


def api_ai_check_cli(server, query, body):
    provider = _ai_provider(body)
    command = _body_text(body, 'cli_command')
    if not isinstance(command, str):
        raise ApiError(400, 'invalid_field', {'field': 'cli_command'})
    try:
        return {'path': ws.resolve_cli_executable(provider, command.strip() or ws.CLI_DEFAULT_COMMANDS[provider])}
    except ws.ProviderError as exc:
        raise _provider_error(exc) from exc


def api_ai_request_text(server, query, body):
    """Request text for the chat website (copy & paste); nothing is sent anywhere."""
    provider = _ai_provider(body)
    return {'text': ws.ai_browser_prompt(_ai_request_prompt(server, body)), 'url': ws.AI_PLATFORM_URLS[provider]}


def api_ai_parse(server, query, body):
    """Split an imported/pasted AI answer into Style and Lyrics (JSON or [STYLE]/[LYRICS])."""
    text = _body_text(body, 'text')
    if not isinstance(text, str) or len(text) > AI_PARSE_LIMIT:
        raise ApiError(400, 'too_long' if isinstance(text, str) else 'invalid_field', {'field': 'text'})
    try:
        style, lyrics = ws.extract_prompt(text)
    except ValueError as exc:
        raise ApiError(400, 'no_structure') from exc
    return {'style': style, 'lyrics': lyrics}


def api_save_prompt_version(server, query, body, song_id):
    """„Als neue Version speichern“: database version + TXT archive in the band's prompt folder."""
    if not isinstance(body, dict):
        raise ApiError(400, 'invalid_body')
    provider = _ai_provider(body)
    band_root = ws.band_root_directory(server.db_path.parent)

    def save(con, sid):
        version_id = ws.save_prompt_version(con, sid, provider, body.get('model', ''), body.get('style', ''),
                                            body.get('lyrics', ''), body.get('brief', ''))
        row = con.execute('SELECT style,lyrics FROM prompt_versions WHERE id=?', (version_id,)).fetchone()
        try:
            path = ws.save_prompt_text_file(con, sid, version_id, row[0], row[1], band_root)
            return {'id': version_id, 'file': str(path), 'file_error': None}
        except (OSError, ValueError) as exc:  # the version itself stays saved
            return {'id': version_id, 'file': None, 'file_error': str(exc)}
    return _write(server, save, int(song_id))


# --------------------------------------------------------------------------- An Suno senden (stage 5)

SUNO_URL_PATTERN = re.compile(r'^https://([a-z0-9-]+\.)*suno\.(com|ai)/', re.I)


def api_suno_info(server, query, body, song_id):
    """Saved prompts of the song (active prompt + versions) and the texts of the send dialog."""
    sid = int(song_id)

    def read(con, _args):
        row = con.execute('SELECT title FROM songs WHERE id=?', (sid,)).fetchone()
        if row is None:
            raise ApiError(404, 'song_missing')
        return {'title': row[0] or '', 'choices': ws.suno_prompt_choices(con, sid), 'limits': ws.SUNO_LIMITS,
                'texts': ws.SUNO_SEND_TEXTS, 'error_texts': ws.AI_ERROR_TEXTS}
    return _read(server, read, {})


def api_suno_send(server, query, body, song_id):
    """Send a *saved* prompt (read here from the database, never taken from the browser) to Suno.

    Spends Suno credits, so it needs ``confirm: true``; only one AI/Suno request runs at a time.
    """
    if not (isinstance(body, dict) and body.get('confirm') is True):
        raise ApiError(400, 'confirm_required')
    sid = int(song_id)
    version_id = _optional_int(body, 'version_id')
    title = _body_text(body, 'title')
    if not isinstance(title, str):
        raise ApiError(400, 'invalid_field', {'field': 'title'})
    choices = _read(server, lambda con, _args: ws.suno_prompt_choices(con, sid), {})
    if not choices:
        raise ApiError(404, 'song_missing')
    choice = next((c for c in choices if c['version_id'] == version_id), None)
    if choice is None:
        raise ApiError(404, 'version_missing')
    arguments = ws.suno_create_arguments(title, choice['style'], choice['lyrics'])
    problem = ws.suno_send_problem(arguments)
    if problem:
        raise ApiError(400, 'suno_' + problem)
    try:  # report a missing Claude Code at once
        ws.resolve_cli_executable('Claude', 'claude')
    except ws.ProviderError as exc:
        raise _provider_error(exc) from exc

    def finish(result):
        outcome = ws.suno_send_outcome(result, arguments)
        clips = [{**clip, 'url': clip['url'] if SUNO_URL_PATTERN.match(clip['url'] or '') else ''}
                 for clip in outcome['clips']]  # only real Suno links become clickable/storable
        return {'status': 'done', 'outcome': outcome['outcome'], 'values': outcome['values'],
                'notes': outcome['notes'], 'clips': clips}

    def run():
        try:
            return ws.call_suno_via_claude('claude', arguments)
        except ws.ProviderError as exc:  # shown as the dialog's own error texts
            return {'provider_error': (exc.kind, exc.code, exc.detail)}
    job = server.ai_jobs.start('Claude', run, finish=finish,
                               private={'song_id': sid, 'title': arguments['title'], 'kind': 'suno'})
    return {'job': job, 'title': arguments['title'], 'style': len(arguments.get('style', '')),
            'lyrics': len(arguments['lyrics'])}


def api_suno_links(server, query, body, song_id):
    """Store the links of a finished send with the song (only links Suno returned to this server)."""
    job_id = _body_text(body, 'job')
    found = server.ai_jobs.private(job_id) if isinstance(job_id, str) else None
    if found is None:
        raise ApiError(404, 'job_missing')
    status, private, clips = found
    if status != 'done' or private.get('kind') != 'suno' or private.get('song_id') != int(song_id):
        raise ApiError(400, 'invalid_field', {'field': 'job'})
    labels = ws.SUNO_SEND_TEXTS.get(ui_language_or(body), ws.SUNO_SEND_TEXTS['en'])['link_label']
    added = _write(server, ws.save_suno_links, int(song_id), private['title'], clips, labels)
    return {'added': added}


def ui_language_or(body):
    lang = body.get('lang') if isinstance(body, dict) else None
    return lang if lang in LANGUAGES else 'de'


# --------------------------------------------------------------------------- KI-Verbindungen (stage 6)

def api_connections_info(server, query, body):
    """Texts, links and the AI CLIs of the KI-Verbindungen page (same as the desktop window)."""
    return {'texts': ws.AI_CONNECTION_TEXTS, 'links': ws.AI_CONNECTION_LINKS,
            'clients': [{'id': c, 'name': ws.MCP_CLIENT_NAMES[c]} for c in ws.MCP_CLIENTS],
            'providers': list(ws.API_KEY_ENV), 'hosts': list(ws.AI_CONNECTION_TLS_HOSTS),
            'windows': sys.platform.startswith('win')}


def api_connections_check(server, query, body):
    """Read-only status check in the background (CLIs, sign-in, keys set yes/no, MCP, TLS)."""
    def finish(result):
        lines, intercepted = ws.ai_connection_status(result)
        return {'status': 'done', 'lines': lines, 'intercepted': intercepted}
    return {'job': server.check_jobs.start('check', ws.check_ai_connections, finish=finish)}


def api_connections_job(server, query, body, job_id):
    job = server.check_jobs.get(job_id)
    if job is None:
        raise ApiError(404, 'job_missing')
    return job


def _connection_client(body):
    client = _body_text(body, 'client')
    if client not in ws.MCP_CLIENTS:
        raise ApiError(400, 'invalid_field', {'field': 'client'})
    exe = ws.find_cli(client)
    if not exe:
        raise ApiError(400, 'need_cli', {'name': ws.MCP_CLIENT_NAMES[client]})
    return client, exe


def api_connections_setup(server, query, body):
    """Add/remove the MPW (read-only) or Suno MCP server for one AI CLI – only after a yes."""
    if not (isinstance(body, dict) and body.get('confirm') is True):  # changes the user's AI set-up
        raise ApiError(400, 'confirm_required')
    target, action = _body_text(body, 'server'), _body_text(body, 'action')
    if target not in ('mpw', 'suno') or action not in ('add', 'remove'):
        raise ApiError(400, 'invalid_field', {'field': 'server'})
    client, exe = _connection_client(body)
    command = None
    if target == 'mpw' and action == 'add':
        command = ws.mpw_mcp_server_command()
        if not Path(command[-1]).is_file():
            raise ApiError(400, 'mcp_exe_missing', {'path': command[-1]})
    code, text = ws.run_helper_tool(ws.mcp_setup_command(client, action, target, exe, command),
                                    timeout=120, cwd=str(Path.home()))
    if code != 0:
        ws.LOGGER.error('KI-Verbindung (Browser): Befehl fehlgeschlagen (%s): %s', code, text)
    return {'ok': code == 0, 'detail': (text or str(code))[-600:] if code != 0 else ''}


def api_connections_login(server, query, body):
    """Interactive sign-in (Claude Code, or Suno for one AI CLI) in its own console window.

    Only on Windows a console can be opened for the user; elsewhere the command is returned
    so it can be run in a terminal.
    """
    target = _body_text(body, 'target')
    if target == 'claude':
        exe = ws.find_cli('claude')
        if not exe:
            raise ApiError(400, 'need_claude')
        args, message = [exe, 'auth', 'login'], 'login_started'
    elif target == 'suno':
        client, exe = _connection_client(body)
        args, message = ws.mcp_login_console_command(client, exe), f'suno_login_started_{client}'
    else:
        raise ApiError(400, 'invalid_field', {'field': 'target'})
    if not sys.platform.startswith('win'):
        import shlex
        return {'started': False, 'command': ' '.join(shlex.quote(a) for a in args), 'message': message}
    try:
        import subprocess
        subprocess.Popen(args, cwd=str(Path.home()), creationflags=getattr(subprocess, 'CREATE_NEW_CONSOLE', 0))
    except OSError as exc:
        return {'started': False, 'error': str(exc)}
    return {'started': True, 'message': message}


def api_connections_desktop_config(server, query, body):
    """JSON block for Claude Desktop (read-only MPW server); the browser copies it."""
    return {'text': ws.claude_desktop_config_snippet(ws.mpw_mcp_server_command())}


ROUTES = [
    ('GET', re.compile(r'^/api/connections$'), api_connections_info),
    ('POST', re.compile(r'^/api/connections/check$'), api_connections_check),
    ('GET', re.compile(r'^/api/connections/jobs/([0-9a-f]{16})$'), api_connections_job),
    ('POST', re.compile(r'^/api/connections/setup$'), api_connections_setup),
    ('POST', re.compile(r'^/api/connections/login$'), api_connections_login),
    ('GET', re.compile(r'^/api/connections/desktop-config$'), api_connections_desktop_config),
    ('GET', re.compile(r'^/api/songs/(\d+)/suno$'), api_suno_info),
    ('POST', re.compile(r'^/api/songs/(\d+)/suno/send$'), api_suno_send),
    ('POST', re.compile(r'^/api/songs/(\d+)/suno/links$'), api_suno_links),
    ('GET', re.compile(r'^/api/ai/options$'), api_ai_options),
    ('GET', re.compile(r'^/api/ai/targets$'), api_ai_targets),
    ('GET', re.compile(r'^/api/ai/jobs/([0-9a-f]{16})$'), api_ai_job),
    ('POST', re.compile(r'^/api/projects/(\d+)/song$'), api_project_song),
    ('POST', re.compile(r'^/api/ai/generate$'), api_ai_generate),
    ('POST', re.compile(r'^/api/ai/check-cli$'), api_ai_check_cli),
    ('POST', re.compile(r'^/api/ai/request-text$'), api_ai_request_text),
    ('POST', re.compile(r'^/api/ai/parse$'), api_ai_parse),
    ('POST', re.compile(r'^/api/songs/(\d+)/prompt-versions$'), api_save_prompt_version),
    ('GET', re.compile(r'^/api/bands/(\d+)/full$'), api_band_full),
    ('GET', re.compile(r'^/api/hardware/choices$'), api_hardware_choices),
    ('GET', re.compile(r'^/api/band-options$'), api_band_options),
    ('GET', re.compile(r'^/api/presets$'), api_presets),
    ('POST', re.compile(r'^/api/bands$'), api_create_band),
    ('POST', re.compile(r'^/api/bands/(\d+)$'), api_update_band),
    ('POST', re.compile(r'^/api/bands/(\d+)/instruments$'), api_add_instrument),
    ('POST', re.compile(r'^/api/instruments/(\d+)$'), api_update_instrument),
    ('POST', re.compile(r'^/api/instruments/(\d+)/delete$'), api_delete_instrument),
    ('POST', re.compile(r'^/api/bands/(\d+)/presets$'), api_save_preset),
    ('POST', re.compile(r'^/api/presets/(\d+)/transfer$'), api_transfer_preset),
    ('GET', re.compile(r'^/api/info$'), api_info),
    ('GET', re.compile(r'^/api/bands$'), api_bands),
    ('GET', re.compile(r'^/api/bands/(\d+)$'), api_band),
    ('GET', re.compile(r'^/api/songs$'), api_songs),
    ('GET', re.compile(r'^/api/songs/(\d+)$'), api_song),
    ('GET', re.compile(r'^/api/songs/(\d+)/versions$'), api_versions),
    ('GET', re.compile(r'^/api/versions/(\d+)$'), api_version),
    ('POST', re.compile(r'^/api/songs/(\d+)$'), api_save_song),
]


# --------------------------------------------------------------------------- HTTP server

class MPWWebServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = False

    def __init__(self, db_path, port=0, token=None, static_dir=None):
        super().__init__(('127.0.0.1', port), MPWRequestHandler)
        self.db_path = Path(db_path)
        self.token = token or secrets.token_urlsafe(24)
        self.static_dir = Path(static_dir or web_directory())
        self.ai_jobs = AiJobs()
        self.check_jobs = AiJobs()  # KI-Verbindungen status checks (do not block prompt requests)

    @property
    def port(self):
        return self.server_address[1]

    @property
    def url(self):
        # Token in the fragment: never sent to the server, not in logs or Referer headers.
        return f'http://127.0.0.1:{self.port}/#t={self.token}'


class MPWRequestHandler(BaseHTTPRequestHandler):
    server_version = 'MPW-Web'
    sys_version = ''

    def log_message(self, fmt, *args):  # quiet console; errors are reported to the browser
        pass

    def do_GET(self):
        self._dispatch('GET')

    def do_POST(self):
        self._dispatch('POST')

    def _send(self, status, payload, content_type='application/json; charset=utf-8'):
        data = payload if isinstance(payload, bytes) else json.dumps(payload, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(data)))
        for key, value in SECURITY_HEADERS.items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(data)

    def _host_ok(self):
        port = self.server.port
        return self.headers.get('Host', '') in (f'127.0.0.1:{port}', f'localhost:{port}')

    def _token_ok(self):
        return hmac.compare_digest(self.headers.get('X-MPW-Token', ''), self.server.token)

    def _body(self):
        length = int(self.headers.get('Content-Length') or 0)
        if length > MAX_BODY:
            self.close_connection = True  # do not read a huge body; drop the connection after answering
            raise ApiError(413, 'too_large')
        # Always read the whole request first: answering early can make Windows reset the
        # connection, and the browser would see a network error instead of the message.
        raw = self.rfile.read(length)
        if not (self.headers.get('Content-Type') or '').startswith('application/json'):
            raise ApiError(415, 'json_required')
        try:
            return json.loads(raw.decode('utf-8') or '{}')
        except (ValueError, UnicodeDecodeError) as exc:
            raise ApiError(400, 'invalid_json') from exc

    def _dispatch(self, method):
        if not self._host_ok():
            return self._send(403, {'error': 'host_not_allowed'})
        parsed = urlparse(self.path)
        if method == 'GET' and parsed.path in STATIC_FILES:
            path = self.server.static_dir / STATIC_FILES[parsed.path]
            try:
                data = path.read_bytes()
            except OSError:
                return self._send(500, {'error': 'web_files_missing'})
            return self._send(200, data, CONTENT_TYPES[path.suffix])
        if not parsed.path.startswith('/api/'):
            return self._send(404, {'error': 'not_found'})
        if not self._token_ok():
            return self._send(403, {'error': 'token'})
        for route_method, pattern, handler in ROUTES:
            match = pattern.match(parsed.path)
            if match and route_method == method:
                try:
                    body = self._body() if method == 'POST' else None
                    result = handler(self.server, parse_qs(parsed.query), body, *match.groups())
                    return self._send(200, result)
                except ApiError as exc:
                    return self._send(exc.status, {'error': exc.message, **exc.extra})
                except Exception as exc:  # never let one request stop the server
                    ws.LOGGER.exception('MPW-Web: Fehler bei %s %s', method, parsed.path)
                    return self._send(500, {'error': 'internal', 'detail': str(exc)[:300]})
        return self._send(405 if any(p.match(parsed.path) for _, p, _ in ROUTES) else 404, {'error': 'not_found'})


# --------------------------------------------------------------------------- self-test and start

def _request(server, method, path, body=None, token=True, host=None):
    request = urllib.request.Request(f'http://127.0.0.1:{server.port}{path}', method=method,
                                     data=None if body is None else json.dumps(body).encode('utf-8'))
    if token:
        request.add_header('X-MPW-Token', server.token)
    if body is not None:
        request.add_header('Content-Type', 'application/json')
    if host:
        request.add_header('Host', host)
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return response.status, json.loads(response.read() or b'null')
    except urllib.error.HTTPError as exc:
        try:
            return exc.code, json.loads(exc.read() or b'null')
        finally:
            exc.close()


def run_self_test():
    """Start the server on a temporary database and exercise the API. Never touches user data."""
    results = []
    try:
        with tempfile.TemporaryDirectory(prefix='mpw_web_selftest_') as folder:
            root = Path(folder)
            with closing(ws.init_database(root)) as con:
                with con:
                    con.execute("INSERT INTO bands(name,genre) VALUES ('Testband','Blues')")
                    con.execute("INSERT INTO projects(band_id,name) VALUES (1,'Testprojekt')")
                    con.execute("INSERT INTO songs(project_id,title,style,lyrics) VALUES (1,'Testlied','alt','alt')")
            server = MPWWebServer(root / 'workstation.db')
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                assert _request(server, 'GET', '/api/info')[0] == 200
                assert _request(server, 'GET', '/api/info', token=False)[0] == 403
                assert _request(server, 'GET', '/api/info', host='evil.example:80')[0] == 403
                results.append('OK: Zugriffsschutz (Schlüssel, Host-Prüfung)')
                status, songs = _request(server, 'GET', '/api/songs')
                assert status == 200 and songs[0]['title'] == 'Testlied'
                results.append('OK: Songs lesen')
                save = {'status': 'Fertig', 'distributor': '', 'platforms': '', 'style': 'neu', 'lyrics': 'neu',
                        'expected': {'status': 'In Bearbeitung', 'distributor': '', 'platforms': '', 'style': 'alt', 'lyrics': 'alt'}}
                status, saved = _request(server, 'POST', '/api/songs/1', save)
                assert status == 200 and saved['archived'] is True and saved['song']['style'] == 'neu'
                assert _request(server, 'POST', '/api/songs/1', save)[0] == 409  # changed meanwhile
                results.append('OK: Song speichern mit Sicherungsversion und Konfliktschutz')
                for name in set(STATIC_FILES.values()):
                    assert (server.static_dir / name).is_file(), f'Web-Datei fehlt: {name}'
                results.append('OK: Web-Dateien vorhanden')
            finally:
                server.shutdown()
                server.server_close()
    except Exception as exc:
        for line in results:
            print(line)
        print(f'FEHLER: {type(exc).__name__}: {exc}', file=sys.stderr)
        return 1
    for line in results:
        print(line)
    print('MPW-Web-Selbsttest bestanden. Produktive MPW-Daten wurden nicht geöffnet.')
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description='MPW im Browser (lokal)')
    parser.add_argument('--port', type=int, default=0, help='fester Port (Standard: freier Port)')
    parser.add_argument('--no-browser', action='store_true', help='Browser nicht automatisch öffnen')
    parser.add_argument('--self-test', action='store_true', help='Selbsttest mit Temp-Daten')
    args = parser.parse_args(argv)
    if args.self_test:
        return run_self_test()
    # Same as the desktop app at start-up: create the database if missing, add new tables/columns
    # (additive only). On macOS/Linux the browser GUI is the only MPW program, so it must do this.
    created = not Path(ws.DB).is_file()
    try:
        with closing(ws.init_database(ws.ROOT)):
            pass
    except (OSError, sqlite3.Error, ImportError, ValueError) as exc:
        print(f'MPW-Datenbank konnte nicht geöffnet werden: {ws.DB}\n{exc}', file=sys.stderr)
        return 2
    if created:
        print(f'Neue MPW-Datenbank angelegt: {ws.DB}')
    try:
        server = MPWWebServer(ws.DB, port=args.port)
    except OSError as exc:
        print(f'MPW-Web konnte nicht starten (Port {args.port} belegt?): {exc}', file=sys.stderr)
        return 3
    print('MPW im Browser läuft.')
    print(f'  Adresse:   {server.url}')
    print(f'  Daten:     {ws.DB}')
    print('  Dieses Fenster offen lassen. Beenden: Fenster schließen oder Strg+C.')
    if not args.no_browser:
        webbrowser.open(server.url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == '__main__':
    sys.exit(main())
