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
        status = 404 if exc.code.endswith('_missing') else 409 if exc.code == 'preset_exists' else 400
        raise ApiError(status, exc.code, exc.values) from exc
    except core.ToolError as exc:
        raise ApiError(404, str(exc)) from exc
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


def api_hardware_choices(server, query, body):
    category = query.get('category', [''])[0][:200]
    return _read(server, lambda con, _args: dict(zip(('groups', 'details'), ws.saved_hardware_choices(con, category))), {})


def api_presets(server, query, body):
    return _read(server, core.tool_list_hardware_presets, {})


def _body_text(body, key):
    if not isinstance(body, dict):
        raise ApiError(400, 'invalid_body')
    return body.get(key, '')


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


ROUTES = [
    ('GET', re.compile(r'^/api/bands/(\d+)/full$'), api_band_full),
    ('GET', re.compile(r'^/api/hardware/choices$'), api_hardware_choices),
    ('GET', re.compile(r'^/api/presets$'), api_presets),
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
