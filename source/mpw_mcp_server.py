"""MPW MCP server: gives AI tools (Claude Code, Claude Desktop, Gemini CLI, Codex) access to MPW data.

Transport: MCP over stdio (newline-delimited JSON-RPC 2.0), implemented with the standard library
only. stdout carries protocol messages exclusively; diagnostics go to stderr.

Safety:
- Uses the same data root as MPW (portable Data folder, MPW_DATA_ROOT, registry/legacy config).
- Read-only by default: the database is opened with SQLite ``mode=ro`` per call and closed again.
- Never creates or migrates the database.
- Writing must be enabled explicitly (``--allow-write`` or ``MPW_MCP_ALLOW_WRITE=1``) and only ever
  adds a new prompt version (plus the usual TXT archive file). The active song prompt and existing
  versions are never changed or deleted.

Usage:
  MPW-MCP.exe                 start the server (normally launched by the AI tool)
  MPW-MCP.exe --allow-write   additionally offer the tool save_prompt_version
  MPW-MCP.exe --config        print setup commands for Claude Code, Gemini CLI, Codex, Claude Desktop
  MPW-MCP.exe --self-test     test against a temporary database; production data is not opened
"""
import html
import json
import os
import re
import sqlite3
import sys
import tempfile
from contextlib import closing
from pathlib import Path

import mpw_core as ws  # Qt-free MPW core: no PySide6 needed for the MCP server

SERVER_NAME = 'mpw'
SERVER_TITLE = 'Music Production Workstation'
SUPPORTED_PROTOCOLS = ('2025-11-25', '2025-06-18', '2025-03-26', '2024-11-05')
STYLE_LIMIT, LYRICS_LIMIT, BRIEF_LIMIT = 1000, 5000, 5000
MAX_LIMIT = 500

INSTRUCTIONS = (
    'Zugriff auf die Music Production Workstation (MPW) des Nutzers: Bands, Bandprofile mit Genres, '
    'Persona und Hardware, Projekte/Songs, aktive Suno-Prompts, gespeicherte Prompt-Versionen, '
    'Hardware-Presets und den Genre-Katalog. Suno-Limits: Style maximal 1000, Lyrics maximal 5000 Zeichen. '
    'Vor dem Schreiben eines neuen Prompts get_suno_briefing für den Song abrufen. '
    'save_prompt_version (falls verfügbar) legt nur eine neue Version an; der Nutzer übernimmt sie selbst in MPW.'
)


class ToolError(Exception):
    """Expected, user-facing tool failure (returned as isError result, not as protocol error)."""


def write_enabled(argv=None, env=None):
    argv = sys.argv if argv is None else argv
    env = os.environ if env is None else env
    return '--allow-write' in argv or str(env.get('MPW_MCP_ALLOW_WRITE', '')).strip().lower() in ('1', 'true', 'yes', 'ja')


# --------------------------------------------------------------------------- database access

def database_path():
    return ws.DB


def open_read(db=None):
    db = Path(db or database_path())
    if not db.is_file():
        raise ToolError(f'MPW-Datenbank nicht gefunden: {db}. MPW einmal starten oder Datenpfad prüfen.')
    con = sqlite3.connect(db.resolve().as_uri() + '?mode=ro', uri=True, timeout=5)
    con.row_factory = sqlite3.Row
    return con


def open_write(db=None):
    db = Path(db or database_path())
    if not db.is_file():  # never create a new database
        raise ToolError(f'MPW-Datenbank nicht gefunden: {db}.')
    con = sqlite3.connect(db, timeout=10)
    con.row_factory = sqlite3.Row
    con.execute('PRAGMA foreign_keys=ON')
    return con


def rows(cursor):
    return [dict(r) for r in cursor.fetchall()]


def table_exists(con, name):
    return con.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (name,)).fetchone() is not None


def html_to_text(value):
    text = re.sub(r'(?is)<(script|style).*?</\1>', '', value or '')
    text = re.sub(r'(?i)<br\s*/?>|</p>|</div>|</li>|</h[1-6]>', '\n', text)
    text = html.unescape(re.sub(r'<[^>]+>', '', text))
    return re.sub(r'\n{3,}', '\n\n', text).strip()


def limit_arg(args, default=100):
    value = args.get('limit', default)
    return max(1, min(int(value), MAX_LIMIT))


