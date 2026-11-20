"""MPW core logic without any GUI toolkit.

Data root, database schema, saving, backups, AI providers, AI command-line tools,
MCP set-up helpers and Suno sending. Used by the desktop app (workstation.py, PySide6),
the MCP server (mpw_mcp_server.py) and the browser GUI (mpw_web.py); runs on Windows,
macOS and Linux without PySide6.
"""
import math
import difflib
from collections import Counter
import logging
import traceback
from logging.handlers import RotatingFileHandler
import csv
import base64
import html
import mimetypes
import wave
import struct
from contextlib import closing
import hashlib
import json
import re
import urllib.request
import urllib.error
import ipaddress
import socket
import ssl
import os
import shutil
import sqlite3
import sys
import importlib.metadata
import platform
import subprocess
import tempfile
import zipfile
from datetime import date, datetime, timedelta
from pathlib import Path
from urllib.parse import urlparse


try:
    from mutagen import File as mutagen_file
except ImportError:
    mutagen_file = None


APP_VERSION = '2.2.0 Alpha 21 Preview 52 RC1'


LEGACY_ROOT = Path.home() / 'MusicProductionWorkstation'


def portable_root():
    """Recognize only a build-owned portable marker next to the bundled executable.

    Never consult the legacy registry/configuration in portable mode, including when
    the user launches App\\MPW.exe directly rather than the CMD launcher.
    """
    if not getattr(sys, 'frozen', False):
        return None
    return portable_root_for(Path(sys.executable).resolve())


PORTABLE_MARKER = '.mpw-portable-v2'


class TranslocatedError(RuntimeError):
    """macOS started the program from a hidden read-only copy (App Translocation)."""


def portable_root_for(exe):
    """Portable folder for an executable, or None. Layouts (same on all systems):

    <Portable>/App/<program>                                  Windows, Linux, macOS (plain binary)
    <Portable>/<Name>.app/Contents/MacOS/<program>            macOS app bundle
    <Portable>/App/<Name>.app/Contents/MacOS/<program>        macOS app bundle inside App/
    The build-owned marker file .mpw-portable-v2 in <Portable> decides; nothing else is guessed.
    """
    exe = Path(exe)
    if '/AppTranslocation/' in exe.as_posix():
        # Data would silently end up in the wrong place: refuse with a clear hint instead.
        raise TranslocatedError(
            'macOS hat MPW aus einem schreibgeschützten Zwischenordner gestartet (App Translocation). '
            'Bitte den MPW-Ordner aus „Downloads“ z. B. nach „Programme“ oder „Dokumente“ verschieben '
            'und die Quarantäne entfernen: xattr -dr com.apple.quarantine <MPW-Ordner>')
    parent = exe.parent
    candidates = []
    if parent.name.lower() == 'app':
        candidates.append(parent.parent)
    if parent.name == 'MacOS' and parent.parent.name == 'Contents' and parent.parent.parent.suffix == '.app':
        bundle_parent = parent.parent.parent.parent
        candidates.append(bundle_parent)
        if bundle_parent.name.lower() == 'app':
            candidates.append(bundle_parent.parent)
    for candidate in candidates:
        if (candidate / PORTABLE_MARKER).is_file():
            return candidate
    return None


def resolve_data_root():
    portable = portable_root()
    if portable is not None:
        data = (portable / 'Data').resolve()
        if not data.is_relative_to(portable.resolve()):
            raise RuntimeError('Unsicherer Portable-Datenpfad')
        # A link to a production data directory must never be followed.
        if data.is_symlink():
            raise RuntimeError('Portable-Data darf kein symbolischer Link sein')
        return data

    # An explicit environment override is retained for isolated source tests.
    override = os.environ.get('MPW_DATA_ROOT', '').strip()
    if override:
        return Path(override).expanduser().resolve()

    # Installed mode: preserve previous registry/config discovery unchanged.
    selected = None
    if os.name == 'nt':
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\MPW') as key:
                selected, _ = winreg.QueryValueEx(key, 'BandRoot')
        except (OSError, ValueError):
            pass
    if not selected:
        old_config = LEGACY_ROOT / 'app_configuration.json'
        try:
            data = json.loads(old_config.read_text(encoding='utf-8'))
            selected = data.get('band_root_directory') if isinstance(data, dict) else None
        except (OSError, ValueError, TypeError):
            pass
    if selected:
        folder = Path(selected).expanduser()
        if folder.is_dir():
            target = folder / 'MPW'
            if (target / 'workstation.db').is_file():
                return target
    return LEGACY_ROOT


ROOT = resolve_data_root()


DB = ROOT / 'workstation.db' 


LOG_DIR = ROOT / 'logs'


LOG_FILE = LOG_DIR / 'mpw_errors.log'


LOGGER = logging.getLogger('mpw')


def configure_error_logging():
    """Write bounded local error logs; no lyrics or other user content is logged intentionally."""
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        if not LOGGER.handlers:
            handler = RotatingFileHandler(LOG_FILE, maxBytes=2_000_000,
                                          backupCount=3, encoding='utf-8')
            handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s'))
            LOGGER.addHandler(handler)
        LOGGER.setLevel(logging.ERROR)
    except OSError:
        # Logging must never prevent the application from starting.
        pass


LYRICS = '[Intro]\n\n[Verse 1]\n\n[Chorus]\n\n[Verse 2]\n\n[Chorus]\n\n[Bridge]\n\n[Guitar Solo]\n\n[Chorus]\n\n[Outro]'


PLATFORMS = ['Spotify', 'Apple Music', 'Amazon Music', 'YouTube Music', 'Deezer', 'Tidal', 'SoundCloud', 'Bandcamp', 'Qobuz', 'YouTube', 'TikTok', 'Instagram/Facebook', 'Andere']


DISTRIBUTORS = ['DistroKid', 'TuneCore', 'CD Baby', 'LANDR', 'recordJet', 'iMusician', 'Ditto Music', 'Amuse', 'ONErpm', 'RouteNote', 'UnitedMasters', 'SoundCloud for Artists', 'Andere / eigener Distributor']


STATES = ['Geplant', 'Eingereicht', 'In Prüfung', 'Veröffentlicht', 'Fehlgeschlagen']


KINDS = {'Cover': {'.png', '.jpg', '.jpeg', '.webp', '.bmp'}, 'Audio': {'.mp3', '.wav', '.flac', '.m4a', '.ogg', '.aiff', '.aif', '.wma', '.aac', '.opus', '.mid', '.midi'}, 'Stem': {'.mp3', '.wav', '.flac', '.aiff', '.aif', '.m4a', '.ogg'}, 'Dokument': {'.pdf', '.txt', '.md', '.docx', '.doc', '.rtf', '.odt'}, 'Video': {'.mp4', '.mov', '.mkv', '.avi', '.webm', '.m4v'}}


SONG_MEDIA_FOLDERS = ('Cover', 'Audio', 'Dokumente', 'Video')


MEDIA_KIND_FOLDER = {'Cover': 'Cover', 'Audio': 'Audio', 'Stem': 'Audio', 'Dokument': 'Dokumente', 'Video': 'Video'}


def init_database(root=ROOT):
    root.mkdir(parents=True, exist_ok=True)
    (root / 'media').mkdir(exist_ok=True)
    con = sqlite3.connect(root / 'workstation.db')
    try:
        con.execute('PRAGMA foreign_keys=ON')
        con.executescript('''
        CREATE TABLE IF NOT EXISTS genre_catalog(name TEXT PRIMARY KEY COLLATE NOCASE);
        CREATE TABLE IF NOT EXISTS bands(id INTEGER PRIMARY KEY, name TEXT UNIQUE NOT NULL, genre TEXT, second_genre TEXT, persona TEXT);
        CREATE TABLE IF NOT EXISTS projects(id INTEGER PRIMARY KEY, band_id INTEGER REFERENCES bands(id), name TEXT, UNIQUE(band_id,name));
        CREATE TABLE IF NOT EXISTS instruments(id INTEGER PRIMARY KEY, band_id INTEGER REFERENCES bands(id), category TEXT, details TEXT);
        CREATE TABLE IF NOT EXISTS hardware_presets(id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE COLLATE NOCASE, items_json TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS songs(id INTEGER PRIMARY KEY, project_id INTEGER REFERENCES projects(id), title TEXT, status TEXT DEFAULT 'In Bearbeitung', distributor TEXT DEFAULT '', platforms TEXT DEFAULT '', style TEXT DEFAULT '', lyrics TEXT DEFAULT '');
        CREATE TABLE IF NOT EXISTS media_links(id INTEGER PRIMARY KEY, song_id INTEGER NOT NULL REFERENCES songs(id) ON DELETE CASCADE, platform TEXT NOT NULL, url TEXT NOT NULL, label TEXT NOT NULL DEFAULT '', UNIQUE(song_id,url));
        CREATE TABLE IF NOT EXISTS media_assets(id INTEGER PRIMARY KEY, song_id INTEGER NOT NULL REFERENCES songs(id) ON DELETE CASCADE, kind TEXT NOT NULL, label TEXT NOT NULL, relative_path TEXT NOT NULL UNIQUE, original_name TEXT NOT NULL, sha256 TEXT NOT NULL, bytes INTEGER NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS releases(id INTEGER PRIMARY KEY, song_id INTEGER NOT NULL REFERENCES songs(id) ON DELETE CASCADE, distributor TEXT NOT NULL, release_date TEXT, submitted_date TEXT, isrc TEXT, upc TEXT, distributor_id TEXT, notes TEXT, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS prompt_versions(id INTEGER PRIMARY KEY, song_id INTEGER NOT NULL REFERENCES songs(id) ON DELETE CASCADE, provider TEXT NOT NULL, model TEXT NOT NULL, style TEXT NOT NULL, lyrics TEXT NOT NULL, brief TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS release_platforms(id INTEGER PRIMARY KEY, release_id INTEGER NOT NULL REFERENCES releases(id) ON DELETE CASCADE, platform TEXT NOT NULL, status TEXT NOT NULL, url TEXT DEFAULT '', UNIQUE(release_id,platform));
        CREATE TABLE IF NOT EXISTS albums(id INTEGER PRIMARY KEY, title TEXT NOT NULL, artist TEXT DEFAULT '', cover_path TEXT DEFAULT '', created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS album_tracks(album_id INTEGER NOT NULL REFERENCES albums(id) ON DELETE CASCADE, song_id INTEGER NOT NULL REFERENCES songs(id) ON DELETE CASCADE, position INTEGER NOT NULL, PRIMARY KEY(album_id,song_id));
        CREATE TABLE IF NOT EXISTS song_infos(song_id INTEGER PRIMARY KEY REFERENCES songs(id) ON DELETE CASCADE, html TEXT NOT NULL DEFAULT '', updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS song_manual_checks(song_id INTEGER NOT NULL REFERENCES songs(id) ON DELETE CASCADE, check_key TEXT NOT NULL, completed INTEGER NOT NULL DEFAULT 0 CHECK(completed IN (0,1)), updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY(song_id,check_key));
        ''')
        # Additive migration: existing albums and tracks are never overwritten.
        album_columns = {row[1] for row in con.execute('PRAGMA table_info(albums)')}
        for name, definition in (
            ('release_date', "TEXT DEFAULT ''"),
            ('genre', "TEXT DEFAULT ''"),
            ('label', "TEXT DEFAULT ''"),
            ('upc', "TEXT DEFAULT ''"),
        ):
            if name not in album_columns:
                con.execute(f'ALTER TABLE albums ADD COLUMN {name} {definition}')
        project_columns = {row[1] for row in con.execute('PRAGMA table_info(projects)')}
        if 'status' not in project_columns:
            con.execute("ALTER TABLE projects ADD COLUMN status TEXT NOT NULL DEFAULT 'In Arbeit'")
        con.commit()
        from mpw_genre_upgrade import install as install_genre_catalog
        install_genre_catalog(con)
    except BaseException:
        # Never leak an open handle: on Windows it locks workstation.db and hides the real error.
        con.close()
        raise
    return con