def find_band(con, args):
    if args.get('band_id') is not None:
        row = con.execute('SELECT * FROM bands WHERE id=?', (int(args['band_id']),)).fetchone()
    elif str(args.get('band_name') or '').strip():
        row = con.execute('SELECT * FROM bands WHERE name=? COLLATE NOCASE', (args['band_name'].strip(),)).fetchone()
    else:
        raise ToolError('band_id oder band_name angeben.')
    if row is None:
        raise ToolError('Band nicht gefunden. Mit list_bands die vorhandenen Bands abrufen.')
    return row


def song_row(con, song_id):
    row = con.execute(
        '''SELECT s.id, s.title, s.status, s.style, s.lyrics, s.distributor, s.platforms,
                  p.id AS project_id, p.name AS project, b.id AS band_id, b.name AS band
           FROM songs s JOIN projects p ON p.id=s.project_id JOIN bands b ON b.id=p.band_id
           WHERE s.id=?''', (int(song_id),)).fetchone()
    if row is None:
        raise ToolError('Song nicht gefunden. Mit list_songs die vorhandenen Songs abrufen.')
    return row


# --------------------------------------------------------------------------- read tools

def tool_list_bands(con, args):
    return rows(con.execute(
        '''SELECT b.id, b.name, b.genre, b.second_genre, b.persona,
                  (SELECT COUNT(*) FROM projects p WHERE p.band_id=b.id) AS projects,
                  (SELECT COUNT(*) FROM songs s JOIN projects p ON p.id=s.project_id WHERE p.band_id=b.id) AS songs
           FROM bands b ORDER BY b.name COLLATE NOCASE'''))


def tool_get_band(con, args):
    band = dict(find_band(con, args))
    band['instruments'] = rows(con.execute(
        'SELECT category, details FROM instruments WHERE band_id=? ORDER BY id', (band['id'],)))
    # projects.status is added by a later MPW migration; read-only access cannot migrate.
    has_status = any(r[1] == 'status' for r in con.execute('PRAGMA table_info(projects)'))
    status = 'p.status' if has_status else "'' AS status"
    band['projects'] = rows(con.execute(
        f'''SELECT p.id, p.name, {status}, s.id AS song_id, s.title AS song_title, s.status AS song_status
           FROM projects p LEFT JOIN songs s ON s.project_id=p.id
           WHERE p.band_id=? ORDER BY p.name COLLATE NOCASE, s.id''', (band['id'],)))
    return band


def tool_list_songs(con, args):
    sql = ['''SELECT s.id, s.title, s.status, b.id AS band_id, b.name AS band, p.name AS project,
                     length(s.style) AS style_chars, length(s.lyrics) AS lyrics_chars,
                     (SELECT COUNT(*) FROM prompt_versions v WHERE v.song_id=s.id) AS prompt_versions
              FROM songs s JOIN projects p ON p.id=s.project_id JOIN bands b ON b.id=p.band_id WHERE 1=1''']
    params = []
    if args.get('band_id') is not None or str(args.get('band_name') or '').strip():
        sql.append('AND b.id=?')
        params.append(find_band(con, args)['id'])
    if str(args.get('query') or '').strip():
        sql.append('AND (s.title LIKE ? OR p.name LIKE ?)')
        params += ['%' + args['query'].strip() + '%'] * 2
    if str(args.get('status') or '').strip():
        sql.append('AND s.status=?')
        params.append(args['status'].strip())
    sql.append('ORDER BY b.name COLLATE NOCASE, s.title COLLATE NOCASE LIMIT ?')
    params.append(limit_arg(args))
    return rows(con.execute(' '.join(sql), params))


def tool_get_song(con, args):
    song = dict(song_row(con, args['song_id']))
    song['style_chars'], song['lyrics_chars'] = len(song['style'] or ''), len(song['lyrics'] or '')
    info = con.execute('SELECT html FROM song_infos WHERE song_id=?', (song['id'],)).fetchone() \
        if table_exists(con, 'song_infos') else None
    song['notes'] = html_to_text(info['html']) if info else ''
    song['prompt_versions'] = con.execute('SELECT COUNT(*) FROM prompt_versions WHERE song_id=?',
                                          (song['id'],)).fetchone()[0]
    song['media'] = rows(con.execute('SELECT kind, COUNT(*) AS count FROM media_assets WHERE song_id=? GROUP BY kind',
                                     (song['id'],)))
    song['links'] = rows(con.execute('SELECT platform, url, label FROM media_links WHERE song_id=? ORDER BY id',
                                     (song['id'],)))
    song['releases'] = rows(con.execute(
        'SELECT id, distributor, release_date, submitted_date, isrc, upc FROM releases WHERE song_id=? ORDER BY id',
        (song['id'],)))
    if table_exists(con, 'mpw_song_genres'):
        song['genres'] = rows(con.execute(
            '''SELECT g.name, sg.role FROM mpw_song_genres sg JOIN mpw_subgenres g ON g.id=sg.sub_id
               WHERE sg.song_id=? ORDER BY sg.role, g.name''', (song['id'],)))
    return song


def tool_list_prompt_versions(con, args):
    song_row(con, args['song_id'])
    return rows(con.execute(
        '''SELECT id, provider, model, created_at, length(style) AS style_chars,
                  length(lyrics) AS lyrics_chars, brief
           FROM prompt_versions WHERE song_id=? ORDER BY id DESC LIMIT ?''',
        (int(args['song_id']), limit_arg(args, 50))))


def tool_get_prompt_version(con, args):
    row = con.execute(
        '''SELECT v.id, v.song_id, s.title AS song, v.provider, v.model, v.created_at, v.brief, v.style, v.lyrics
           FROM prompt_versions v JOIN songs s ON s.id=v.song_id WHERE v.id=?''',
        (int(args['version_id']),)).fetchone()
    if row is None:
        raise ToolError('Prompt-Version nicht gefunden.')
    return dict(row)


def tool_list_hardware_presets(con, args):
    result = []
    for row in con.execute('SELECT id, name, items_json, created_at FROM hardware_presets ORDER BY name COLLATE NOCASE'):
        try:
            items = json.loads(row['items_json'])
        except ValueError:
            items = []
        result.append({'id': row['id'], 'name': row['name'], 'created_at': row['created_at'],
                       'items': [{'category': c, 'details': d} for c, d in items
                                 if isinstance(c, str) and isinstance(d, str)] if isinstance(items, list) else []})
    return result


def tool_search_genres(con, args):
    query = str(args.get('query') or '').strip()
    limit = limit_arg(args, 50)
    if table_exists(con, 'mpw_subgenres'):
        return rows(con.execute(
            '''SELECT sg.name AS subgenre, group_concat(mg.name, ', ') AS main_genres
               FROM mpw_subgenres sg
               LEFT JOIN mpw_genre_relations r ON r.sub_id=sg.id
               LEFT JOIN mpw_main_genres mg ON mg.id=r.main_id
               WHERE sg.name LIKE ? OR mg.name LIKE ?
               GROUP BY sg.id ORDER BY sg.name COLLATE NOCASE LIMIT ?''',
            ('%' + query + '%', '%' + query + '%', limit)))
    return rows(con.execute('SELECT name FROM genre_catalog WHERE name LIKE ? ORDER BY name COLLATE NOCASE LIMIT ?',
                            ('%' + query + '%', limit)))


def tool_get_suno_briefing(con, args):
    song_row(con, args['song_id'])
    preset = args.get('hardware_preset_id')
    try:
        request = ws.suno_prompt_request(con, int(args['song_id']), None if preset is None else int(preset),
                                         str(args.get('song_idea') or '').strip())
    except ValueError as exc:
        raise ToolError(str(exc)) from exc
    return {'briefing': request, 'limits': {'style': STYLE_LIMIT, 'lyrics': LYRICS_LIMIT},
            'hint': 'Style und Lyrics getrennt erstellen. Mit save_prompt_version (falls aktiviert) als neue Version speichern.'}


# --------------------------------------------------------------------------- write tool

def prompt_band_root():
    """Band root folder of this MPW installation; the TXT archive uses MPW's own rules
    (mpw_core.save_prompt_text_file), so files look exactly like those saved in the GUI."""
    return ws.band_root_directory()


def clean_label(value, default, size=60):
    value = re.sub(r'[\x00-\x1f]', ' ', str(value or '')).strip()
    return (value or default)[:size]