SONG_STATUS_KEYS = ('In Bearbeitung', 'Fertig', 'Veröffentlicht')


def save_song_record(con, song_id, status, distributor, platforms, style, lyrics):
    """Save a song exactly like Songs & Suno does (desktop and browser GUI).

    Keeps the last active prompt as a recoverable version whenever it changes; both writes
    share one transaction, so a failed save leaves no partial history.
    Returns True if the previous prompt was archived, False if not, None if the song is gone.
    """
    with con:
        previous = con.execute('SELECT style,lyrics FROM songs WHERE id=?', (song_id,)).fetchone()
        if previous is None:
            return None
        old_style, old_lyrics = previous[0] or '', previous[1] or ''
        archived = (old_style, old_lyrics) != (style, lyrics) and bool(old_style or old_lyrics)
        if archived:
            con.execute(
                'INSERT INTO prompt_versions(song_id,provider,model,style,lyrics,brief) VALUES(?,?,?,?,?,?)',
                (song_id, 'MPW Sicherung', 'vor Song-Speicherung', old_style, old_lyrics,
                 'Automatische Sicherung des vorherigen aktiven Prompts vor dem Speichern in Songs & Suno'))
        con.execute('UPDATE songs SET status=?,distributor=?,platforms=?,style=?,lyrics=? WHERE id=?',
                    (status, distributor, platforms, style, lyrics, song_id))
    return archived


def preset_items_missing(existing, items):
    """Preset entries the band does not have yet (case/space-insensitive, no duplicates)."""
    seen = {((c or '').strip().casefold(), (d or '').strip().casefold()) for c, d in existing}
    missing = []
    for category, details in items:
        category, details = (category or '').strip(), (details or '').strip()
        key = (category.casefold(), details.casefold())
        if category and details and key not in seen:
            seen.add(key)
            missing.append((category, details))
    return missing


def saved_hardware_choices(con, category=None):
    """Menu values for the Bands tab: saved groups and hardware of all bands and presets.

    Returns (groups, details). If ``category`` names a saved group (case-insensitive),
    details are limited to that group; otherwise all saved details are returned.
    Read-only; duplicates differing only in case or surrounding spaces appear once.
    """
    pairs = [(c, d) for c, d in con.execute('SELECT category, details FROM instruments')]
    for (items_json,) in con.execute('SELECT items_json FROM hardware_presets'):
        try:
            items = json.loads(items_json)
        except (ValueError, TypeError):
            continue  # a damaged preset must not break the Bands tab
        if isinstance(items, list):
            pairs.extend(tuple(x) for x in items
                         if isinstance(x, list) and len(x) == 2 and all(isinstance(v, str) for v in x))

    def unique(values):
        seen = {}
        for value in values:
            text = (value or '').strip()
            if text and text.casefold() not in seen:
                seen[text.casefold()] = text
        return sorted(seen.values(), key=str.casefold)

    groups = unique(c for c, _ in pairs)
    wanted = (category or '').strip().casefold()
    if wanted and wanted in {g.casefold() for g in groups}:
        details = unique(d for c, d in pairs if (c or '').strip().casefold() == wanted)
    else:
        details = unique(d for _, d in pairs)
    return groups, details