def tool_save_prompt_version(con_unused, args, client='', db=None):
    style = str(args.get('style') or '').strip()
    lyrics = str(args.get('lyrics') or '').strip()
    brief = str(args.get('brief') or '').strip()
    if not style or not lyrics:
        raise ToolError('Style und Lyrics dürfen nicht leer sein.')
    if len(style) > STYLE_LIMIT or len(lyrics) > LYRICS_LIMIT:
        raise ToolError(f'Zeichenlimit überschritten: Style {len(style)}/{STYLE_LIMIT}, Lyrics {len(lyrics)}/{LYRICS_LIMIT}.')
    if len(brief) > BRIEF_LIMIT:
        raise ToolError(f'Songidee zu lang ({len(brief)}/{BRIEF_LIMIT} Zeichen).')
    provider = 'MCP'
    model = clean_label(args.get('model'), clean_label(client, 'KI-Werkzeug'))
    with closing(open_write(db)) as con:
        song = song_row(con, args['song_id'])
        with con:
            cursor = con.execute(
                'INSERT INTO prompt_versions(song_id,provider,model,style,lyrics,brief) VALUES(?,?,?,?,?,?)',
                (song['id'], provider, model, style, lyrics, brief))
            version_id = cursor.lastrowid
        result = {'version_id': version_id, 'song_id': song['id'], 'song': song['title'],
                  'provider': provider, 'model': model,
                  'hint': 'Neue Version gespeichert. Der aktive Song-Prompt bleibt unverändert; '
                          'Übernahme in MPW über „Version B in Song-Editor übernehmen“.'}
        try:
            result['archive_file'] = str(ws.save_prompt_text_file(con, song['id'], version_id, style, lyrics,
                                                                  prompt_band_root()))
        except (OSError, ValueError) as exc:
            result['archive_warning'] = f'TXT-Archivierung fehlgeschlagen: {exc}. Die Version bleibt gespeichert.'
    return result


# --------------------------------------------------------------------------- tool registry

def _schema(props=None, required=()):
    return {'type': 'object', 'properties': props or {}, 'required': list(required), 'additionalProperties': False}


INT = {'type': 'integer', 'minimum': 1}
LIMIT = {'type': 'integer', 'minimum': 1, 'maximum': MAX_LIMIT, 'description': 'Maximale Anzahl Einträge'}
BAND_SELECT = {'band_id': {**INT, 'description': 'ID der Band (aus list_bands)'},
               'band_name': {'type': 'string', 'description': 'Name der Band (alternativ zu band_id)'}}
READ_ONLY = {'readOnlyHint': True, 'destructiveHint': False, 'idempotentHint': True, 'openWorldHint': False}

READ_TOOLS = {
    'list_bands': (tool_list_bands, 'Bands auflisten',
                   'Alle Bands mit Haupt-/Zweitgenre, Persona und Anzahl Projekte/Songs.', _schema()),
    'get_band': (tool_get_band, 'Bandprofil abrufen',
                 'Bandprofil mit Genres, Persona, Instrumenten/Hardware und allen Projekten samt Song-IDs.',
                 _schema(BAND_SELECT)),
    'list_songs': (tool_list_songs, 'Songs auflisten',
                   'Songs mit Status, Band, Projekt, Länge des aktiven Prompts und Anzahl Prompt-Versionen. '
                   'Optional nach Band, Titel (query) oder Status filtern.',
                   _schema({**BAND_SELECT, 'query': {'type': 'string', 'description': 'Teil des Song-/Projekttitels'},
                            'status': {'type': 'string', 'description': 'Exakter Status, z. B. „In Bearbeitung“'},
                            'limit': LIMIT})),
    'get_song': (tool_get_song, 'Song abrufen',
                 'Song mit aktivem Suno-Prompt (Style, Lyrics), Notizen, Genres, Medienanzahl, Links und Releases.',
                 _schema({'song_id': INT}, ['song_id'])),
    'list_prompt_versions': (tool_list_prompt_versions, 'Prompt-Versionen auflisten',
                             'Gespeicherte Prompt-Versionen eines Songs, neueste zuerst (ohne Volltext).',
                             _schema({'song_id': INT, 'limit': LIMIT}, ['song_id'])),
    'get_prompt_version': (tool_get_prompt_version, 'Prompt-Version abrufen',
                           'Volltext (Style, Lyrics, Songidee) einer gespeicherten Prompt-Version.',
                           _schema({'version_id': INT}, ['version_id'])),
    'list_hardware_presets': (tool_list_hardware_presets, 'Hardware-Presets auflisten',
                              'Gespeicherte Hardware-Presets mit ihren Einträgen.', _schema()),
    'search_genres': (tool_search_genres, 'Genre-Katalog durchsuchen',
                      'Subgenres und zugehörige Hauptgenres aus dem MPW-Genre-Katalog suchen.',
                      _schema({'query': {'type': 'string', 'description': 'Suchbegriff, leer = alle'}, 'limit': LIMIT})),
    'get_suno_briefing': (tool_get_suno_briefing, 'Suno-Briefing erstellen',
                          'Dieselbe Anweisung, die der AI Prompt Launcher an die KI sendet: Band, Genres, Persona, '
                          'Hardware (Bandprofil oder Preset), Songidee und Suno-Regeln. Ändert nichts.',
                          _schema({'song_id': INT, 'song_idea': {'type': 'string', 'description': 'Songidee / Anweisung'},
                                   'hardware_preset_id': {**INT, 'description': 'Optional: Preset statt Bandprofil-Hardware'}},
                                  ['song_id'])),
}
WRITE_TOOLS = {
    'save_prompt_version': (tool_save_prompt_version, 'Prompt als neue Version speichern',
                            'Speichert Style und Lyrics als NEUE Prompt-Version des Songs (wie „Als neue Version speichern“ '
                            'im AI Prompt Launcher) inklusive TXT-Archivdatei. Der aktive Prompt und bestehende Versionen '
                            'bleiben unverändert. Limits: Style 1000, Lyrics 5000 Zeichen.',
                            _schema({'song_id': INT,
                                     'style': {'type': 'string', 'maxLength': STYLE_LIMIT},
                                     'lyrics': {'type': 'string', 'maxLength': LYRICS_LIMIT},
                                     'brief': {'type': 'string', 'maxLength': BRIEF_LIMIT, 'description': 'Songidee'},
                                     'model': {'type': 'string', 'description': 'Optional: verwendetes KI-Modell'}},
                                    ['song_id', 'style', 'lyrics'])),
}


def validate_arguments(schema, args):
    if not isinstance(args, dict):
        raise ToolError('arguments muss ein Objekt sein.')
    props = schema['properties']
    unknown = sorted(set(args) - set(props))
    if unknown:
        raise ToolError('Unbekannte Parameter: ' + ', '.join(unknown))
    missing = [k for k in schema['required'] if args.get(k) in (None, '')]
    if missing:
        raise ToolError('Fehlende Parameter: ' + ', '.join(missing))
    for key, value in args.items():
        if value is None:
            continue
        kind = props[key].get('type')
        if kind == 'integer' and (isinstance(value, bool) or not isinstance(value, int)):
            if isinstance(value, str) and value.strip().isdigit():
                args[key] = int(value.strip())
            else:
                raise ToolError(f'{key} muss eine Ganzzahl sein.')
        if kind == 'string' and not isinstance(value, str):
            raise ToolError(f'{key} muss ein Text sein.')
    return args