def digest_file(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def safe_song_directory(con, root, song_id, band_root=None, create=False):
    """Shared project media directory. Never move or remove legacy song folders."""
    row = con.execute('SELECT p.name,b.name FROM songs s '
                      'JOIN projects p ON p.id=s.project_id '
                      'JOIN bands b ON b.id=p.band_id WHERE s.id=?', (song_id,)).fetchone()
    if row is None:
        raise ValueError('Song oder Projekt nicht gefunden.')
    project_name, band_name = row
    base = Path(band_root) if band_root else Path(root) / 'Bands'
    parent = base
    for name in (band_name, project_name):
        if not parent.is_dir():
            if not create: return None
            parent.mkdir(parents=True, exist_ok=True)
        matches = [e for e in parent.iterdir() if e.name.casefold() == name.casefold()]
        if len(matches) > 1: raise OSError(f'Mehrdeutiger Ordnername: {name}')
        if matches:
            child = matches[0]
            if not child.is_dir() or child.is_symlink():
                raise OSError(f'Kein sicherer Ordner: {child}')
        else:
            if not create: return None
            child = parent / name
            child.mkdir(exist_ok=True)
        parent = child
    if create:
        for name in SONG_MEDIA_FOLDERS:
            matches = [e for e in parent.iterdir() if e.name.casefold() == name.casefold()]
            if len(matches) > 1: raise OSError(f'Mehrdeutiger Medienordner: {name}')
            target = matches[0] if matches else parent / name
            if target.is_symlink() or (target.exists() and not target.is_dir()):
                raise OSError(f'Medienordner ist nicht sicher: {target}')
            target.mkdir(exist_ok=True)
    return parent


def legacy_song_directory(con, root, song_id, band_root=None):
    """Find a former per-song directory read-only, for backward compatibility."""
    project = safe_song_directory(con, root, song_id, band_root, create=False)
    if project is None: return None
    row = con.execute('SELECT title FROM songs WHERE id=?', (song_id,)).fetchone()
    if not row: return None
    title = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', row[0]).strip(' .')[:90].rstrip(' .') or 'Song'
    name = f'{title} [Song-{song_id}]'
    matches = [e for e in project.iterdir() if e.name.casefold() == name.casefold()]
    return matches[0] if len(matches) == 1 and matches[0].is_dir() and not matches[0].is_symlink() else None


PROJECT_SORT_IMAGE_EXTENSIONS = KINDS['Cover'] | {'.gif', '.tif', '.tiff', '.heic', '.heif', '.avif', '.svg'}


PROJECT_SORT_AUDIO_EXTENSIONS = KINDS['Audio'] | KINDS['Stem'] | {'.alac', '.ape', '.dsf', '.dff', '.caf', '.w64', '.bwf'}


PROJECT_SORT_VIDEO_EXTENSIONS = KINDS['Video'] | {'.mpeg', '.mpg', '.wmv', '.flv', '.mts', '.m2ts', '.3gp', '.ts'}


def plan_project_media_sort(con, band_root):
    """Only top-level project files; never touch existing subdirectories or folder icons."""
    plan, skipped = [], []
    root = Path(band_root)
    for band, project in con.execute('SELECT b.name,p.name FROM projects p JOIN bands b ON b.id=p.band_id ORDER BY b.name,p.name'):
        parent = root
        for name in (band, project):
            if not parent.is_dir() or parent.is_symlink():
                parent = None; break
            matches = [x for x in parent.iterdir() if x.name.casefold() == name.casefold()]
            if len(matches) != 1 or not matches[0].is_dir() or matches[0].is_symlink():
                parent = None; break
            parent = matches[0]
        if parent is None: continue
        for source in sorted(parent.iterdir(), key=lambda p:p.name.casefold()):
            if source.is_symlink() or not source.is_file(): continue
            # Windows Explorer folder artwork and metadata are strictly protected.
            if source.stem.casefold() == 'folder' or source.name.casefold() in {'desktop.ini', 'thumbs.db'} or source.suffix.casefold() == '.ico':
                skipped.append((source, 'Geschütztes Ordnersymbol / folder-Datei'))
                continue
            ext = source.suffix.casefold()
            if ext in PROJECT_SORT_IMAGE_EXTENSIONS: folder = 'Bilder'
            elif ext in PROJECT_SORT_AUDIO_EXTENSIONS: folder = 'Audio'
            elif ext in PROJECT_SORT_VIDEO_EXTENSIONS: folder = 'Video'
            else: continue
            target_dir = parent / folder
            if target_dir.is_symlink() or (target_dir.exists() and not target_dir.is_dir()):
                skipped.append((source, f'Unsicherer Zielordner: {target_dir}'))
                continue
            target = target_dir / source.name
            if target.exists():
                skipped.append((source, f'Zieldatei existiert bereits: {target}'))
                continue
            plan.append((source, target))
    return plan, skipped


def execute_project_media_sort(plan):
    """Verify each copy before removing the source; never overwrite or delete folders."""
    moved, errors = [], []
    for source, target in plan:
        temporary = None
        try:
            if source.is_symlink() or not source.is_file(): raise OSError('Quelle fehlt oder ist ein Link')
            if source.stem.casefold() == 'folder' or source.name.casefold() in {'desktop.ini', 'thumbs.db'} or source.suffix.casefold() == '.ico':
                raise OSError('Geschützte Ordnersymbol-Datei')
            if target.exists() or target.is_symlink(): raise FileExistsError('Ziel existiert bereits')
            if target.parent.is_symlink() or (target.parent.exists() and not target.parent.is_dir()):
                raise OSError('Unsicherer Zielordner')
            target.parent.mkdir(exist_ok=True)
            import uuid
            temporary = target.parent / ('.mpw-sort-' + uuid.uuid4().hex + '.tmp')
            shutil.copy2(source, temporary)
            if digest_file(source) != digest_file(temporary): raise OSError('SHA-256 stimmt nicht überein')
            # Exclusive creation prevents overwriting a file added since the preview.
            with temporary.open('rb') as read, target.open('xb') as write:
                shutil.copyfileobj(read, write, 1024*1024)
            if digest_file(source) != digest_file(target):
                target.unlink()
                raise OSError('Zieldatei konnte nicht verifiziert werden')
            source.unlink()
            moved.append((source,target))
        except Exception as exc:
            errors.append((source,str(exc)))
        finally:
            if temporary is not None:
                try: temporary.unlink(missing_ok=True)
                except OSError: pass
    return moved, errors


def plan_legacy_audio_migration(con, band_root):
    """Plan all audio files in legacy project/Musik, once per project."""
    plan, skipped = [], []
    rows = con.execute('SELECT p.id,p.name,b.name FROM projects p JOIN bands b ON b.id=p.band_id ORDER BY b.name,p.name').fetchall()
    for project_id, project_name, band_name in rows:
        base = Path(band_root)
        for part in (band_name, project_name, 'Musik'):
            if not base.is_dir(): base = None; break
            matches = [x for x in base.iterdir() if x.name.casefold() == part.casefold()]
            if len(matches) != 1 or not matches[0].is_dir() or matches[0].is_symlink():
                base = None; break
            base = matches[0]
        if base is None: continue
        songs = con.execute('SELECT id FROM songs WHERE project_id=? ORDER BY id',(project_id,)).fetchall()
        for path in sorted(base.rglob('*')):
            if path.is_symlink() or not path.is_file() or path.suffix.lower() not in (KINDS['Audio'] | KINDS['Stem']):
                continue
            if any(part.is_symlink() for part in path.parents if part != base and base in part.parents):
                skipped.append((str(path), 'Symbolischer Unterordner')); continue
            if not songs:
                skipped.append((str(path), 'Projekt hat keinen Song als Ziel')); continue
            # A single song ID is enough to resolve the shared project Audio folder.
            plan.append((path,(songs[0][0],),band_name,project_name))
    return plan, skipped


def migrate_legacy_audio_files(con, root, band_root, plan, move=False):
    """Copy to all chosen songs; remove source only after every target verifies."""
    copied, errors = [], []
    for source, song_ids, band, project in plan:
        try:
            if not source.is_file() or source.is_symlink():
                raise OSError('Quelle fehlt oder ist ein symbolischer Link')
            source_hash = digest_file(source)
            results = []
            all_verified = True
            for sid in song_ids:
                try:
                    target_folder = safe_song_directory(con,root,sid,band_root,create=True) / 'Audio'
                    if target_folder.is_symlink(): raise OSError('Zielordner ist ein symbolischer Link')
                    # Preserve nested folders relative to the old Musik directory.
                    # This prevents identically named files in different subfolders
                    # from being collapsed into one flat destination.
                    old_music = source
                    while old_music.name.casefold() != 'musik' and old_music != old_music.parent:
                        old_music = old_music.parent
                    if old_music.name.casefold() != 'musik':
                        raise OSError('Alter Musik-Stammordner nicht gefunden')
                    relative = source.relative_to(old_music)
                    target_folder = target_folder.joinpath(*relative.parts[:-1])
                    if target_folder.exists() and (target_folder.is_symlink() or not target_folder.is_dir()):
                        raise OSError('Unsicherer Ziel-Unterordner')
                    # Never follow existing symlinks in nested target folders.
                    parent = target_folder
                    while parent != parent.parent:
                        if parent.is_symlink(): raise OSError('Symbolischer Ziel-Unterordner')
                        if parent == safe_song_directory(con,root,sid,band_root,create=False): break
                        parent = parent.parent
                    target_folder.mkdir(parents=True,exist_ok=True)
                    target = target_folder / source.name
                    if target.exists():
                        if target.is_file() and not target.is_symlink() and digest_file(target) == source_hash:
                            results.append((source,target,'bereits vorhanden (identisch)'))
                            continue
                        index=2
                        while target.exists():
                            target=target_folder / f'{source.stem} ({index}){source.suffix}'
                            index+=1
                    try:
                        with source.open('rb') as inp, target.open('xb') as out:
                            shutil.copyfileobj(inp,out,1024*1024)
                        if digest_file(target) != source_hash:
                            raise OSError('Prüfsumme stimmt nicht überein')
                    except Exception:
                        if target.exists(): target.unlink()
                        raise
                    results.append((source,target,'kopiert'))
                except Exception as exc:
                    all_verified = False
                    errors.append((str(source),f'Song-ID {sid}: {exc}'))
            copied.extend(results)
            if move and all_verified and len(results) == len(song_ids):
                source.unlink()
                copied.append((source,source,'Quelle nach vollständiger Prüfung entfernt'))
        except Exception as exc:
            errors.append((str(source),str(exc)))
    return copied, errors


def filesystem_song_assets(con, root, song_id, band_root=None):
    """Read shared project media and the song's former individual folders."""
    project = safe_song_directory(con, root, song_id, band_root, create=False)
    legacy = legacy_song_directory(con, root, song_id, band_root)
    result, seen = [], set()
    for folder in (project, legacy):
        if folder is None: continue
        for name in SONG_MEDIA_FOLDERS:
            sub = folder / name
            if not sub.is_dir() or sub.is_symlink(): continue
            for path in sorted(sub.iterdir(), key=lambda x: x.name.casefold()):
                if path.is_file() and not path.is_symlink() and str(path) not in seen:
                    seen.add(str(path))
                    kind = ('Cover' if name == 'Cover' else 'Audio' if name == 'Audio'
                            else 'Dokument' if name == 'Dokumente' else 'Video')
                    result.append((kind, path.stem, path.name, path.stat().st_size, str(path)))
    return result


# Windows Explorer folder icon from a cover image needs Qt image tools; the desktop app
# (workstation.py) installs its implementation here. Elsewhere no icon is set.
COVER_ICON_HOOK = None


def import_asset(con, root, song_id, kind, source, label, band_root=None):
    """Copy media to the song folder. Never store media blobs or new media index rows in SQLite."""
    source = Path(source)
    if kind not in KINDS or source.suffix.lower() not in KINDS[kind]:
        raise ValueError('Dateiformat passt nicht zur gewählten Kategorie.')
    if not source.is_file():
        raise FileNotFoundError(source)
    song_folder = safe_song_directory(con, root, song_id, band_root, create=True)
    folder = song_folder / MEDIA_KIND_FOLDER[kind]
    filename = source.name
    dest = folder / filename
    if dest.exists():
        if dest.is_file() and digest_file(dest) == digest_file(source):
            raise ValueError('Diese Datei ist bereits im Songordner vorhanden.')
        # Never overwrite an existing file, even if its name is identical.
        counter = 2
        while True:
            dest = folder / f'{source.stem} ({counter}){source.suffix}'
            if not dest.exists():
                break
            counter += 1
    shutil.copy2(source, dest)
    if kind == 'Cover' and COVER_ICON_HOOK is not None:
        try:
            COVER_ICON_HOOK(song_folder)
        except OSError as exc:
            LOGGER.error('Ordnersymbol konnte nicht gesetzt werden: %s', exc)
    return dest


def check_database_integrity(connection, *, include_foreign_keys=True):
    """Read-only SQLite integrity and referential checks; never repair or alter data."""
    results = [row[0] for row in connection.execute('PRAGMA integrity_check')]
    if results != ['ok']:
        details = '; '.join(str(item) for item in results[:8])
        raise ValueError('SQLite-Integritätsprüfung fehlgeschlagen: ' + details)
    violations = list(connection.execute('PRAGMA foreign_key_check')) if include_foreign_keys else []
    if violations:
        sample = '; '.join(f'{table} (Zeile {rowid}, Verweis {parent})'
                           for table, rowid, parent, _ in violations[:8])
        raise ValueError(f'{len(violations)} ungültige Fremdschlüssel gefunden: ' + sample)
    return 'SQLite integrity_check: OK; Fremdschlüssel: OK' if include_foreign_keys else 'SQLite integrity_check: OK'


def check_live_database_integrity(root):
    """Use an independent read-only connection, without creating or migrating a database."""
    db_path = Path(root) / 'workstation.db'
    if not db_path.is_file():
        raise FileNotFoundError(f'MPW-Datenbank nicht gefunden: {db_path}')
    with closing(sqlite3.connect(db_path.as_uri() + '?mode=ro', uri=True, timeout=15)) as connection:
        return check_database_integrity(connection)


def _write_backup_archive(con, root, destination):
    """Write a verified SQLite snapshot atomically; preserve an existing archive on error."""
    destination = Path(destination)
    if not destination.parent.is_dir():
        raise FileNotFoundError(f'Backup-Zielordner nicht gefunden: {destination.parent}')
    with tempfile.TemporaryDirectory() as tmp:
        snapshot = Path(tmp) / 'workstation.db'
        with closing(sqlite3.connect(snapshot)) as target:
            con.backup(target)
            check_database_integrity(target)
        # Temporary file is on the same volume as the final destination.
        with tempfile.NamedTemporaryFile(prefix='.mpw_backup_', suffix='.zip', dir=destination.parent, delete=False) as staged_file:
            staging = Path(staged_file.name)
        try:
            with zipfile.ZipFile(staging, 'w', zipfile.ZIP_DEFLATED, allowZip64=True) as archive:
                archive.write(snapshot, 'workstation.db')
                archive.writestr('backup_info.txt',
                    f'MPW database-only backup\nCreated: {datetime.now().isoformat()}\n'
                    'Media files and band/project directories are intentionally excluded.\n')
            validate_backup(staging)
            staging.replace(destination)
        finally:
            staging.unlink(missing_ok=True)
    return destination


def append_backup_log(destination, status, details):
    """Append-only audit trail, stored next to the backup (not inside it)."""
    destination = Path(destination)
    record = {'timestamp': datetime.now().isoformat(timespec='seconds'),
              'file': destination.name, 'status': status, 'details': str(details)}
    with (destination.parent / 'MPW_Backup_Pruefprotokoll.jsonl').open('a', encoding='utf-8') as log:
        log.write(json.dumps(record, ensure_ascii=False) + '\n')


def check_backup_free_space(root, destination):
    """Preflight: ensure the target drive has room before starting a backup.

    Audio is often already compressed, so assume near-uncompressed archive size.
    The check is conservative and does not write to the destination.
    """
    root, destination = Path(root), Path(destination)
    parent = destination.parent
    if not parent.is_dir():
        raise OSError(f'Backup-Zielordner nicht erreichbar: {parent}')
    source_bytes = 0
    db_path = root / 'workstation.db'
    if db_path.is_file():
        source_bytes += db_path.stat().st_size
    required = source_bytes + 100 * 1024 * 1024
    available = shutil.disk_usage(parent).free
    if available < required:
        raise OSError(
            'Nicht genügend freier Speicherplatz auf dem Backup-Laufwerk.\n'
            f'Verfügbar: {available / 1024**3:.2f} GiB; '
            f'geschätzter Mindestbedarf: {required / 1024**3:.2f} GiB.\n'
            'Es wurde kein neues Backup angelegt.')
    return available, required


def create_backup(con, root, destination):
    """Create, verify ZIP and SQLite, then record result in a persistent audit log."""
    destination = Path(destination)
    try:
        check_backup_free_space(root, destination)
        check_live_database_integrity(root)
        _write_backup_archive(con, root, destination)
        validate_backup(destination)
    except Exception as exc:
        try:
            append_backup_log(destination, 'FEHLER', exc)
        except OSError:
            pass  # Preserve the original failure, especially for unavailable drives.
        raise
    try:
        append_backup_log(destination, 'OK', 'ZIP und SQLite erfolgreich geprüft')
    except OSError as exc:
        # A verified backup is valid even if writing its auxiliary log fails.
        print(f'Warnung: Backup-Prüfprotokoll konnte nicht geschrieben werden: {exc}', file=sys.stderr)
    return destination


def validate_backup(archive_path):
    """Validate backup structure and SQLite integrity before touching live data."""
    archive_path = Path(archive_path)
    with zipfile.ZipFile(archive_path) as z:
        bad = z.testzip()
        if bad:
            raise ValueError(f'Beschädigte ZIP-Datei: {bad}')
        members = z.infolist()
        names = [m.filename for m in members if not m.is_dir()]
        if len(names) != len(set(names)) or 'workstation.db' not in names:
            raise ValueError('Backup enthält keine eindeutige workstation.db.')
        for m in members:
            path = Path(m.filename.replace('\\', '/'))
            if (path.is_absolute() or '..' in path.parts or
                not (m.filename == 'workstation.db' or m.filename == 'backup_info.txt' or m.filename.startswith('media/')) or
                (m.external_attr >> 16) & 0o170000 == 0o120000):
                raise ValueError('Backup enthält einen unzulässigen Dateipfad.')
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / 'workstation.db'
            with z.open('workstation.db') as source, db.open('wb') as target:
                shutil.copyfileobj(source, target)
            with closing(sqlite3.connect(db)) as con:
                check_database_integrity(con)
                tables = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
                if not {'bands','projects','songs','releases','media_assets'}.issubset(tables):
                    raise ValueError('Das Backup enthält keine gültige MPW-Datenbank.')
    return True


def restore_backup(archive_path, root):
    """Restore only the SQLite database; never alter band/project/media folders."""
    validate_backup(archive_path)
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    # Restoration must happen with MPW closed. WAL/SHM files may hold newer data.
    if any((root / name).exists() for name in ('workstation.db-wal', 'workstation.db-shm')):
        raise RuntimeError('Wiederherstellung abgebrochen: SQLite-WAL/SHM vorhanden. MPW schließen und Datenbank sicher prüfen.')
    with tempfile.TemporaryDirectory(dir=root.parent, prefix='mpw_restore_') as tmp:
        staging = Path(tmp) / 'workstation.db'
        with zipfile.ZipFile(archive_path) as archive:
            with archive.open('workstation.db') as source, staging.open('wb') as target:
                shutil.copyfileobj(source, target)
        existing = root / 'workstation.db'
        previous = Path(tmp) / 'previous.db'
        if existing.exists():
            existing.replace(previous)
        try:
            staging.replace(existing)
        except Exception:
            if previous.exists():
                previous.replace(existing)
            raise


def extract_prompt(text):
    """Accept JSON or MPW tagged output. Never run generated content as code."""
    candidate = text.strip()
    if candidate.startswith('```'):
        candidate = re.sub(r'^```(?:json)?\s*|\s*```$', '', candidate, flags=re.I).strip()
    try:
        obj = json.loads(candidate)
        if isinstance(obj, dict):
            return str(obj.get('style','')).strip(), str(obj.get('lyrics','')).strip()
    except (ValueError, TypeError):
        pass
    # Both the new editable template and older MPW responses are supported.
    # Closing markers are excluded from the actual Style/Lyrics values.
    style = re.search(r'\[STYLE\]\s*(.*?)(?=\[/STYLE\]|\[LYRICS\]|$)', text, re.S | re.I)
    lyrics = re.search(r'\[LYRICS\]\s*(.*?)(?=\[/LYRICS\]|\[END MPW\]|$)', text, re.S | re.I)
    if style and lyrics:
        return style.group(1).strip(), lyrics.group(1).strip()
    raise ValueError('Keine gültige Style/Lyrics-Struktur in der KI-Antwort erkannt.')


def suno_prompt_request(con, sid, preset_id=None, brief=''):
    """Assemble the Suno request for one song; shared by the GUI and the MCP server."""
    row = con.execute("""SELECT s.title,b.name,b.genre,b.second_genre,b.persona,b.id
                              FROM songs s JOIN projects p ON p.id=s.project_id
                              JOIN bands b ON b.id=p.band_id WHERE s.id=?""",(sid,)).fetchone()
    if not row: raise ValueError('Song nicht gefunden.')
    title,band,genre,secondary,persona,band_id = row
    instruments = con.execute('SELECT category,details FROM instruments WHERE band_id=?',(band_id,)).fetchall()
    hardware_source = 'Hardware des Bandprofils'
    if preset_id is not None:
        preset = con.execute('SELECT name,items_json FROM hardware_presets WHERE id=?', (preset_id,)).fetchone()
        if not preset:
            raise ValueError('Hardware-Preset nicht gefunden.')
        try:
            items = json.loads(preset[1])
            if not isinstance(items, list) or any(not isinstance(x, list) or len(x) != 2 or not all(isinstance(v,str) for v in x) for x in items):
                raise ValueError('Ungültige Preset-Daten.')
        except (ValueError, TypeError) as exc:
            raise ValueError(f'Hardware-Preset fehlerhaft: {exc}') from exc
        instruments = items
        hardware_source = 'Hardware-Preset: ' + preset[0]
    hardware = '\n'.join(f'{c}: {d}' for c,d in instruments)
    return f"""Erstelle einen vollständigen Suno-v6-Prompt. Antworte ausschließlich als JSON-Objekt mit den Schlüsseln "style" und "lyrics" (beide Strings). Keine Markdown-Codeblöcke.
Band: {band}
Song: {title}
Hauptgenre: {genre or ''}
Zweitgenre: {secondary or ''}
Persona: {persona or 'Keep Current'}
Instrumente und Hardware ({hardware_source}):
{hardware}
Songidee: {brief}
Regeln: Style maximal 1000 Zeichen, Lyrics maximal 5000 Zeichen. Bei Keep Current keine Stimmbeschreibungen oder Vocal-Anweisungen; Mikrofon-Hardware ist erlaubt. No reverb, no echo, no hall, no delay. Keine Behauptung, dass konkrete Hardware garantiert verwendet wird.
Lyric-Struktur: [Intro], [Verse 1], [Chorus], [Verse 2], [Chorus], [Bridge], [Guitar Solo], [Chorus], [Outro]. Die Lyrics sollen einen vollständigen Songtext enthalten."""


class ProviderError(RuntimeError):
    """API failure with a stable kind; the GUI localizes it (worker threads know no UI language).

    Kinds: auth, model, rate, bad_request, server, http, network, timeout, blocked,
    truncated, empty, format.
    """

    def __init__(self, kind, provider, code='', detail=''):
        super().__init__(f'{provider}: {kind} {code} {detail}'.strip())
        self.kind, self.provider, self.code, self.detail = kind, provider, str(code or ''), detail or ''


def _provider_error_detail(raw, api_key):
    """Short single-line provider message from an error body; never echoes the API key."""
    text = raw.decode('utf-8', 'replace') if isinstance(raw, bytes) else str(raw or '')
    try:
        obj = json.loads(text)
        if isinstance(obj, list) and obj:
            obj = obj[0]  # Gemini may wrap errors in a list
        err = obj.get('error') if isinstance(obj, dict) else None
        if isinstance(err, dict) and err.get('message'):
            text = str(err['message'])
        elif isinstance(err, str):
            text = err
    except (ValueError, TypeError, AttributeError):
        pass
    if api_key:
        text = text.replace(api_key, '***')
    text = ' '.join(text.split())
    return text[:300] + ('…' if len(text) > 300 else '')


def _http_error_kind(code):
    if code in (401, 403):
        return 'auth'
    if code == 404:
        return 'model'
    if code in (402, 429):
        return 'rate'
    if code in (400, 422):
        return 'bad_request'
    if code >= 500:  # includes Anthropic 529 "overloaded"
        return 'server'
    return 'http'


def _provider_answer_text(provider, result):
    """Extract the answer text; raise ProviderError for blocked, truncated or empty answers."""
    try:
        if provider == 'ChatGPT':
            choice = result['choices'][0]
            finish = choice.get('finish_reason')
            text = choice['message'].get('content') or ''
            if finish == 'content_filter' or choice['message'].get('refusal'):
                raise ProviderError('blocked', provider, detail=choice['message'].get('refusal') or finish)
        elif provider == 'Gemini':
            candidates = result.get('candidates') or []
            if not candidates:
                reason = (result.get('promptFeedback') or {}).get('blockReason')
                raise ProviderError('blocked' if reason else 'empty', provider, detail=reason or '')
            candidate = candidates[0]
            finish = candidate.get('finishReason')
            if finish in ('SAFETY', 'RECITATION', 'BLOCKLIST', 'PROHIBITED_CONTENT', 'SPII'):
                raise ProviderError('blocked', provider, detail=finish)
            parts = (candidate.get('content') or {}).get('parts') or []
            text = ''.join(p.get('text', '') for p in parts)
            finish = 'length' if finish == 'MAX_TOKENS' else finish
        else:
            finish = result.get('stop_reason')
            if finish == 'refusal':
                raise ProviderError('blocked', provider, detail=finish)
            text = ''.join(p.get('text', '') for p in result['content'] if p.get('type') == 'text')
            finish = 'length' if finish == 'max_tokens' else finish
    except ProviderError:
        raise
    except (KeyError, IndexError, TypeError, AttributeError) as exc:
        raise ProviderError('format', provider, detail=type(exc).__name__) from exc
    if finish == 'length':
        raise ProviderError('truncated', provider)
    if not text.strip():
        raise ProviderError('empty', provider)
    return text


def call_provider(provider, model, api_key, prompt):
    body = None
    if provider == 'ChatGPT':
        url = 'https://api.openai.com/v1/chat/completions'
        headers = {'Authorization': 'Bearer ' + api_key}
        body = {'model': model, 'messages': [{'role':'user','content':prompt}], 'temperature':0.7}
    elif provider == 'Gemini':
        url = 'https://generativelanguage.googleapis.com/v1beta/models/' + model + ':generateContent'
        headers = {'x-goog-api-key': api_key}
        body = {'contents':[{'parts':[{'text':prompt}]}]}
    else:
        url = 'https://api.anthropic.com/v1/messages'
        headers = {'x-api-key':api_key,'anthropic-version':'2023-06-01'}
        # Current Claude models think before answering and that counts against max_tokens;
        # 6000 cut answers off. 16000 leaves room for thinking plus 1000/5000-char Style/Lyrics.
        body = {'model':model,'max_tokens':16000,'messages':[{'role':'user','content':prompt}]}
    request = urllib.request.Request(url, data=json.dumps(body).encode('utf-8'), headers={**headers,'Content-Type':'application/json'}, method='POST')
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            result = json.load(response)
    except urllib.error.HTTPError as exc:
        try:
            raw = exc.read()
        except OSError:
            raw = b''
        finally:
            exc.close()  # release the provider's error response (no open connection left behind)
        raise ProviderError(_http_error_kind(exc.code), provider, exc.code,
                            _provider_error_detail(raw, api_key)) from exc
    except TimeoutError as exc:
        raise ProviderError('timeout', provider) from exc
    except urllib.error.URLError as exc:
        if isinstance(exc.reason, TimeoutError):
            raise ProviderError('timeout', provider) from exc
        raise ProviderError('network', provider, detail=_provider_error_detail(str(exc.reason), api_key)) from exc
    except (ValueError, UnicodeDecodeError) as exc:
        raise ProviderError('format', provider, detail='JSON') from exc
    except OSError as exc:
        raise ProviderError('network', provider, detail=_provider_error_detail(str(exc), api_key)) from exc
    return _provider_answer_text(provider, result)


# Local AI command-line tools: use the provider's own CLI login (subscription)
# instead of an API key. The prompt is passed via stdin, never through a shell.
CLI_DEFAULT_COMMANDS = {'ChatGPT': 'codex', 'Gemini': 'gemini', 'Claude': 'claude'}


CLI_TIMEOUT_SECONDS = 300


_CLI_UNSAFE_CHARS = re.compile(r'[&|<>^%!"`\r\n;]')


# ---------------------------------------------------------------------------
# AI connections assistant (Konfiguration › KI-Verbindungen).
# Every user connects their own accounts; MPW never stores keys or logins.
# ---------------------------------------------------------------------------
AI_CONNECTION_LINKS = {
    'claude_install': 'https://code.claude.com/docs/en/setup',
    'gemini_install': 'https://github.com/google-gemini/gemini-cli',
    'codex_install': 'https://github.com/openai/codex',
    'node_install': 'https://nodejs.org/en/download',
    'anthropic_keys': 'https://platform.claude.com/settings/keys',
    'openai_keys': 'https://platform.openai.com/api-keys',
    'gemini_keys': 'https://aistudio.google.com/apikey',
    'suno_access': 'https://suno.com/mcp',
}


SUNO_MCP_URL = 'https://api.suno.com/mcp'


API_KEY_ENV = {'Claude': 'ANTHROPIC_API_KEY', 'ChatGPT': 'OPENAI_API_KEY', 'Gemini': 'GEMINI_API_KEY'}


# Issuer fragments of certificates that antivirus/proxy products create for HTTPS scanning.
TLS_INTERCEPTION_MARKERS = ('norton', 'avast', 'avg ', 'kaspersky', 'eset', 'bitdefender', 'sophos',
                            'mcafee', 'trend micro', 'f-secure', 'g data', 'zscaler', 'fortinet',
                            'netskope', 'ssl/tls scanning', 'web/mail shield')


AI_CONNECTION_TLS_HOSTS = ('api.anthropic.com', 'api.suno.com')


def cli_search_paths(command, system=None, home=None, env=None):
    """Usual install locations of an AI CLI per system (used when PATH does not show it,
    e.g. right after installing, or for programs started by double-click on macOS)."""
    system = system or sys.platform
    home = Path(home) if home else Path.home()
    env = os.environ if env is None else env
    if system.startswith('win'):
        paths = [home / '.local' / 'bin' / f'{command}.exe']
        if env.get('APPDATA'):
            paths.append(Path(env['APPDATA']) / 'npm' / f'{command}.cmd')
        return paths
    folders = [home / '.local' / 'bin', home / '.claude' / 'local', home / '.npm-global' / 'bin',
               home / '.volta' / 'bin', home / 'bin', Path('/opt/homebrew/bin'), Path('/usr/local/bin'),
               Path('/usr/bin')]
    if env.get('NPM_CONFIG_PREFIX'):
        folders.insert(0, Path(env['NPM_CONFIG_PREFIX']) / 'bin')
    # nvm installs one folder per Node version; newest first
    nvm = home / '.nvm' / 'versions' / 'node'
    try:
        folders += sorted((p / 'bin' for p in nvm.iterdir() if p.is_dir()), reverse=True)
    except OSError:
        pass
    return [folder / command for folder in folders]


def find_cli(command):
    """Locate a CLI; also checks the usual install folders, because a program started from
    Explorer/Finder may not see a PATH entry that an installer added."""
    found = shutil.which(command)
    if found:
        return found
    for path in cli_search_paths(command):
        if path.is_file() and (os.name == 'nt' or os.access(path, os.X_OK)):
            return str(path)
    return None


def cli_environment(executable, base=None):
    """Environment for running an AI CLI: its own folder first in PATH, because npm-installed
    CLIs (Gemini, Codex) are Node scripts that need `node` from the same folder."""
    env = dict(os.environ if base is None else base)
    env.setdefault('NO_COLOR', '1')
    folder = str(Path(executable).parent)
    current = env.get('PATH', '')
    if folder and folder not in current.split(os.pathsep):
        env['PATH'] = folder + (os.pathsep + current if current else '')
    return env


def program_name(name):
    """Platform file name of a bundled MPW program (MPW-MCP.exe on Windows, MPW-MCP elsewhere)."""
    return name + ('.exe' if os.name == 'nt' else '')


def mpw_mcp_server_command():
    """Command starting the MPW MCP server: MPW-MCP next to the running program, or the source script."""
    if getattr(sys, 'frozen', False):
        return [str(Path(sys.executable).with_name(program_name('MPW-MCP')))]
    return [sys.executable, str(Path(__file__).resolve().with_name('mpw_mcp_server.py'))]


def claude_desktop_config_snippet(command):
    """JSON block for claude_desktop_config.json (read-only MPW server)."""
    return json.dumps({'mcpServers': {'mpw': {'command': command[0], 'args': list(command[1:])}}},
                      indent=2, ensure_ascii=False)


def run_helper_tool(args, timeout=90, cwd=None):
    """Run a helper command without a console window. Returns (returncode or None, text)."""
    env = cli_environment(args[0])
    try:
        proc = subprocess.run(args, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, timeout=timeout, cwd=cwd, env=env,
                              creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    except subprocess.TimeoutExpired:
        return None, 'timeout'
    except OSError as exc:
        return None, str(exc)
    text = (proc.stdout or b'').decode('utf-8', 'replace') + (proc.stderr or b'').decode('utf-8', 'replace')
    return proc.returncode, re.sub(r'\x1b\[[0-9;?]*[A-Za-z]', '', text).strip()


def parse_claude_auth_status(text):
    """loggedIn from `claude auth status` (JSON); None when it cannot be read."""
    try:
        obj = json.loads(text[text.index('{'):text.rindex('}') + 1])
    except ValueError:
        return None
    value = obj.get('loggedIn') if isinstance(obj, dict) else None
    return value if isinstance(value, bool) else None


def parse_mcp_get_status(returncode, text):
    """'connected', 'needs_auth', 'failed', 'missing' or 'unknown' from `claude mcp get <name>`."""
    low = (text or '').lower()
    if 'no mcp server named' in low:
        return 'missing'
    if 'needs authentication' in low:
        return 'needs_auth'
    if 'failed to connect' in low:
        return 'failed'
    if re.search(r'status:\s*\S*\s*connected', low):
        return 'connected'
    return 'unknown'


def tls_interceptor(issuer):
    """The issuer text if it looks like an HTTPS-scanning antivirus/proxy, else None."""
    low = (issuer or '').lower()
    return issuer if any(marker in low for marker in TLS_INTERCEPTION_MARKERS) else None


def issuer_display_name(issuer):
    """Short readable name of a certificate issuer (organization, else common name)."""
    for field in ('organizationName=', 'commonName='):
        match = re.search(re.escape(field) + r'([^,]+)', issuer or '')
        if match:
            return match.group(1).strip()
    return (issuer or '').strip()


def tls_certificate_issuer(host, timeout=10):
    """Issuer of the certificate this PC actually receives for host (Windows trust store)."""
    context = ssl.create_default_context()
    with socket.create_connection((host, 443), timeout=timeout) as raw:
        with context.wrap_socket(raw, server_hostname=host) as tls:
            cert = tls.getpeercert() or {}
    return ', '.join(f'{key}={value}' for rdn in cert.get('issuer', ()) for key, value in rdn)


# The three AI command-line tools MPW can connect to MCP servers (MPW data, Suno).
MCP_CLIENTS = ('claude', 'gemini', 'codex')


MCP_CLIENT_NAMES = {'claude': 'Claude Code', 'gemini': 'Gemini CLI', 'codex': 'Codex CLI'}


def mcp_setup_command(client, action, server, exe, server_command=None):
    """Argument list that adds/removes an MCP server at user level for one AI CLI.

    action: 'add' or 'remove'; server: 'mpw' (stdio, read-only) or 'suno' (official HTTP server).
    Syntax per the official docs of Claude Code, Gemini CLI and Codex CLI.
    """
    if action == 'remove':
        return {'claude': [exe, 'mcp', 'remove', server, '--scope', 'user'],
                'gemini': [exe, 'mcp', 'remove', '--scope', 'user', server],
                'codex': [exe, 'mcp', 'remove', server]}[client]
    if server == 'suno':
        return {'claude': [exe, 'mcp', 'add', '--scope', 'user', '--transport', 'http', 'suno', SUNO_MCP_URL],
                'gemini': [exe, 'mcp', 'add', '--scope', 'user', '--transport', 'http', 'suno', SUNO_MCP_URL],
                'codex': [exe, 'mcp', 'add', 'suno', '--url', SUNO_MCP_URL]}[client]
    command = list(server_command or mpw_mcp_server_command())
    return {'claude': [exe, 'mcp', 'add', '--scope', 'user', 'mpw', '--', *command],
            'gemini': [exe, 'mcp', 'add', '--scope', 'user', 'mpw', *command],
            'codex': [exe, 'mcp', 'add', 'mpw', '--', *command]}[client]


def mcp_login_console_command(client, exe):
    """Interactive sign-in to Suno's MCP server (OAuth in the browser), run in its own console."""
    return {'claude': [exe],                      # then: /mcp › suno › Authenticate
            'gemini': [exe],                      # then: /mcp auth suno
            'codex': [exe, 'mcp', 'login', 'suno']}[client]


def parse_gemini_mcp_list(text):
    """{name: 'connected' | 'registered'} from `gemini mcp list`
    (lines like '✓ suno: https://… (http) - Connected')."""
    servers = {}
    for line in (text or '').splitlines():
        match = re.match(r'^\s*\S?\s*([A-Za-z0-9_.-]+):\s.*?-\s*(\w[\w ]*)\s*$', line)
        if match:
            servers[match.group(1)] = 'connected' if match.group(2).strip().lower() == 'connected' else 'registered'
    return servers


def parse_codex_mcp_list(text):
    """{name: 'registered'} from `codex mcp list --json` (format not documented; read defensively)."""
    try:
        data = json.loads(text[text.index('['):text.rindex(']') + 1]) if '[' in (text or '') else json.loads(text)
    except (ValueError, TypeError):
        data = None
    names = []
    if isinstance(data, list):
        names = [item.get('name') for item in data if isinstance(item, dict)]
    elif isinstance(data, dict):
        servers = data.get('mcp_servers') or data.get('servers') or data
        names = list(servers) if isinstance(servers, dict) else []
    return {str(name): 'registered' for name in names if name}


def codex_mcp_server_names():
    """MCP servers in the user's Codex config (CODEX_HOME or ~/.codex/config.toml); [] if unreadable."""
    home = os.environ.get('CODEX_HOME', '').strip()
    path = (Path(home) if home else Path.home() / '.codex') / 'config.toml'
    try:
        import tomllib
        data = tomllib.loads(path.read_text(encoding='utf-8'))
    except (OSError, ValueError, ImportError):
        return []
    servers = data.get('mcp_servers')
    return sorted(servers) if isinstance(servers, dict) else []


def codex_disable_mcp_overrides(names):
    """`-c mcp_servers.<name>.enabled=false` per configured server: MPW prompt runs use no MCP tools."""
    args = []
    for name in names:
        key = name if re.fullmatch(r'[A-Za-z0-9_-]+', name) else json.dumps(name)
        args += ['-c', f'mcp_servers.{key}.enabled=false']
    return args


def check_mcp_status(client, exe, home):
    """{'mpw': state, 'suno': state} for one AI CLI; states: connected, needs_auth, failed,
    registered, missing, unknown."""
    if client == 'claude':
        states = {}
        for name in ('mpw', 'suno'):
            code, text = run_helper_tool([exe, 'mcp', 'get', name], timeout=90, cwd=home)
            states[name] = parse_mcp_get_status(code, text) if code is not None else 'unknown'
        return states
    if client == 'gemini':
        code, text = run_helper_tool([exe, 'mcp', 'list'], timeout=120, cwd=home)
        servers = parse_gemini_mcp_list(text) if code == 0 else None
    else:
        code, text = run_helper_tool([exe, 'mcp', 'list', '--json'], timeout=90, cwd=home)
        servers = parse_codex_mcp_list(text) if code == 0 else None
    if servers is None:
        return {'mpw': 'unknown', 'suno': 'unknown'}
    return {name: servers.get(name, 'missing') for name in ('mpw', 'suno')}


def check_ai_connections():
    """Collect the status shown in the KI-Verbindungen window. Read-only; sends no prompts."""
    home = str(Path.home())
    result = {'claude': find_cli('claude'), 'gemini': find_cli('gemini'), 'codex': find_cli('codex'),
              'node': shutil.which('node'), 'claude_logged_in': None,
              'keys': {provider: bool(os.environ.get(env, '').strip()) for provider, env in API_KEY_ENV.items()},
              'mcp': {}, 'tls': {}}
    if result['claude']:
        code, text = run_helper_tool([result['claude'], 'auth', 'status'], timeout=60, cwd=home)
        result['claude_logged_in'] = parse_claude_auth_status(text)
    # User-level entries (cwd = home) are what count for every folder the user starts the AI in.
    for client in MCP_CLIENTS:
        if result[client]:
            result['mcp'][client] = check_mcp_status(client, result[client], home)
    for host in AI_CONNECTION_TLS_HOSTS:
        try:
            issuer = tls_certificate_issuer(host)
            result['tls'][host] = {'issuer': issuer, 'intercepted': tls_interceptor(issuer), 'error': None}
        except (OSError, ssl.SSLError, ValueError) as exc:
            result['tls'][host] = {'issuer': '', 'intercepted': None, 'error': str(exc)[:160]}
    return result


# ---------------------------------------------------------------------------
# Songs & Suno › "An Suno senden (MCP)": a saved prompt goes to Suno's official MCP
# server through Claude Code (the user's own Claude sign-in and Suno sign-in).
# ---------------------------------------------------------------------------
SUNO_MCP_CONFIG = {'mcpServers': {'suno': {'type': 'http', 'url': SUNO_MCP_URL}}}


SUNO_CREATE_TOOL = 'mcp__suno__audio-create'


SUNO_WAIT_TOOL = 'mcp__suno__audio-wait'


SUNO_SEND_TIMEOUT_SECONDS = 600


SUNO_LIMITS = {'title': 256, 'style': 1000, 'lyrics': 5000}


def suno_create_arguments(title, style, lyrics, key=None):
    """Arguments for audio-create in custom mode; the key makes retries free of double charges."""
    arguments = {'title': (title or '').strip(), 'style': (style or '').strip(),
                 'lyrics': (lyrics or '').strip(), 'idempotency_key': key or 'mpw-' + os.urandom(12).hex()}
    if not arguments['style']:
        del arguments['style']
    return arguments


def suno_send_instruction(arguments):
    return ('Send this song to Suno. Call the tool ' + SUNO_CREATE_TOOL + ' exactly once, in custom mode, with '
            'exactly the following JSON object as its arguments. Copy every value verbatim: do not change, shorten, '
            'translate or reformat anything, and do not add other arguments.\n\n'
            + json.dumps(arguments, ensure_ascii=False, indent=1)
            + '\n\nThen call ' + SUNO_WAIT_TOOL + ' once with all clip ids it returned (argument "ids", '
            '"until": "playable"). Do not call any other mcp__suno__ tool. If a tool returns an error, stop and '
            'repeat the error message.')


def _json_or_text(text):
    try:
        return json.loads(text)
    except (ValueError, TypeError):
        return text


def parse_suno_stream(text):
    """Read Claude Code's stream-json output: what was really sent to Suno and Suno's own answers."""
    parsed = {'mcp_status': None, 'create_inputs': [], 'create_result': None, 'wait_result': None,
              'errors': [], 'final_error': None}
    names = {}
    for line in (text or '').splitlines():
        line = line.strip()
        if not line.startswith('{'):
            continue
        try:
            obj = json.loads(line)
        except ValueError:
            continue
        kind = obj.get('type')
        content = (obj.get('message') or {}).get('content') or []
        if kind == 'system' and obj.get('subtype') == 'init':
            for server in obj.get('mcp_servers') or []:
                if server.get('name') == 'suno':
                    parsed['mcp_status'] = server.get('status')
        elif kind == 'assistant':
            for block in content:
                if isinstance(block, dict) and block.get('type') == 'tool_use':
                    names[block.get('id')] = block.get('name')
                    if block.get('name') == SUNO_CREATE_TOOL:
                        parsed['create_inputs'].append(block.get('input') or {})
        elif kind == 'user':
            for block in content:
                if not (isinstance(block, dict) and block.get('type') == 'tool_result'):
                    continue
                name = names.get(block.get('tool_use_id'), '?')
                raw = block.get('content')
                body = raw if isinstance(raw, str) else ''.join(
                    part.get('text', '') for part in raw or [] if isinstance(part, dict))
                if block.get('is_error'):
                    parsed['errors'].append(f'{name}: {body}'[:600])
                elif name == SUNO_CREATE_TOOL:
                    parsed['create_result'] = _json_or_text(body)
                elif name == SUNO_WAIT_TOOL:
                    parsed['wait_result'] = _json_or_text(body)
        elif kind == 'result' and obj.get('is_error'):
            parsed['final_error'] = str(obj.get('result') or obj.get('subtype') or 'error')[:600]
    return parsed


def suno_clips(parsed):
    """Songs from Suno's answer: [{'id', 'title', 'status', 'url'}] (wait result preferred)."""
    def clip(item):
        url = next((item.get(k) for k in ('song_url', 'share_url', 'audio_url', 'url') if item.get(k)), '')
        return {'id': str(item.get('id') or ''), 'title': str(item.get('title') or ''),
                'status': str(item.get('status') or ''), 'url': str(url)}
    wait = parsed.get('wait_result')
    if isinstance(wait, dict):
        items = wait.get('clips') if isinstance(wait.get('clips'), list) else [wait]
        clips = [clip(i) for i in items if isinstance(i, dict) and (i.get('id') or i.get('song_url'))]
        if clips:
            return clips
    create = parsed.get('create_result')
    if isinstance(create, dict):
        if isinstance(create.get('clips'), list):
            return [clip(i) for i in create['clips'] if isinstance(i, dict)]
        ids = create.get('clip_ids') or ([create['id']] if create.get('id') else [])
        return [{'id': str(i), 'title': str(create.get('title') or ''), 'status': str(create.get('status') or ''),
                 'url': ''} for i in ids]
    return []


def suno_send_matches(sent, arguments):
    """True if Claude passed exactly the arguments MPW prepared (no edits, nothing added)."""
    return isinstance(sent, dict) and sent == arguments


def call_suno_via_claude(command, arguments, timeout=SUNO_SEND_TIMEOUT_SECONDS):
    """Run Claude Code with only Suno's MCP server and only audio-create/audio-wait allowed."""
    executable = resolve_cli_executable('Claude', command or 'claude')
    env = cli_environment(executable)
    with tempfile.TemporaryDirectory(prefix='mpw_suno_') as work:
        config = Path(work) / 'mcp.json'
        config.write_text(json.dumps(SUNO_MCP_CONFIG), encoding='utf-8')
        args = [executable, '-p', '--output-format', 'stream-json', '--verbose', '--strict-mcp-config',
                '--mcp-config', str(config), '--allowedTools', SUNO_CREATE_TOOL, SUNO_WAIT_TOOL]
        try:
            proc = subprocess.run(args, input=suno_send_instruction(arguments).encode('utf-8'),
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=work, env=env,
                                  timeout=timeout, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        except subprocess.TimeoutExpired as exc:
            raise ProviderError('cli_timeout', 'Claude', detail=str(timeout)) from exc
        except OSError as exc:
            raise ProviderError('cli_start', 'Claude', detail=_cli_detail(str(exc))) from exc
    parsed = parse_suno_stream(proc.stdout.decode('utf-8', 'replace'))
    parsed['returncode'] = proc.returncode
    parsed['stderr'] = _cli_detail(proc.stderr)
    return parsed


def resolve_cli_executable(provider, command):
    """Resolve a CLI name or path to an executable; reject shell metacharacters."""
    command = (command or '').strip()
    if len(command) >= 2 and command[0] == command[-1] == '"':
        command = command[1:-1].strip()
    if not command or _CLI_UNSAFE_CHARS.search(command):
        raise ProviderError('cli_invalid', provider, detail=command[:120])
    found = shutil.which(command) or (find_cli(command) if not os.path.dirname(command) else None)
    if not found:
        raise ProviderError('cli_missing', provider, detail=command[:200])
    return found


def cli_arguments(provider, executable, model='', answer_file=None, codex_mcp_off=()):
    """Fixed, non-interactive argument lists per CLI; the prompt itself is sent via stdin."""
    if provider == 'ChatGPT':  # OpenAI Codex CLI
        args = [executable, 'exec', '--skip-git-repo-check', '--sandbox', 'read-only', '--color', 'never']
        # MPW prompt runs never use the user's MCP servers (e.g. Suno credits): switch each one off.
        args += codex_disable_mcp_overrides(codex_mcp_off)
        if model:
            args += ['-m', model]
        if answer_file is not None:
            args += ['--output-last-message', str(answer_file)]
        return args + ['-']
    if provider == 'Gemini':  # Gemini CLI reads stdin non-interactively
        args = [executable]
        if model:
            args += ['-m', model]
        return args
    # Claude Code. --strict-mcp-config: MPW prompt requests never start the user's MCP
    # servers (e.g. Suno), so they cannot spend credits or read other data.
    args = [executable, '-p', '--output-format', 'text', '--strict-mcp-config']
    if model:
        args += ['--model', model]
    return args


def _cli_detail(raw):
    text = raw.decode('utf-8', 'replace') if isinstance(raw, bytes) else str(raw or '')
    text = re.sub(r'\x1b\[[0-9;?]*[A-Za-z]', '', text)  # strip ANSI colours
    text = ' '.join(text.split())
    return text[-300:] if len(text) > 300 else text


def cli_answer_json(text):
    """CLIs sometimes add a sentence around the JSON object; keep only the object."""
    stripped = text.strip()
    if stripped.startswith('{') or stripped.startswith('```'):
        return text
    match = re.search(r'\{.*\}', text, re.S)
    if match:
        try:
            obj = json.loads(match.group(0))
            if isinstance(obj, dict) and 'style' in obj and 'lyrics' in obj:
                return match.group(0)
        except ValueError:
            pass
    return text


def call_cli(provider, command, model, prompt, timeout=CLI_TIMEOUT_SECONDS):
    """Run the provider CLI in an empty temporary folder; no project files are visible to it."""
    if model and not re.fullmatch(r'[a-zA-Z0-9._:-]+', model):
        raise ProviderError('cli_invalid', provider, detail=model[:120])
    executable = resolve_cli_executable(provider, command)
    flags = getattr(subprocess, 'CREATE_NO_WINDOW', 0)
    env = cli_environment(executable)
    with tempfile.TemporaryDirectory(prefix='mpw_cli_') as work:
        answer_file = Path(work) / 'answer.txt'
        args = cli_arguments(provider, executable, model, answer_file,
                             codex_mcp_server_names() if provider == 'ChatGPT' else ())
        try:
            proc = subprocess.run(args, input=prompt.encode('utf-8'), stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, cwd=work, env=env, timeout=timeout,
                                  creationflags=flags)
        except subprocess.TimeoutExpired as exc:
            raise ProviderError('cli_timeout', provider, detail=str(timeout)) from exc
        except OSError as exc:
            raise ProviderError('cli_start', provider, detail=_cli_detail(str(exc))) from exc
        answer = proc.stdout.decode('utf-8', 'replace')
        if answer_file.is_file():
            answer = answer_file.read_text(encoding='utf-8', errors='replace') or answer
    if proc.returncode != 0:
        raise ProviderError('cli_failed', provider, proc.returncode, _cli_detail(proc.stderr or proc.stdout))
    answer = re.sub(r'\x1b\[[0-9;?]*[A-Za-z]', '', answer)
    if not answer.strip():
        raise ProviderError('empty', provider)
    return cli_answer_json(answer)


# ---------------------------------------------------------------------------
# Configuration, band folders and the TXT archive of saved prompt versions
# (shared by the desktop app and the MCP server; same rules as before).
# ---------------------------------------------------------------------------
BAND_PROMPT_FOLDER = 'Song-Prompts'


def app_configuration(root=None):
    """Read independent UI preferences without touching the music database."""
    path = Path(root or ROOT) / 'app_configuration.json'
    try:
        data = json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def band_root_directory(root=None):
    root = Path(root or ROOT)
    return Path(app_configuration(root).get('band_root_directory') or (root / 'Bands'))


def existing_named_folder(parent, name):
    if not parent.is_dir():
        return None
    match = next((entry for entry in parent.iterdir()
                  if entry.name.casefold() == name.casefold()), None)
    if match is not None and not match.is_dir():
        raise OSError(f'Der Name ist bereits durch eine Datei belegt: {match}')
    return match


def band_prompt_directory(band_name, band_root=None):
    """Find the existing band safely and add only the fixed prompt folder."""
    band_folder = existing_named_folder(Path(band_root) if band_root else band_root_directory(), band_name)
    if band_folder is None or band_folder.is_symlink():
        raise OSError(f'Bandordner nicht vorhanden oder symbolischer Link: {band_name}')
    prompt_folder = existing_named_folder(band_folder, BAND_PROMPT_FOLDER)
    if prompt_folder is None:
        prompt_folder = band_folder / BAND_PROMPT_FOLDER
        prompt_folder.mkdir(exist_ok=True)
    if prompt_folder.is_symlink():
        raise OSError('Der Prompt-Ordner darf kein symbolischer Link sein.')
    return prompt_folder


def save_prompt_text_file(con, sid, version_id, style, lyrics, band_root=None):
    """Archive a saved AI version without replacing existing files."""
    row = con.execute(
        'SELECT s.title, b.name FROM songs s '
        'JOIN projects p ON p.id=s.project_id '
        'JOIN bands b ON b.id=p.band_id WHERE s.id=?', (sid,)
    ).fetchone()
    if row is None:
        raise ValueError('Song oder zugehörige Band nicht gefunden.')
    song_title, band_name = row[0], row[1]
    folder = band_prompt_directory(band_name, band_root)
    safe_title = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', song_title).strip(' .')
    safe_title = safe_title[:90].rstrip(' .') or 'Song'
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S_%f')
    filename = f'{safe_title}_{timestamp}_V{version_id}.txt'
    payload = (f'Song: {song_title}\nBand: {band_name}\n'
               f'Gespeichert: {datetime.now().isoformat(timespec="seconds")}\n'
               f'Prompt-Version: {version_id}\n\n'
               f'[STYLE]\n{style}\n[/STYLE]\n\n'
               f'[LYRICS]\n{lyrics}\n[/LYRICS]\n')
    # Exclusive creation: existing prompt files are never overwritten.
    with (folder / filename).open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(payload)
    return folder / filename


# ---------------------------------------------------------------------------
# Bands tab: profile, instruments/hardware and hardware presets (database only).
# Same rules as the desktop app; shared with the browser GUI (mpw_web.py).
# ---------------------------------------------------------------------------
PERSONAS = ('Keep Current', 'Keine', 'Individuell')
HARDWARE_TEXT_LIMIT = 500


class BandDataError(ValueError):
    """Validation problem with a stable code for translated messages."""

    def __init__(self, code, **values):
        super().__init__(code)
        self.code, self.values = code, values


def _clean_text(value, field, limit=HARDWARE_TEXT_LIMIT, required=True):
    if not isinstance(value, str):
        raise BandDataError('invalid_field', field=field)
    value = value.strip()
    if required and not value:
        raise BandDataError('empty_field', field=field)
    if len(value) > limit:
        raise BandDataError('too_long', field=field, limit=limit)
    return value


_RESERVED_FOLDER_NAMES = {'CON', 'PRN', 'AUX', 'NUL',
                          *(f'COM{i}' for i in range(1, 10)), *(f'LPT{i}' for i in range(1, 10))}
BAND_NAME_LIMIT = 120


def validate_folder_name(name):
    """Same rule as the desktop app: the name must be a valid folder name on every system."""
    if (not name or name in ('.', '..') or any(ch in name for ch in '<>:"/\\|?*')
            or any(ord(ch) < 32 for ch in name)
            or name.endswith(('.', ' ')) or name.split('.')[0].upper() in _RESERVED_FOLDER_NAMES):
        raise ValueError('Der Name ist als Windows-Ordnername nicht zulässig.')


def create_band(con, name, genre='', second_genre='', persona='Keep Current',
                band_root=None, import_existing=False):
    """Create a band like the desktop „Band anlegen“: band folder + database row + prompt folder.

    An existing folder with the same name is only taken over with ``import_existing=True``
    (never changed); otherwise ``BandDataError('folder_exists')``. Project subfolders are
    created later, when a project is added. Returns id, created flag, folder and an optional
    prompt-folder warning (the band itself is created in that case).
    """
    name = _clean_text(name, 'name', BAND_NAME_LIMIT)
    try:
        validate_folder_name(name)
    except ValueError as exc:
        raise BandDataError('invalid_name') from exc
    genre = _clean_text(genre, 'genre', 200, required=False)
    second_genre = _clean_text(second_genre, 'second_genre', 200, required=False)
    if persona not in PERSONAS:
        raise BandDataError('invalid_persona')
    match = con.execute('SELECT id FROM bands WHERE name=? COLLATE NOCASE', (name,)).fetchone()
    if match is not None:
        raise BandDataError('band_exists', id=match[0])

    base = Path(band_root) if band_root else band_root_directory()
    try:
        existing = existing_named_folder(base, name)
        if existing is not None:
            if existing.is_symlink():
                raise OSError('Der Bandordner darf kein symbolischer Link sein.')
            if not import_existing:
                raise BandDataError('folder_exists', folder=existing.name)
            # keep the folder's own spelling, so band name and folder stay identical
            target, created, name = existing, False, existing.name
        else:
            base.mkdir(parents=True, exist_ok=True)
            target = base / name
            target.mkdir(exist_ok=False)
            created = True
    except OSError as exc:
        raise BandDataError('folder_error', detail=str(exc)) from exc

    try:
        with con:
            new_id = con.execute('INSERT INTO bands(name,genre,second_genre,persona) VALUES(?,?,?,?)',
                                 (name, genre, second_genre, persona)).lastrowid
            for value in (genre, second_genre):
                if value:
                    con.execute('INSERT OR IGNORE INTO genre_catalog(name) VALUES(?)', (value,))
    except sqlite3.Error:
        if created:
            try:
                target.rmdir()  # only the empty folder created just now
            except OSError:
                pass
        raise

    warning = None
    try:
        band_prompt_directory(target.name, base)
    except (OSError, ValueError) as exc:
        warning = str(exc)
    return {'id': new_id, 'name': name, 'created': created, 'folder': str(target), 'prompt_warning': warning}


def update_band_profile(con, band_id, genre, second_genre, persona):
    """Genres and persona of an existing band (the name stays: band folders depend on it)."""
    genre = _clean_text(genre, 'genre', 200, required=False)
    second_genre = _clean_text(second_genre, 'second_genre', 200, required=False)
    if persona not in PERSONAS:
        raise BandDataError('invalid_persona')
    with con:
        if con.execute('UPDATE bands SET genre=?,second_genre=?,persona=? WHERE id=?',
                       (genre, second_genre, persona, band_id)).rowcount != 1:
            raise BandDataError('band_missing')
        # keep the genre menus complete, like the desktop genre catalog
        for value in (genre, second_genre):
            if value:
                con.execute('INSERT OR IGNORE INTO genre_catalog(name) VALUES(?)', (value,))


def band_instruments(con, band_id):
    return [{'id': r[0], 'category': r[1] or '', 'details': r[2] or ''} for r in con.execute(
        'SELECT id,category,details FROM instruments WHERE band_id=? ORDER BY id', (band_id,))]


def add_instrument(con, band_id, category, details):
    category, details = _clean_text(category, 'category'), _clean_text(details, 'details')
    with con:
        if con.execute('SELECT 1 FROM bands WHERE id=?', (band_id,)).fetchone() is None:
            raise BandDataError('band_missing')
        return con.execute('INSERT INTO instruments(band_id,category,details) VALUES(?,?,?)',
                           (band_id, category, details)).lastrowid


def update_instrument(con, instrument_id, category, details):
    category, details = _clean_text(category, 'category'), _clean_text(details, 'details')
    with con:
        if con.execute('UPDATE instruments SET category=?,details=? WHERE id=?',
                       (category, details, instrument_id)).rowcount != 1:
            raise BandDataError('instrument_missing')


def delete_instrument(con, instrument_id):
    with con:
        if con.execute('DELETE FROM instruments WHERE id=?', (instrument_id,)).rowcount != 1:
            raise BandDataError('instrument_missing')


def load_preset_items(con, preset_id):
    """(name, [[category, details], ...]) of a saved preset; damaged data is refused."""
    row = con.execute('SELECT name,items_json FROM hardware_presets WHERE id=?', (preset_id,)).fetchone()
    if row is None:
        raise BandDataError('preset_missing')
    try:
        items = json.loads(row[1])
    except (ValueError, TypeError) as exc:
        raise BandDataError('preset_damaged') from exc
    if not isinstance(items, list) or any(not isinstance(x, list) or len(x) != 2
                                          or not all(isinstance(v, str) for v in x) for x in items):
        raise BandDataError('preset_damaged')
    return row[0], items


def save_band_hardware_as_preset(con, band_id, name, overwrite=False):
    """Store the band's hardware as a named preset. Returns (preset id, item count)."""
    name = _clean_text(name, 'name', 120)
    items = [[c, d] for c, d in con.execute(
        'SELECT category,details FROM instruments WHERE band_id=? ORDER BY id', (band_id,))]
    if not items:
        raise BandDataError('no_hardware')
    payload = json.dumps(items, ensure_ascii=False)
    with con:
        existing = con.execute('SELECT id FROM hardware_presets WHERE name=? COLLATE NOCASE', (name,)).fetchone()
        if existing and not overwrite:
            raise BandDataError('preset_exists', name=name)
        if existing:
            con.execute('UPDATE hardware_presets SET items_json=? WHERE id=?', (payload, existing[0]))
            return existing[0], len(items)
        return con.execute('INSERT INTO hardware_presets(name,items_json) VALUES(?,?)', (name, payload)).lastrowid, len(items)


def transfer_preset_to_band(con, preset_id, band_id, mode):
    """mode 'add': only missing entries (existing hardware stays); 'replace': all hardware replaced.
    Returns {'name', 'added', 'skipped', 'removed'}."""
    if mode not in ('add', 'replace'):
        raise BandDataError('invalid_mode')
    name, items = load_preset_items(con, preset_id)
    if con.execute('SELECT 1 FROM bands WHERE id=?', (band_id,)).fetchone() is None:
        raise BandDataError('band_missing')
    existing = con.execute('SELECT category,details FROM instruments WHERE band_id=?', (band_id,)).fetchall()
    with con:
        if mode == 'replace':
            con.execute('DELETE FROM instruments WHERE band_id=?', (band_id,))
            new_items = [(c, d) for c, d in items]
        else:
            new_items = preset_items_missing(existing, items)
        con.executemany('INSERT INTO instruments(band_id,category,details) VALUES(?,?,?)',
                        [(band_id, c, d) for c, d in new_items])
    return {'name': name, 'added': len(new_items), 'skipped': len(items) - len(new_items) if mode == 'add' else 0,
            'removed': len(existing) if mode == 'replace' else 0}