class MPWServer:
    def __init__(self, allow_write=False, db=None):
        self.allow_write = allow_write
        self.db = db
        self.client = ''
        self.tools = dict(READ_TOOLS)
        if allow_write:
            self.tools.update(WRITE_TOOLS)

    def tool_list(self):
        result = []
        for name, (_fn, title, description, schema) in self.tools.items():
            annotations = dict(READ_ONLY) if name in READ_TOOLS else {
                'readOnlyHint': False, 'destructiveHint': False, 'idempotentHint': False, 'openWorldHint': False}
            annotations['title'] = title
            result.append({'name': name, 'title': title, 'description': description,
                           'inputSchema': schema, 'annotations': annotations})
        return result

    def call_tool(self, name, args):
        if name not in self.tools:
            raise KeyError(name)
        fn, _title, _description, schema = self.tools[name]
        try:
            args = validate_arguments(schema, dict(args or {}))
            if name in WRITE_TOOLS:
                data = fn(None, args, client=self.client, db=self.db)
            else:
                with closing(open_read(self.db)) as con:
                    data = fn(con, args)
            text = json.dumps(data, ensure_ascii=False, indent=1, default=str)
            return {'content': [{'type': 'text', 'text': text}], 'isError': False}
        except ToolError as exc:
            return {'content': [{'type': 'text', 'text': str(exc)}], 'isError': True}
        except sqlite3.OperationalError as exc:
            hint = ' Die Datenbank ist gerade gesperrt (MPW speichert?). Bitte erneut versuchen.' \
                if 'locked' in str(exc).lower() or 'busy' in str(exc).lower() else ''
            return {'content': [{'type': 'text', 'text': f'Datenbankfehler: {exc}.{hint}'}], 'isError': True}
        except (sqlite3.Error, ValueError, TypeError) as exc:
            return {'content': [{'type': 'text', 'text': f'Fehler: {exc}'}], 'isError': True}

    # JSON-RPC ----------------------------------------------------------------
    def handle(self, message):
        """Return the response dict for one message, or None for notifications."""
        if not isinstance(message, dict) or message.get('jsonrpc') != '2.0':
            return _error(None, -32600, 'Invalid Request')
        method, msg_id = message.get('method'), message.get('id')
        is_request = 'id' in message
        if not isinstance(method, str):
            # Responses from the client (we never send requests) are ignored.
            return None if not is_request or 'result' in message or 'error' in message else _error(msg_id, -32600, 'Invalid Request')
        params = message.get('params') or {}
        if not is_request:
            return None  # notifications/initialized, notifications/cancelled, ...
        try:
            if method == 'initialize':
                requested = params.get('protocolVersion')
                version = requested if requested in SUPPORTED_PROTOCOLS else SUPPORTED_PROTOCOLS[0]
                info = params.get('clientInfo') or {}
                self.client = clean_label(info.get('name'), '')
                return _result(msg_id, {
                    'protocolVersion': version,
                    'capabilities': {'tools': {'listChanged': False}},
                    'serverInfo': {'name': SERVER_NAME, 'title': SERVER_TITLE, 'version': ws.APP_VERSION},
                    'instructions': INSTRUCTIONS + ('' if self.allow_write else ' Schreibzugriff ist ausgeschaltet.'),
                })
            if method == 'ping':
                return _result(msg_id, {})
            if method == 'tools/list':
                return _result(msg_id, {'tools': self.tool_list()})
            if method == 'tools/call':
                name = params.get('name')
                if not isinstance(name, str) or name not in self.tools:
                    return _error(msg_id, -32602, f'Unknown tool: {name}')
                return _result(msg_id, self.call_tool(name, params.get('arguments')))
            if method in ('resources/list', 'prompts/list'):
                return _result(msg_id, {method.split('/')[0]: []})
            return _error(msg_id, -32601, f'Method not found: {method}')
        except Exception as exc:  # never crash the server loop
            print(f'MPW-MCP: interner Fehler bei {method}: {exc!r}', file=sys.stderr)
            return _error(msg_id, -32603, 'Internal error')

    def handle_line(self, line):
        line = line.strip()
        if not line:
            return None
        try:
            message = json.loads(line)
        except ValueError:
            return _error(None, -32700, 'Parse error')
        if isinstance(message, list):  # JSON-RPC batch (protocol 2025-03-26)
            replies = [r for r in (self.handle(m) for m in message) if r is not None]
            return replies or None
        return self.handle(message)

    def serve(self, stdin=None, stdout=None):
        stdin = stdin or sys.stdin.buffer
        stdout = stdout or sys.stdout.buffer
        for raw in stdin:
            reply = self.handle_line(raw.decode('utf-8', 'replace'))
            if reply is not None:
                stdout.write(json.dumps(reply, ensure_ascii=False, separators=(',', ':')).encode('utf-8') + b'\n')
                stdout.flush()


def _result(msg_id, result):
    return {'jsonrpc': '2.0', 'id': msg_id, 'result': result}


def _error(msg_id, code, message):
    return {'jsonrpc': '2.0', 'id': msg_id, 'error': {'code': code, 'message': message}}


# --------------------------------------------------------------------------- setup help and self-test

def launch_command():
    if getattr(sys, 'frozen', False):
        return [str(Path(sys.executable).resolve())]
    return [str(Path(sys.executable).resolve()), str(Path(__file__).resolve())]


def config_text():
    cmd = launch_command()
    quoted = ' '.join(f'"{c}"' if ' ' in c else c for c in cmd)
    desktop = {'mcpServers': {SERVER_NAME: {'command': cmd[0], 'args': cmd[1:]}}}
    return '\n'.join([
        'MPW-MCP-Server einrichten (Datenbank: ' + str(database_path()) + ')',
        '',
        'Claude Code:',
        f'  claude mcp add --scope user {SERVER_NAME} -- {quoted}',
        'Gemini CLI:',
        f'  gemini mcp add --scope user {SERVER_NAME} {quoted}',
        'Codex CLI:',
        f'  codex mcp add {SERVER_NAME} -- {quoted}',
        '',
        'Claude Desktop (claude_desktop_config.json):',
        json.dumps(desktop, indent=2, ensure_ascii=False),
        '',
        'Schreibzugriff (neue Prompt-Versionen speichern): am Ende zusätzlich --allow-write anhängen.',
    ])


def run_self_test():
    results = []
    with tempfile.TemporaryDirectory(prefix='mpw_mcp_test_') as sandbox:
        root = Path(sandbox) / 'data'
        with closing(ws.init_database(root)) as con:
            con.execute("INSERT INTO bands(name,genre,persona) VALUES('MCP-Testband','Blues','Keep Current')")
            con.execute("INSERT INTO projects(band_id,name) VALUES(1,'Testsong')")
            con.execute("INSERT INTO songs(project_id,title,style,lyrics) VALUES(1,'Testsong','Blues','[Verse 1]')")
            con.execute("INSERT INTO instruments(band_id,category,details) VALUES(1,'Gitarre','Telecaster')")
            con.commit()
        db = root / 'workstation.db'
        before = db.read_bytes()
        server = MPWServer(allow_write=False, db=db)
        init = server.handle({'jsonrpc': '2.0', 'id': 1, 'method': 'initialize',
                              'params': {'protocolVersion': '2025-06-18', 'clientInfo': {'name': 'selftest'}}})
        assert init['result']['protocolVersion'] == '2025-06-18'
        names = {t['name'] for t in server.handle({'jsonrpc': '2.0', 'id': 2, 'method': 'tools/list'})['result']['tools']}
        assert names == set(READ_TOOLS), names
        results.append(f'OK: Initialisierung und {len(names)} Lese-Werkzeuge')

        def call(srv, name, **args):
            reply = srv.handle({'jsonrpc': '2.0', 'id': 3, 'method': 'tools/call',
                                'params': {'name': name, 'arguments': args}})['result']
            return reply['isError'], reply['content'][0]['text']

        err, text = call(server, 'get_band', band_name='mcp-testband')
        assert not err and 'Telecaster' in text, text
        err, text = call(server, 'get_suno_briefing', song_id=1, song_idea='Regen')
        assert not err and 'Songidee: Regen' in text, text
        err, text = call(server, 'get_song', song_id=99)
        assert err, text
        assert db.read_bytes() == before, 'Lesezugriff hat die Datenbank verändert'
        results.append('OK: Lesezugriff ändert die Datenbank nicht')

        writer = MPWServer(allow_write=True, db=db)
        writer.client = 'selftest'
        err, text = call(writer, 'save_prompt_version', song_id=1, style='x' * 1001, lyrics='y')
        assert err, text
        err, text = call(writer, 'save_prompt_version', song_id=1, style='Neuer Style', lyrics='Neue Lyrics')
        assert not err and '"version_id": 1' in text, text
        with closing(sqlite3.connect(db)) as check:
            assert check.execute('SELECT style FROM songs WHERE id=1').fetchone()[0] == 'Blues'
            assert check.execute('SELECT provider, model FROM prompt_versions').fetchall() == [('MCP', 'selftest')]
        results.append('OK: Schreiben legt nur eine neue Version an; aktiver Prompt bleibt unverändert')
    for line in results:
        print(line, file=sys.stderr)
    print('MPW-MCP-Selbsttest bestanden. Produktive MPW-Daten wurden nicht geöffnet.', file=sys.stderr)
    return 0


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if '--self-test' in argv:
        return run_self_test()
    if '--config' in argv or '--help' in argv or '-h' in argv:
        print(config_text() if '--config' in argv else __doc__)
        return 0
    allow = write_enabled(argv)
    print(f'MPW-MCP-Server gestartet · Datenbank: {database_path()} · '
          f'Schreibzugriff: {"an" if allow else "aus"}', file=sys.stderr)
    try:
        MPWServer(allow_write=allow).serve()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == '__main__':
    sys.exit(main())
