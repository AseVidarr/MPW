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


# Texts of the KI-Verbindungen window (desktop and browser GUI), 5 languages.
AI_CONNECTION_TEXTS = {
    'de': {
        'title': 'MPW – KI-Verbindungen',
        'entry_group': 'KI-Verbindungen',
        'entry_hint': 'Claude Code, Gemini CLI, Codex CLI, API-Schlüssel, die Freigabe der MPW-Daten (MCP) und Suno prüfen und einrichten – in einem eigenen Fenster.',
        'entry_button': 'KI-Verbindungen einrichten …',
        'intro': 'Hier siehst du, welche KI-Verbindungen eingerichtet sind, und startest fehlende Schritte direkt. MPW nutzt immer deine eigenen Konten und speichert keine Schlüssel oder Anmeldedaten. „Plattform im Browser öffnen“ im AI Prompt Launcher funktioniert auch ganz ohne Einrichtung.',
        'grp_claude': 'Claude Code (Anmeldung mit deinem Claude-Abo)',
        'grp_cli': 'Gemini CLI und Codex CLI',
        'grp_keys': 'API-Schlüssel (Abrechnung pro Anfrage)',
        'grp_mpw': 'MPW-Daten für KI freigeben (MCP)',
        'grp_suno': 'Suno (über Claude Code, Gemini CLI oder Codex CLI)',
        'grp_net': 'Netzwerk',
        'checking': '… wird geprüft',
        'found': '✔ installiert: {path}',
        'not_installed': '✖ nicht installiert',
        'logged_in': '✔ angemeldet',
        'not_logged_in': '✖ nicht angemeldet – „Anmelden …“ klicken',
        'login_unknown': '⚠ Anmeldestatus unbekannt',
        'cli_line': '{name}: {status}',
        'node_missing': '⚠ Node.js fehlt (für Gemini CLI und Codex CLI nötig)',
        'key_set': '✔ {env} ist gesetzt',
        'key_missing': '– {env} ist nicht gesetzt',
        'mcp_connected': '✔ verbunden',
        'mcp_needs_auth': '⚠ eingetragen – Anmeldung bei Suno fehlt („Bei Suno anmelden …“)',
        'mcp_failed': '✖ eingetragen, aber keine Verbindung – siehe „Netzwerk“',
        'mcp_missing': '– nicht eingerichtet',
        'mcp_unknown': '⚠ Status unbekannt',
        'needs_claude': '– zuerst Claude Code installieren und anmelden',
        'tls_ok': '✔ {host}: direkte Verbindung',
        'tls_intercepted': '⚠ {host}: wird untersucht von „{issuer}“',
        'tls_error': '✖ {host}: nicht erreichbar ({error})',
        'tls_hint': 'Ein Virenscanner untersucht verschlüsselte Verbindungen. Das kann KI-Verbindungen stören (z. B. „Failed to connect“). Lege dort eine Ausnahme für die genannten Adressen an – bei Norton unter Betrugsschutz › Sicheres Web › Ausschlüsse.',
        'keys_note': 'Schlüssel als Windows-Umgebungsvariable hinterlegen oder im AI Prompt Launcher nur für die Sitzung eingeben. MPW zeigt Schlüssel nie an.',
        'mpw_note': 'Die KI kann dann Bandprofile, Songs und Prompt-Versionen aus MPW lesen (nur lesend). Diese Inhalte gehen an den jeweiligen KI-Anbieter.',
        'suno_note': 'Die KI kann damit Songs in deinem Suno-Konto erstellen; das verbraucht Suno-Credits. Der Suno-Zugang ist eine Beta und muss bei Suno beantragt werden. „An Suno senden“ im Reiter Songs & Suno nutzt Claude Code.',
        'btn_install': 'Installationsanleitung öffnen',
        'btn_login': 'Anmelden …',
        'btn_gemini': 'Gemini CLI – Anleitung',
        'btn_codex': 'Codex CLI – Anleitung',
        'btn_node': 'Node.js herunterladen',
        'btn_key_claude': 'Claude-Schlüssel',
        'btn_key_openai': 'OpenAI-Schlüssel',
        'btn_key_gemini': 'Gemini-Schlüssel',
        'btn_connect': 'Verbinden (nur lesend) …',
        'btn_disconnect': 'Trennen …',
        'btn_desktop': 'Für Claude Desktop kopieren',
        'btn_suno_add': 'Suno eintragen …',
        'btn_suno_login': 'Bei Suno anmelden …',
        'btn_suno_access': 'Beta-Zugang beantragen',
        'btn_recheck': 'Erneut prüfen',
        'btn_close': 'Schließen',
        'confirm_connect': 'MPW-Daten für {name} freigeben?\n\n{name} kann danach Bandprofile, Songs, Notizen und Prompt-Versionen lesen; diese Inhalte werden an den KI-Anbieter übertragen. Schreibzugriff wird nicht freigegeben.',
        'confirm_disconnect': 'Die Verbindung zwischen {name} und MPW entfernen?',
        'confirm_suno': 'Den offiziellen Suno-MCP-Server in {name} eintragen?\n\nDanach meldest du dich einmal bei Suno an. Songs, die die KI erstellt, verbrauchen Credits deines Suno-Kontos.',
        'login_started': 'Ein Fenster zur Anmeldung wurde geöffnet. Nach der Anmeldung im Browser hier „Erneut prüfen“ klicken.',
        'desktop_copied': 'Die Einrichtung wurde kopiert. In Claude Desktop unter Einstellungen › Entwickler › „Konfiguration bearbeiten“ den Eintrag „mpw“ unter „mcpServers“ einfügen und Claude Desktop neu starten.',
        'done': 'Erledigt.',
        'failed': 'Der Befehl ist fehlgeschlagen:\n{detail}',
        'need_claude': 'Claude Code wurde nicht gefunden. Bitte zuerst über „Installationsanleitung öffnen“ installieren.',
        'mcp_exe_missing': 'Der MPW-MCP-Server wurde nicht gefunden:\n{path}',
        'check_failed': '⚠ Prüfung fehlgeschlagen: {error}',
        'target_label': 'Einrichten für:',
        'mcp_registered': '✔ eingetragen (Verbindung entsteht beim Start der KI)',
        'btn_suno_remove': 'Suno entfernen …',
        'confirm_suno_remove': 'Suno aus {name} entfernen? Deine Songs und dein Suno-Konto bleiben unverändert.',
        'need_cli': '{name} wurde nicht gefunden. Bitte zuerst installieren (Anleitung weiter oben).',
        'suno_login_started_claude': 'Claude Code wurde in einem eigenen Fenster gestartet. Dort /mcp eingeben, „suno“ wählen und „Authenticate“ bestätigen. Danach hier „Erneut prüfen“ klicken.',
        'suno_login_started_gemini': 'Gemini CLI wurde in einem eigenen Fenster gestartet. Dort /mcp auth suno eingeben und dich im Browser bei Suno anmelden. Danach hier „Erneut prüfen“ klicken.',
        'suno_login_started_codex': 'Die Anmeldung von Codex CLI bei Suno wurde in einem eigenen Fenster gestartet; der Browser öffnet sich. Nach der Anmeldung hier „Erneut prüfen“ klicken.',
    },
    'en': {
        'title': 'MPW – AI connections',
        'entry_group': 'AI connections',
        'entry_hint': 'Check and set up Claude Code, Gemini CLI, Codex CLI, API keys, sharing MPW data (MCP) and Suno – in a separate window.',
        'entry_button': 'Set up AI connections …',
        'intro': 'See which AI connections are set up and start missing steps directly. MPW always uses your own accounts and never stores keys or sign-ins. “Open platform in browser” in the AI Prompt Launcher works without any setup.',
        'grp_claude': 'Claude Code (sign in with your Claude subscription)',
        'grp_cli': 'Gemini CLI and Codex CLI',
        'grp_keys': 'API keys (billed per request)',
        'grp_mpw': 'Share MPW data with AI (MCP)',
        'grp_suno': 'Suno (via Claude Code, Gemini CLI or Codex CLI)',
        'grp_net': 'Network',
        'checking': '… checking',
        'found': '✔ installed: {path}',
        'not_installed': '✖ not installed',
        'logged_in': '✔ signed in',
        'not_logged_in': '✖ not signed in – click “Sign in …”',
        'login_unknown': '⚠ sign-in status unknown',
        'cli_line': '{name}: {status}',
        'node_missing': '⚠ Node.js is missing (required for Gemini CLI and Codex CLI)',
        'key_set': '✔ {env} is set',
        'key_missing': '– {env} is not set',
        'mcp_connected': '✔ connected',
        'mcp_needs_auth': '⚠ added – Suno sign-in missing (“Sign in to Suno …”)',
        'mcp_failed': '✖ added, but no connection – see “Network”',
        'mcp_missing': '– not set up',
        'mcp_unknown': '⚠ status unknown',
        'needs_claude': '– install Claude Code and sign in first',
        'tls_ok': '✔ {host}: direct connection',
        'tls_intercepted': '⚠ {host}: inspected by “{issuer}”',
        'tls_error': '✖ {host}: not reachable ({error})',
        'tls_hint': 'An antivirus program inspects encrypted connections. This can break AI connections (e.g. “Failed to connect”). Add an exception for the addresses listed – in Norton under Scam Protection › Safe Web › Exclusions.',
        'keys_note': 'Store keys as Windows environment variables or enter them for one session in the AI Prompt Launcher. MPW never displays keys.',
        'mpw_note': 'The AI can then read band profiles, songs and prompt versions from MPW (read-only). This content is sent to the respective AI provider.',
        'suno_note': 'The AI can then create songs in your Suno account, which uses Suno credits. Suno access is a beta and must be requested from Suno. “Send to Suno” on the Songs & Suno tab uses Claude Code.',
        'btn_install': 'Open installation guide',
        'btn_login': 'Sign in …',
        'btn_gemini': 'Gemini CLI – guide',
        'btn_codex': 'Codex CLI – guide',
        'btn_node': 'Download Node.js',
        'btn_key_claude': 'Claude key',
        'btn_key_openai': 'OpenAI key',
        'btn_key_gemini': 'Gemini key',
        'btn_connect': 'Connect (read-only) …',
        'btn_disconnect': 'Disconnect …',
        'btn_desktop': 'Copy for Claude Desktop',
        'btn_suno_add': 'Add Suno …',
        'btn_suno_login': 'Sign in to Suno …',
        'btn_suno_access': 'Request beta access',
        'btn_recheck': 'Check again',
        'btn_close': 'Close',
        'confirm_connect': 'Share MPW data with {name}?\n\n{name} can then read band profiles, songs, notes and prompt versions; this content is sent to the AI provider. Write access is not granted.',
        'confirm_disconnect': 'Remove the connection between {name} and MPW?',
        'confirm_suno': 'Add the official Suno MCP server to {name}?\n\nYou then sign in to Suno once. Songs created by the AI use credits from your Suno account.',
        'login_started': 'A sign-in window was opened. After signing in in the browser, click “Check again” here.',
        'desktop_copied': 'The setup was copied. In Claude Desktop open Settings › Developer › “Edit Config”, paste the “mpw” entry under “mcpServers” and restart Claude Desktop.',
        'done': 'Done.',
        'failed': 'The command failed:\n{detail}',
        'need_claude': 'Claude Code was not found. Please install it first via “Open installation guide”.',
        'mcp_exe_missing': 'The MPW MCP server was not found:\n{path}',
        'check_failed': '⚠ Check failed: {error}',
        'target_label': 'Set up for:',
        'mcp_registered': '✔ added (connects when the AI starts)',
        'btn_suno_remove': 'Remove Suno …',
        'confirm_suno_remove': 'Remove Suno from {name}? Your songs and your Suno account stay unchanged.',
        'need_cli': '{name} was not found. Please install it first (guide above).',
        'suno_login_started_claude': 'Claude Code was started in a separate window. Type /mcp there, choose “suno” and confirm “Authenticate”. Then click “Check again” here.',
        'suno_login_started_gemini': 'Gemini CLI was started in a separate window. Type /mcp auth suno there and sign in to Suno in the browser. Then click “Check again” here.',
        'suno_login_started_codex': 'Codex CLI’s sign-in to Suno was started in a separate window; the browser opens. After signing in, click “Check again” here.',
    },
    'fr': {
        'title': 'MPW – Connexions IA',
        'entry_group': 'Connexions IA',
        'entry_hint': 'Vérifier et configurer Claude Code, Gemini CLI, Codex CLI, les clés API, le partage des données MPW (MCP) et Suno – dans une fenêtre distincte.',
        'entry_button': 'Configurer les connexions IA …',
        'intro': 'Voyez quelles connexions IA sont configurées et lancez directement les étapes manquantes. MPW utilise toujours vos propres comptes et n’enregistre ni clés ni identifiants. « Ouvrir la plateforme dans le navigateur » fonctionne sans configuration.',
        'grp_claude': 'Claude Code (connexion avec votre abonnement Claude)',
        'grp_cli': 'Gemini CLI et Codex CLI',
        'grp_keys': 'Clés API (facturation par requête)',
        'grp_mpw': 'Partager les données MPW avec l’IA (MCP)',
        'grp_suno': 'Suno (via Claude Code, Gemini CLI ou Codex CLI)',
        'grp_net': 'Réseau',
        'checking': '… vérification',
        'found': '✔ installé : {path}',
        'not_installed': '✖ non installé',
        'logged_in': '✔ connecté',
        'not_logged_in': '✖ non connecté – cliquez sur « Se connecter … »',
        'login_unknown': '⚠ état de connexion inconnu',
        'cli_line': '{name} : {status}',
        'node_missing': '⚠ Node.js manque (nécessaire pour Gemini CLI et Codex CLI)',
        'key_set': '✔ {env} est défini',
        'key_missing': '– {env} n’est pas défini',
        'mcp_connected': '✔ connecté',
        'mcp_needs_auth': '⚠ ajouté – connexion à Suno manquante (« Se connecter à Suno … »)',
        'mcp_failed': '✖ ajouté, mais pas de connexion – voir « Réseau »',
        'mcp_missing': '– non configuré',
        'mcp_unknown': '⚠ état inconnu',
        'needs_claude': '– installez d’abord Claude Code et connectez-vous',
        'tls_ok': '✔ {host} : connexion directe',
        'tls_intercepted': '⚠ {host} : inspecté par « {issuer} »',
        'tls_error': '✖ {host} : inaccessible ({error})',
        'tls_hint': 'Un antivirus inspecte les connexions chiffrées. Cela peut perturber les connexions IA (p. ex. « Failed to connect »). Ajoutez une exception pour les adresses indiquées – dans Norton sous Protection contre les arnaques › Safe Web › Exclusions.',
        'keys_note': 'Enregistrez les clés comme variables d’environnement Windows ou saisissez-les pour une session dans l’AI Prompt Launcher. MPW n’affiche jamais les clés.',
        'mpw_note': 'L’IA peut alors lire les profils, morceaux et versions de prompts dans MPW (lecture seule). Ces contenus sont transmis au fournisseur d’IA concerné.',
        'suno_note': 'L’IA peut alors créer des morceaux dans votre compte Suno, ce qui consomme des crédits Suno. L’accès Suno est une bêta à demander auprès de Suno. « Envoyer à Suno » dans l’onglet Songs & Suno utilise Claude Code.',
        'btn_install': 'Ouvrir le guide d’installation',
        'btn_login': 'Se connecter …',
        'btn_gemini': 'Gemini CLI – guide',
        'btn_codex': 'Codex CLI – guide',
        'btn_node': 'Télécharger Node.js',
        'btn_key_claude': 'Clé Claude',
        'btn_key_openai': 'Clé OpenAI',
        'btn_key_gemini': 'Clé Gemini',
        'btn_connect': 'Connecter (lecture seule) …',
        'btn_disconnect': 'Déconnecter …',
        'btn_desktop': 'Copier pour Claude Desktop',
        'btn_suno_add': 'Ajouter Suno …',
        'btn_suno_login': 'Se connecter à Suno …',
        'btn_suno_access': 'Demander l’accès bêta',
        'btn_recheck': 'Vérifier à nouveau',
        'btn_close': 'Fermer',
        'confirm_connect': 'Partager les données MPW avec {name} ?\n\n{name} pourra lire les profils, morceaux, notes et versions de prompts ; ces contenus sont transmis au fournisseur d’IA. Aucun accès en écriture n’est accordé.',
        'confirm_disconnect': 'Supprimer la connexion entre {name} et MPW ?',
        'confirm_suno': 'Ajouter le serveur MCP officiel de Suno à {name} ?\n\nVous vous connectez ensuite une fois à Suno. Les morceaux créés par l’IA consomment des crédits de votre compte Suno.',
        'login_started': 'Une fenêtre de connexion a été ouverte. Après la connexion dans le navigateur, cliquez ici sur « Vérifier à nouveau ».',
        'desktop_copied': 'La configuration a été copiée. Dans Claude Desktop, ouvrez Paramètres › Développeur › « Modifier la configuration », collez l’entrée « mpw » sous « mcpServers » et redémarrez Claude Desktop.',
        'done': 'Terminé.',
        'failed': 'La commande a échoué :\n{detail}',
        'need_claude': 'Claude Code est introuvable. Installez-le d’abord via « Ouvrir le guide d’installation ».',
        'mcp_exe_missing': 'Le serveur MCP de MPW est introuvable :\n{path}',
        'check_failed': '⚠ Échec de la vérification : {error}',
        'target_label': 'Configurer pour :',
        'mcp_registered': '✔ ajouté (connexion au démarrage de l’IA)',
        'btn_suno_remove': 'Retirer Suno …',
        'confirm_suno_remove': 'Retirer Suno de {name} ? Vos morceaux et votre compte Suno restent inchangés.',
        'need_cli': '{name} est introuvable. Installez-le d’abord (guide plus haut).',
        'suno_login_started_claude': 'Claude Code a été lancé dans une fenêtre distincte. Tapez /mcp, choisissez « suno » et confirmez « Authenticate ». Cliquez ensuite ici sur « Vérifier à nouveau ».',
        'suno_login_started_gemini': 'Gemini CLI a été lancé dans une fenêtre distincte. Tapez /mcp auth suno et connectez-vous à Suno dans le navigateur. Cliquez ensuite ici sur « Vérifier à nouveau ».',
        'suno_login_started_codex': 'La connexion de Codex CLI à Suno a été lancée dans une fenêtre distincte ; le navigateur s’ouvre. Après la connexion, cliquez ici sur « Vérifier à nouveau ».',
    },
    'es': {
        'title': 'MPW – Conexiones de IA',
        'entry_group': 'Conexiones de IA',
        'entry_hint': 'Comprobar y configurar Claude Code, Gemini CLI, Codex CLI, claves API, compartir datos de MPW (MCP) y Suno, en una ventana aparte.',
        'entry_button': 'Configurar conexiones de IA …',
        'intro': 'Vea qué conexiones de IA están configuradas e inicie directamente los pasos que faltan. MPW usa siempre sus propias cuentas y no guarda claves ni inicios de sesión. «Abrir plataforma en el navegador» funciona sin configuración.',
        'grp_claude': 'Claude Code (inicio de sesión con su suscripción de Claude)',
        'grp_cli': 'Gemini CLI y Codex CLI',
        'grp_keys': 'Claves API (facturación por solicitud)',
        'grp_mpw': 'Compartir datos de MPW con la IA (MCP)',
        'grp_suno': 'Suno (a través de Claude Code, Gemini CLI o Codex CLI)',
        'grp_net': 'Red',
        'checking': '… comprobando',
        'found': '✔ instalado: {path}',
        'not_installed': '✖ no instalado',
        'logged_in': '✔ sesión iniciada',
        'not_logged_in': '✖ sin sesión – haga clic en «Iniciar sesión …»',
        'login_unknown': '⚠ estado de sesión desconocido',
        'cli_line': '{name}: {status}',
        'node_missing': '⚠ Falta Node.js (necesario para Gemini CLI y Codex CLI)',
        'key_set': '✔ {env} está definida',
        'key_missing': '– {env} no está definida',
        'mcp_connected': '✔ conectado',
        'mcp_needs_auth': '⚠ añadido – falta iniciar sesión en Suno («Iniciar sesión en Suno …»)',
        'mcp_failed': '✖ añadido, pero sin conexión – vea «Red»',
        'mcp_missing': '– no configurado',
        'mcp_unknown': '⚠ estado desconocido',
        'needs_claude': '– primero instale Claude Code e inicie sesión',
        'tls_ok': '✔ {host}: conexión directa',
        'tls_intercepted': '⚠ {host}: inspeccionado por «{issuer}»',
        'tls_error': '✖ {host}: no accesible ({error})',
        'tls_hint': 'Un antivirus inspecciona las conexiones cifradas. Esto puede impedir las conexiones de IA (p. ej. «Failed to connect»). Añada una excepción para las direcciones indicadas; en Norton en Protección contra estafas › Safe Web › Exclusiones.',
        'keys_note': 'Guarde las claves como variables de entorno de Windows o introdúzcalas para una sesión en el AI Prompt Launcher. MPW nunca muestra las claves.',
        'mpw_note': 'La IA podrá leer perfiles de bandas, canciones y versiones de prompts de MPW (solo lectura). Este contenido se envía al proveedor de IA correspondiente.',
        'suno_note': 'La IA podrá crear canciones en su cuenta de Suno, lo que consume créditos de Suno. El acceso a Suno es una beta que debe solicitarse a Suno. «Enviar a Suno» en la pestaña Songs & Suno usa Claude Code.',
        'btn_install': 'Abrir guía de instalación',
        'btn_login': 'Iniciar sesión …',
        'btn_gemini': 'Gemini CLI – guía',
        'btn_codex': 'Codex CLI – guía',
        'btn_node': 'Descargar Node.js',
        'btn_key_claude': 'Clave de Claude',
        'btn_key_openai': 'Clave de OpenAI',
        'btn_key_gemini': 'Clave de Gemini',
        'btn_connect': 'Conectar (solo lectura) …',
        'btn_disconnect': 'Desconectar …',
        'btn_desktop': 'Copiar para Claude Desktop',
        'btn_suno_add': 'Añadir Suno …',
        'btn_suno_login': 'Iniciar sesión en Suno …',
        'btn_suno_access': 'Solicitar acceso beta',
        'btn_recheck': 'Comprobar de nuevo',
        'btn_close': 'Cerrar',
        'confirm_connect': '¿Compartir los datos de MPW con {name}?\n\n{name} podrá leer perfiles de bandas, canciones, notas y versiones de prompts; este contenido se envía al proveedor de IA. No se concede acceso de escritura.',
        'confirm_disconnect': '¿Eliminar la conexión entre {name} y MPW?',
        'confirm_suno': '¿Añadir el servidor MCP oficial de Suno a {name}?\n\nDespués inicia sesión una vez en Suno. Las canciones creadas por la IA consumen créditos de su cuenta de Suno.',
        'login_started': 'Se abrió una ventana de inicio de sesión. Tras iniciar sesión en el navegador, haga clic aquí en «Comprobar de nuevo».',
        'desktop_copied': 'La configuración se copió. En Claude Desktop abra Configuración › Desarrollador › «Editar configuración», pegue la entrada «mpw» en «mcpServers» y reinicie Claude Desktop.',
        'done': 'Hecho.',
        'failed': 'El comando falló:\n{detail}',
        'need_claude': 'No se encontró Claude Code. Instálelo primero con «Abrir guía de instalación».',
        'mcp_exe_missing': 'No se encontró el servidor MCP de MPW:\n{path}',
        'check_failed': '⚠ Error en la comprobación: {error}',
        'target_label': 'Configurar para:',
        'mcp_registered': '✔ añadido (se conecta al iniciar la IA)',
        'btn_suno_remove': 'Quitar Suno …',
        'confirm_suno_remove': '¿Quitar Suno de {name}? Sus canciones y su cuenta de Suno no cambian.',
        'need_cli': 'No se encontró {name}. Instálelo primero (guía más arriba).',
        'suno_login_started_claude': 'Claude Code se inició en una ventana aparte. Escriba /mcp, elija «suno» y confirme «Authenticate». Después haga clic aquí en «Comprobar de nuevo».',
        'suno_login_started_gemini': 'Gemini CLI se inició en una ventana aparte. Escriba /mcp auth suno e inicie sesión en Suno en el navegador. Después haga clic aquí en «Comprobar de nuevo».',
        'suno_login_started_codex': 'El inicio de sesión de Codex CLI en Suno se inició en una ventana aparte; se abre el navegador. Tras iniciar sesión, haga clic aquí en «Comprobar de nuevo».',
    },
    'it': {
        'title': 'MPW – Connessioni IA',
        'entry_group': 'Connessioni IA',
        'entry_hint': 'Verificare e configurare Claude Code, Gemini CLI, Codex CLI, chiavi API, la condivisione dei dati MPW (MCP) e Suno, in una finestra separata.',
        'entry_button': 'Configura connessioni IA …',
        'intro': 'Vedi quali connessioni IA sono configurate e avvia subito i passaggi mancanti. MPW usa sempre i tuoi account e non salva chiavi né accessi. «Apri piattaforma nel browser» funziona senza configurazione.',
        'grp_claude': 'Claude Code (accesso con il tuo abbonamento Claude)',
        'grp_cli': 'Gemini CLI e Codex CLI',
        'grp_keys': 'Chiavi API (fatturazione per richiesta)',
        'grp_mpw': 'Condividi i dati MPW con l’IA (MCP)',
        'grp_suno': 'Suno (tramite Claude Code, Gemini CLI o Codex CLI)',
        'grp_net': 'Rete',
        'checking': '… verifica in corso',
        'found': '✔ installato: {path}',
        'not_installed': '✖ non installato',
        'logged_in': '✔ accesso eseguito',
        'not_logged_in': '✖ accesso non eseguito – fai clic su «Accedi …»',
        'login_unknown': '⚠ stato di accesso sconosciuto',
        'cli_line': '{name}: {status}',
        'node_missing': '⚠ Manca Node.js (necessario per Gemini CLI e Codex CLI)',
        'key_set': '✔ {env} è impostata',
        'key_missing': '– {env} non è impostata',
        'mcp_connected': '✔ connesso',
        'mcp_needs_auth': '⚠ aggiunto – manca l’accesso a Suno («Accedi a Suno …»)',
        'mcp_failed': '✖ aggiunto, ma nessuna connessione – vedi «Rete»',
        'mcp_missing': '– non configurato',
        'mcp_unknown': '⚠ stato sconosciuto',
        'needs_claude': '– prima installa Claude Code ed esegui l’accesso',
        'tls_ok': '✔ {host}: connessione diretta',
        'tls_intercepted': '⚠ {host}: ispezionato da «{issuer}»',
        'tls_error': '✖ {host}: non raggiungibile ({error})',
        'tls_hint': 'Un antivirus ispeziona le connessioni cifrate. Questo può bloccare le connessioni IA (ad es. «Failed to connect»). Aggiungi un’eccezione per gli indirizzi indicati; in Norton in Protezione dalle truffe › Safe Web › Esclusioni.',
        'keys_note': 'Salva le chiavi come variabili d’ambiente di Windows o inseriscile per una sessione nell’AI Prompt Launcher. MPW non mostra mai le chiavi.',
        'mpw_note': 'L’IA potrà leggere profili, brani e versioni dei prompt da MPW (sola lettura). Questi contenuti vengono inviati al rispettivo fornitore di IA.',
        'suno_note': 'L’IA potrà creare brani nel tuo account Suno, consumando crediti Suno. L’accesso a Suno è una beta da richiedere a Suno. «Invia a Suno» nella scheda Songs & Suno usa Claude Code.',
        'btn_install': 'Apri guida all’installazione',
        'btn_login': 'Accedi …',
        'btn_gemini': 'Gemini CLI – guida',
        'btn_codex': 'Codex CLI – guida',
        'btn_node': 'Scarica Node.js',
        'btn_key_claude': 'Chiave Claude',
        'btn_key_openai': 'Chiave OpenAI',
        'btn_key_gemini': 'Chiave Gemini',
        'btn_connect': 'Connetti (sola lettura) …',
        'btn_disconnect': 'Disconnetti …',
        'btn_desktop': 'Copia per Claude Desktop',
        'btn_suno_add': 'Aggiungi Suno …',
        'btn_suno_login': 'Accedi a Suno …',
        'btn_suno_access': 'Richiedi accesso beta',
        'btn_recheck': 'Verifica di nuovo',
        'btn_close': 'Chiudi',
        'confirm_connect': 'Condividere i dati MPW con {name}?\n\n{name} potrà leggere profili, brani, note e versioni dei prompt; questi contenuti vengono inviati al fornitore di IA. Nessun accesso in scrittura.',
        'confirm_disconnect': 'Rimuovere la connessione tra {name} e MPW?',
        'confirm_suno': 'Aggiungere il server MCP ufficiale di Suno a {name}?\n\nPoi accedi una volta a Suno. I brani creati dall’IA consumano crediti del tuo account Suno.',
        'login_started': 'È stata aperta una finestra di accesso. Dopo l’accesso nel browser, fai clic qui su «Verifica di nuovo».',
        'desktop_copied': 'La configurazione è stata copiata. In Claude Desktop apri Impostazioni › Sviluppatore › «Modifica configurazione», incolla la voce «mpw» sotto «mcpServers» e riavvia Claude Desktop.',
        'done': 'Fatto.',
        'failed': 'Il comando non è riuscito:\n{detail}',
        'need_claude': 'Claude Code non trovato. Installalo prima con «Apri guida all’installazione».',
        'mcp_exe_missing': 'Server MCP di MPW non trovato:\n{path}',
        'check_failed': '⚠ Verifica non riuscita: {error}',
        'target_label': 'Configura per:',
        'mcp_registered': '✔ aggiunto (si connette all’avvio dell’IA)',
        'btn_suno_remove': 'Rimuovi Suno …',
        'confirm_suno_remove': 'Rimuovere Suno da {name}? I tuoi brani e il tuo account Suno restano invariati.',
        'need_cli': '{name} non trovato. Installalo prima (guida più sopra).',
        'suno_login_started_claude': 'Claude Code è stato avviato in una finestra separata. Digita /mcp, scegli «suno» e conferma «Authenticate». Poi fai clic qui su «Verifica di nuovo».',
        'suno_login_started_gemini': 'Gemini CLI è stato avviato in una finestra separata. Digita /mcp auth suno e accedi a Suno nel browser. Poi fai clic qui su «Verifica di nuovo».',
        'suno_login_started_codex': 'L’accesso di Codex CLI a Suno è stato avviato in una finestra separata; si apre il browser. Dopo l’accesso, fai clic qui su «Verifica di nuovo».',
    },
}


def ai_connection_status(result):
    """Language-neutral status lines of the KI-Verbindungen window from check_ai_connections().

    Returns ({line: [text_key, values]}, tls_intercepted). A value may itself be [text_key, values]
    (translated first), e.g. 'cli_line' with a nested 'status'. Shared by desktop and browser GUI.
    """
    keys = (['claude_path', 'claude_login', 'gemini_path', 'codex_path', 'node']
            + [f'key_{p}' for p in API_KEY_ENV]
            + [f'mcp_{name}_{c}' for name in ('mpw', 'suno') for c in MCP_CLIENTS]
            + [f'tls_{host}' for host in AI_CONNECTION_TLS_HOSTS])
    if result.get('error'):
        return {key: ['check_failed', {'error': result['error']}] for key in keys}, False

    def installed(path):
        return ['found', {'path': path}] if path else ['not_installed', {}]
    lines = {'claude_path': installed(result.get('claude'))}
    login = result.get('claude_logged_in')
    lines['claude_login'] = [('logged_in' if login is True else 'not_logged_in' if login is False
                              else 'needs_claude' if not result.get('claude') else 'login_unknown'), {}]
    lines['gemini_path'] = ['cli_line', {'name': 'Gemini CLI', 'status': installed(result.get('gemini'))}]
    lines['codex_path'] = ['cli_line', {'name': 'Codex CLI', 'status': installed(result.get('codex'))}]
    lines['node'] = (['cli_line', {'name': 'Node.js', 'status': installed(result.get('node'))}]
                     if result.get('node') else ['node_missing', {}])
    for provider, env in API_KEY_ENV.items():
        lines[f'key_{provider}'] = ['key_set' if result.get('keys', {}).get(provider) else 'key_missing', {'env': env}]
    state_keys = {'connected': 'mcp_connected', 'needs_auth': 'mcp_needs_auth', 'failed': 'mcp_failed',
                  'registered': 'mcp_registered', 'missing': 'mcp_missing'}
    for client in MCP_CLIENTS:
        states = result.get('mcp', {}).get(client) or {}
        for name in ('mpw', 'suno'):
            status = [state_keys.get(states.get(name), 'mcp_unknown'), {}] if result.get(client) else ['not_installed', {}]
            lines[f'mcp_{name}_{client}'] = ['cli_line', {'name': MCP_CLIENT_NAMES[client], 'status': status}]
    intercepted = False
    for host in AI_CONNECTION_TLS_HOSTS:
        info = result.get('tls', {}).get(host) or {}
        if info.get('error'):
            lines[f'tls_{host}'] = ['tls_error', {'host': host, 'error': info['error']}]
        elif info.get('intercepted'):
            intercepted = True
            lines[f'tls_{host}'] = ['tls_intercepted', {'host': host, 'issuer': issuer_display_name(info['intercepted'])}]
        else:
            lines[f'tls_{host}'] = ['tls_ok', {'host': host}]
    return lines, intercepted


def render_ai_connection_line(texts, line):
    """Translate one [text_key, values] line with the given language table (nested values first)."""
    key, values = line
    values = {k: render_ai_connection_line(texts, v) if isinstance(v, list) else v for k, v in values.items()}
    return texts[key].format(**values) if values else texts[key]


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


# Texts of „An Suno senden“ (desktop dialog and browser GUI), 5 languages.
SUNO_SEND_TEXTS = {
    'de': {
        'button': 'An Suno senden (MCP) …',
        'tooltip': 'Einen gespeicherten Prompt dieses Songs über Claude Code und Sunos MCP-Server an Suno senden.',
        'title': 'An Suno senden – {song}',
        'prompt_label': 'Gespeicherter Prompt:',
        'active': 'Aktiver Song-Prompt (gespeichert)',
        'version': 'Version #{id} · {provider} · {created}',
        'title_label': 'Songtitel bei Suno:',
        'style_label': 'Style ({count}/1.000)',
        'lyrics_label': 'Lyrics ({count}/5.000)',
        'info': 'Claude Code überträgt den Prompt unverändert an Sunos MCP-Server (audio-create, Custom-Modus). Suno erstellt dabei 2 Songs und verbraucht Credits deines Suno-Kontos. Voraussetzung: Claude Code angemeldet und Suno verbunden (Konfiguration › KI-Verbindungen).',
        'unsaved': '⚠ Im Editor gibt es ungespeicherte Änderungen. Gesendet wird der gespeicherte Stand.',
        'btn_send': 'An Suno senden …',
        'btn_save_links': 'Links beim Song speichern',
        'btn_close': 'Schließen',
        'confirm': 'Jetzt an Suno senden?\n\nTitel: {title}\nStyle: {style} Zeichen · Lyrics: {lyrics} Zeichen\n\nSuno erstellt 2 Songs und verbraucht dafür Credits deines Suno-Kontos.',
        'no_song': 'Bitte zuerst einen Song auswählen.',
        'empty': 'Dieser Prompt hat keine Lyrics. Für Sunos Custom-Modus sind Lyrics nötig.',
        'too_long': 'Der Prompt überschreitet Sunos Grenzen (Titel 256, Style 1.000, Lyrics 5.000 Zeichen).',
        'sending': '… wird an Suno gesendet. Das kann einige Minuten dauern.',
        'done': '✔ Suno hat {count} Song(s) erstellt:',
        'no_clips': 'Suno hat den Auftrag angenommen, aber keine Song-Links zurückgegeben. Bitte in deiner Suno-Bibliothek nachsehen.',
        'mismatch': '⚠ Claude hat den Prompt nicht exakt so übertragen wie in MPW gespeichert. Bitte den Song in Suno prüfen.',
        'multiple': '⚠ Claude hat audio-create mehrfach aufgerufen. Mit demselben Auftragsschlüssel berechnet Suno nicht doppelt; bitte trotzdem die Bibliothek prüfen.',
        'not_connected': 'Suno ist in Claude Code nicht verbunden (Status: {status}). Unter Konfiguration › KI-Verbindungen „Suno eintragen …“ bzw. „Bei Suno anmelden …“ nutzen.',
        'not_sent': 'Claude hat audio-create nicht aufgerufen. Es wurde nichts erstellt.',
        'error': 'Senden an Suno fehlgeschlagen:\n{detail}',
        'timeout': 'Keine Rückmeldung innerhalb von {minutes} Minuten. Suno hat die Songs eventuell trotzdem erstellt – bitte in deiner Suno-Bibliothek nachsehen.',
        'links_saved': '{count} Link(s) beim Song gespeichert (Medien & Player).',
        'link_label': 'Suno – {title} ({index}/{count})',
    },
    'en': {
        'button': 'Send to Suno (MCP) …',
        'tooltip': 'Send a saved prompt of this song to Suno via Claude Code and Suno’s MCP server.',
        'title': 'Send to Suno – {song}',
        'prompt_label': 'Saved prompt:',
        'active': 'Active song prompt (saved)',
        'version': 'Version #{id} · {provider} · {created}',
        'title_label': 'Song title at Suno:',
        'style_label': 'Style ({count}/1,000)',
        'lyrics_label': 'Lyrics ({count}/5,000)',
        'info': 'Claude Code sends the prompt unchanged to Suno’s MCP server (audio-create, custom mode). Suno creates 2 songs and uses credits from your Suno account. Requires Claude Code signed in and Suno connected (Configuration › AI connections).',
        'unsaved': '⚠ The editor has unsaved changes. The saved version will be sent.',
        'btn_send': 'Send to Suno …',
        'btn_save_links': 'Save links with the song',
        'btn_close': 'Close',
        'confirm': 'Send to Suno now?\n\nTitle: {title}\nStyle: {style} characters · Lyrics: {lyrics} characters\n\nSuno creates 2 songs and uses credits from your Suno account.',
        'no_song': 'Please select a song first.',
        'empty': 'This prompt has no lyrics. Suno’s custom mode needs lyrics.',
        'too_long': 'The prompt exceeds Suno’s limits (title 256, style 1,000, lyrics 5,000 characters).',
        'sending': '… sending to Suno. This can take a few minutes.',
        'done': '✔ Suno created {count} song(s):',
        'no_clips': 'Suno accepted the request but returned no song links. Please check your Suno library.',
        'mismatch': '⚠ Claude did not send the prompt exactly as saved in MPW. Please check the song in Suno.',
        'multiple': '⚠ Claude called audio-create more than once. With the same request key Suno does not charge twice; please still check your library.',
        'not_connected': 'Suno is not connected in Claude Code (status: {status}). Use “Add Suno …” or “Sign in to Suno …” under Configuration › AI connections.',
        'not_sent': 'Claude did not call audio-create. Nothing was created.',
        'error': 'Sending to Suno failed:\n{detail}',
        'timeout': 'No answer within {minutes} minutes. Suno may still have created the songs – please check your Suno library.',
        'links_saved': '{count} link(s) saved with the song (Media & Player).',
        'link_label': 'Suno – {title} ({index}/{count})',
    },
    'fr': {
        'button': 'Envoyer à Suno (MCP) …',
        'tooltip': 'Envoyer un prompt enregistré de ce morceau à Suno via Claude Code et le serveur MCP de Suno.',
        'title': 'Envoyer à Suno – {song}',
        'prompt_label': 'Prompt enregistré :',
        'active': 'Prompt actif du morceau (enregistré)',
        'version': 'Version n° {id} · {provider} · {created}',
        'title_label': 'Titre chez Suno :',
        'style_label': 'Style ({count}/1 000)',
        'lyrics_label': 'Paroles ({count}/5 000)',
        'info': 'Claude Code transmet le prompt sans modification au serveur MCP de Suno (audio-create, mode personnalisé). Suno crée 2 morceaux et consomme des crédits de votre compte Suno. Prérequis : Claude Code connecté et Suno relié (Configuration › Connexions IA).',
        'unsaved': '⚠ L’éditeur contient des modifications non enregistrées. C’est la version enregistrée qui est envoyée.',
        'btn_send': 'Envoyer à Suno …',
        'btn_save_links': 'Enregistrer les liens avec le morceau',
        'btn_close': 'Fermer',
        'confirm': 'Envoyer à Suno maintenant ?\n\nTitre : {title}\nStyle : {style} caractères · Paroles : {lyrics} caractères\n\nSuno crée 2 morceaux et consomme des crédits de votre compte Suno.',
        'no_song': 'Veuillez d’abord sélectionner un morceau.',
        'empty': 'Ce prompt n’a pas de paroles. Le mode personnalisé de Suno en exige.',
        'too_long': 'Le prompt dépasse les limites de Suno (titre 256, style 1 000, paroles 5 000 caractères).',
        'sending': '… envoi à Suno. Cela peut prendre quelques minutes.',
        'done': '✔ Suno a créé {count} morceau(x) :',
        'no_clips': 'Suno a accepté la demande mais n’a renvoyé aucun lien. Veuillez vérifier votre bibliothèque Suno.',
        'mismatch': '⚠ Claude n’a pas transmis le prompt exactement comme enregistré dans MPW. Vérifiez le morceau dans Suno.',
        'multiple': '⚠ Claude a appelé audio-create plusieurs fois. Avec la même clé de requête, Suno ne facture pas deux fois ; vérifiez tout de même la bibliothèque.',
        'not_connected': 'Suno n’est pas relié dans Claude Code (état : {status}). Utilisez « Ajouter Suno … » ou « Se connecter à Suno … » sous Configuration › Connexions IA.',
        'not_sent': 'Claude n’a pas appelé audio-create. Rien n’a été créé.',
        'error': 'L’envoi à Suno a échoué :\n{detail}',
        'timeout': 'Aucune réponse en {minutes} minutes. Suno a peut-être quand même créé les morceaux – vérifiez votre bibliothèque Suno.',
        'links_saved': '{count} lien(s) enregistré(s) avec le morceau (Médias & lecteur).',
        'link_label': 'Suno – {title} ({index}/{count})',
    },
    'es': {
        'button': 'Enviar a Suno (MCP) …',
        'tooltip': 'Enviar un prompt guardado de esta canción a Suno mediante Claude Code y el servidor MCP de Suno.',
        'title': 'Enviar a Suno – {song}',
        'prompt_label': 'Prompt guardado:',
        'active': 'Prompt activo de la canción (guardado)',
        'version': 'Versión n.º {id} · {provider} · {created}',
        'title_label': 'Título en Suno:',
        'style_label': 'Style ({count}/1.000)',
        'lyrics_label': 'Letra ({count}/5.000)',
        'info': 'Claude Code envía el prompt sin cambios al servidor MCP de Suno (audio-create, modo personalizado). Suno crea 2 canciones y consume créditos de su cuenta de Suno. Requisito: Claude Code con sesión iniciada y Suno conectado (Configuración › Conexiones de IA).',
        'unsaved': '⚠ El editor tiene cambios sin guardar. Se envía la versión guardada.',
        'btn_send': 'Enviar a Suno …',
        'btn_save_links': 'Guardar enlaces en la canción',
        'btn_close': 'Cerrar',
        'confirm': '¿Enviar a Suno ahora?\n\nTítulo: {title}\nStyle: {style} caracteres · Letra: {lyrics} caracteres\n\nSuno crea 2 canciones y consume créditos de su cuenta de Suno.',
        'no_song': 'Primero seleccione una canción.',
        'empty': 'Este prompt no tiene letra. El modo personalizado de Suno la necesita.',
        'too_long': 'El prompt supera los límites de Suno (título 256, style 1.000, letra 5.000 caracteres).',
        'sending': '… enviando a Suno. Puede tardar unos minutos.',
        'done': '✔ Suno creó {count} canción(es):',
        'no_clips': 'Suno aceptó la solicitud pero no devolvió enlaces. Revise su biblioteca de Suno.',
        'mismatch': '⚠ Claude no envió el prompt exactamente como está guardado en MPW. Revise la canción en Suno.',
        'multiple': '⚠ Claude llamó a audio-create varias veces. Con la misma clave de solicitud Suno no cobra dos veces; aun así revise la biblioteca.',
        'not_connected': 'Suno no está conectado en Claude Code (estado: {status}). Use «Añadir Suno …» o «Iniciar sesión en Suno …» en Configuración › Conexiones de IA.',
        'not_sent': 'Claude no llamó a audio-create. No se creó nada.',
        'error': 'El envío a Suno falló:\n{detail}',
        'timeout': 'Sin respuesta en {minutes} minutos. Puede que Suno haya creado las canciones igualmente: revise su biblioteca de Suno.',
        'links_saved': '{count} enlace(s) guardado(s) en la canción (Medios y reproductor).',
        'link_label': 'Suno – {title} ({index}/{count})',
    },
    'it': {
        'button': 'Invia a Suno (MCP) …',
        'tooltip': 'Invia un prompt salvato di questo brano a Suno tramite Claude Code e il server MCP di Suno.',
        'title': 'Invia a Suno – {song}',
        'prompt_label': 'Prompt salvato:',
        'active': 'Prompt attivo del brano (salvato)',
        'version': 'Versione n. {id} · {provider} · {created}',
        'title_label': 'Titolo su Suno:',
        'style_label': 'Style ({count}/1.000)',
        'lyrics_label': 'Testo ({count}/5.000)',
        'info': 'Claude Code invia il prompt senza modifiche al server MCP di Suno (audio-create, modalità personalizzata). Suno crea 2 brani e consuma crediti del tuo account Suno. Requisito: Claude Code con accesso eseguito e Suno connesso (Configurazione › Connessioni IA).',
        'unsaved': '⚠ L’editor contiene modifiche non salvate. Viene inviata la versione salvata.',
        'btn_send': 'Invia a Suno …',
        'btn_save_links': 'Salva i link nel brano',
        'btn_close': 'Chiudi',
        'confirm': 'Inviare ora a Suno?\n\nTitolo: {title}\nStyle: {style} caratteri · Testo: {lyrics} caratteri\n\nSuno crea 2 brani e consuma crediti del tuo account Suno.',
        'no_song': 'Seleziona prima un brano.',
        'empty': 'Questo prompt non ha testo. La modalità personalizzata di Suno lo richiede.',
        'too_long': 'Il prompt supera i limiti di Suno (titolo 256, style 1.000, testo 5.000 caratteri).',
        'sending': '… invio a Suno in corso. Può richiedere alcuni minuti.',
        'done': '✔ Suno ha creato {count} brano/i:',
        'no_clips': 'Suno ha accettato la richiesta ma non ha restituito link. Controlla la tua libreria Suno.',
        'mismatch': '⚠ Claude non ha inviato il prompt esattamente come salvato in MPW. Controlla il brano in Suno.',
        'multiple': '⚠ Claude ha chiamato audio-create più volte. Con la stessa chiave di richiesta Suno non addebita due volte; controlla comunque la libreria.',
        'not_connected': 'Suno non è connesso in Claude Code (stato: {status}). Usa «Aggiungi Suno …» o «Accedi a Suno …» in Configurazione › Connessioni IA.',
        'not_sent': 'Claude non ha chiamato audio-create. Non è stato creato nulla.',
        'error': 'Invio a Suno non riuscito:\n{detail}',
        'timeout': 'Nessuna risposta entro {minutes} minuti. Suno potrebbe aver comunque creato i brani: controlla la tua libreria Suno.',
        'links_saved': '{count} link salvato/i nel brano (Media & Player).',
        'link_label': 'Suno – {title} ({index}/{count})',
    },
}


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


def suno_prompt_choices(con, sid):
    """Saved prompts of a song for Suno: the saved active prompt first, then versions (newest first)."""
    row = con.execute('SELECT style,lyrics FROM songs WHERE id=?', (sid,)).fetchone()
    if row is None:
        return []
    choices = [{'version_id': None, 'provider': '', 'created': '', 'style': row[0] or '', 'lyrics': row[1] or ''}]
    for vid, provider, created, style, lyrics in con.execute(
            'SELECT id,provider,created_at,style,lyrics FROM prompt_versions WHERE song_id=? ORDER BY id DESC', (sid,)):
        choices.append({'version_id': vid, 'provider': provider or '', 'created': created or '',
                        'style': style or '', 'lyrics': lyrics or ''})
    return choices


def suno_send_problem(arguments):
    """Text key if the arguments cannot be sent ('empty', 'too_long'), else None."""
    if not arguments.get('lyrics'):
        return 'empty'
    if any(len(arguments.get(k, '')) > limit for k, limit in SUNO_LIMITS.items()):
        return 'too_long'
    return None


def suno_send_outcome(result, arguments):
    """Language-neutral result of a send: outcome text key + values, notes and the songs.

    Outcomes: provider_error (kind/code/detail), timeout, not_connected, error, not_sent, done, no_clips.
    """
    if result.get('provider_error'):
        kind, code, detail = result['provider_error']
        if kind == 'cli_timeout':
            return {'outcome': 'timeout', 'values': {'minutes': SUNO_SEND_TIMEOUT_SECONDS // 60}, 'notes': [], 'clips': []}
        return {'outcome': 'provider_error', 'values': {'kind': kind, 'code': code, 'detail': detail},
                'notes': [], 'clips': []}
    if result.get('mcp_status') not in (None, 'connected'):
        return {'outcome': 'not_connected', 'values': {'status': result['mcp_status']}, 'notes': [], 'clips': []}
    sent = result.get('create_inputs') or []
    if not sent:
        detail = '\n'.join(result.get('errors') or []) or result.get('final_error') or result.get('stderr') or ''
        return {'outcome': 'error' if detail else 'not_sent', 'values': {'detail': detail}, 'notes': [], 'clips': []}
    notes = []
    if not all(suno_send_matches(item, arguments) for item in sent):
        notes.append('mismatch')
    if len(sent) > 1:
        notes.append('multiple')
    clips = suno_clips(result)
    if result.get('errors') and not clips:
        return {'outcome': 'error', 'values': {'detail': '\n'.join(result['errors'])}, 'notes': [], 'clips': []}
    return {'outcome': 'done' if clips else 'no_clips', 'values': {'count': len(clips)}, 'notes': notes, 'clips': clips}


def save_suno_links(con, sid, title, clips, label_template='Suno – {title} ({index}/{count})'):
    """Store the Suno song links with the song (Medien & Player); existing links are kept."""
    with_url = [clip for clip in clips if clip.get('url')]
    added = 0
    with con:
        for index, clip in enumerate(with_url, 1):
            label = label_template.format(title=clip.get('title') or title, index=index, count=len(with_url))
            cursor = con.execute('INSERT OR IGNORE INTO media_links(song_id,platform,url,label) VALUES(?,?,?,?)',
                                 (sid, 'Suno', clip['url'], label))
            added += cursor.rowcount
    return added


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
# AI Prompt Launcher: shared rules (desktop tab and browser GUI).
# ---------------------------------------------------------------------------
AI_PROVIDERS = ('ChatGPT', 'Gemini', 'Claude')
AI_DEFAULT_MODELS = {'ChatGPT': 'gpt-4.1-mini', 'Gemini': 'gemini-2.5-flash', 'Claude': 'claude-sonnet-5-5'}
AI_PLATFORM_URLS = {'ChatGPT': 'https://chatgpt.com/', 'Gemini': 'https://gemini.google.com/',
                    'Claude': 'https://claude.ai/'}
API_MODEL_PATTERN = re.compile(r'[a-zA-Z0-9._-]+')
STYLE_LIMIT, LYRICS_LIMIT, BRIEF_LIMIT = 1000, 5000, 4000
# Localized error texts for ProviderError kinds; {provider}, {code} and {model} are filled in,
# the provider's own message is appended separately as detail.
AI_API_ERROR_TEXTS = {
    'de': {
        'auth': '{provider} hat den API-Schlüssel abgelehnt (HTTP {code}). Schlüssel prüfen und ob er für diese API freigeschaltet ist.',
        'model': '{provider} kennt das Modell „{model}“ nicht oder es ist für dieses Konto nicht verfügbar (HTTP {code}). Modellnamen im Feld „API-Modell“ prüfen.',
        'rate': '{provider} hat die Anfrage begrenzt (HTTP {code}): zu viele Anfragen oder kein Guthaben/Kontingent mehr. Später erneut versuchen oder Abrechnung prüfen.',
        'bad_request': '{provider} hat die Anfrage als ungültig abgelehnt (HTTP {code}). Modellnamen und API-Schlüssel prüfen.',
        'server': '{provider} ist gerade gestört oder überlastet (HTTP {code}). Bitte später erneut versuchen.',
        'http': '{provider} hat mit HTTP {code} geantwortet.',
        'network': '{provider} ist nicht erreichbar. Internetverbindung, Proxy oder Firewall prüfen.',
        'timeout': '{provider} hat nicht innerhalb von 180 Sekunden geantwortet. Bitte erneut versuchen.',
        'blocked': '{provider} hat die Antwort aus Sicherheitsgründen blockiert oder verweigert. Songidee umformulieren und erneut versuchen.',
        'truncated': 'Die Antwort von {provider} wurde abgeschnitten (Längenlimit erreicht) und wurde nicht übernommen. Bitte erneut versuchen.',
        'empty': '{provider} hat eine leere Antwort geliefert. Bitte erneut versuchen.',
        'format': '{provider} hat eine Antwort in unerwartetem Format geliefert. Modellnamen prüfen.',
        'unexpected': 'Unerwarteter Fehler bei der Anfrage an {provider}. Details stehen im Fehlerprotokoll.',
        'detail': 'Meldung des Anbieters:', 'status': 'API-Anfrage fehlgeschlagen.',
    },
    'en': {
        'auth': '{provider} rejected the API key (HTTP {code}). Check the key and that it is enabled for this API.',
        'model': '{provider} does not know the model “{model}” or it is not available for this account (HTTP {code}). Check the name in “API model”.',
        'rate': '{provider} rate-limited the request (HTTP {code}): too many requests or no credit/quota left. Try again later or check billing.',
        'bad_request': '{provider} rejected the request as invalid (HTTP {code}). Check the model name and API key.',
        'server': '{provider} is currently unavailable or overloaded (HTTP {code}). Please try again later.',
        'http': '{provider} responded with HTTP {code}.',
        'network': '{provider} cannot be reached. Check your internet connection, proxy or firewall.',
        'timeout': '{provider} did not respond within 180 seconds. Please try again.',
        'blocked': '{provider} blocked or refused the answer for safety reasons. Rephrase the song idea and try again.',
        'truncated': 'The answer from {provider} was cut off (length limit reached) and was not applied. Please try again.',
        'empty': '{provider} returned an empty answer. Please try again.',
        'format': '{provider} returned an answer in an unexpected format. Check the model name.',
        'unexpected': 'Unexpected error while contacting {provider}. Details are in the error log.',
        'detail': 'Provider message:', 'status': 'API request failed.',
    },
    'fr': {
        'auth': '{provider} a refusé la clé API (HTTP {code}). Vérifiez la clé et qu’elle est activée pour cette API.',
        'model': '{provider} ne connaît pas le modèle « {model} » ou il n’est pas disponible pour ce compte (HTTP {code}). Vérifiez le nom dans « Modèle API ».',
        'rate': '{provider} a limité la requête (HTTP {code}) : trop de requêtes ou plus de crédit/quota. Réessayez plus tard ou vérifiez la facturation.',
        'bad_request': '{provider} a refusé la requête comme non valide (HTTP {code}). Vérifiez le nom du modèle et la clé API.',
        'server': '{provider} est actuellement indisponible ou surchargé (HTTP {code}). Réessayez plus tard.',
        'http': '{provider} a répondu avec HTTP {code}.',
        'network': '{provider} est injoignable. Vérifiez la connexion Internet, le proxy ou le pare-feu.',
        'timeout': '{provider} n’a pas répondu en 180 secondes. Veuillez réessayer.',
        'blocked': '{provider} a bloqué ou refusé la réponse pour des raisons de sécurité. Reformulez l’idée et réessayez.',
        'truncated': 'La réponse de {provider} a été tronquée (limite de longueur atteinte) et n’a pas été reprise. Veuillez réessayer.',
        'empty': '{provider} a renvoyé une réponse vide. Veuillez réessayer.',
        'format': '{provider} a renvoyé une réponse dans un format inattendu. Vérifiez le nom du modèle.',
        'unexpected': 'Erreur inattendue lors de la requête à {provider}. Détails dans le journal des erreurs.',
        'detail': 'Message du fournisseur :', 'status': 'La requête API a échoué.',
    },
    'es': {
        'auth': '{provider} rechazó la clave API (HTTP {code}). Compruebe la clave y que esté habilitada para esta API.',
        'model': '{provider} no conoce el modelo «{model}» o no está disponible para esta cuenta (HTTP {code}). Compruebe el nombre en «Modelo API».',
        'rate': '{provider} limitó la solicitud (HTTP {code}): demasiadas solicitudes o sin saldo/cuota. Inténtelo más tarde o revise la facturación.',
        'bad_request': '{provider} rechazó la solicitud por no válida (HTTP {code}). Compruebe el nombre del modelo y la clave API.',
        'server': '{provider} no está disponible o está sobrecargado (HTTP {code}). Inténtelo más tarde.',
        'http': '{provider} respondió con HTTP {code}.',
        'network': 'No se puede conectar con {provider}. Compruebe la conexión a Internet, el proxy o el cortafuegos.',
        'timeout': '{provider} no respondió en 180 segundos. Inténtelo de nuevo.',
        'blocked': '{provider} bloqueó o rechazó la respuesta por motivos de seguridad. Reformule la idea e inténtelo de nuevo.',
        'truncated': 'La respuesta de {provider} se cortó (límite de longitud alcanzado) y no se aplicó. Inténtelo de nuevo.',
        'empty': '{provider} devolvió una respuesta vacía. Inténtelo de nuevo.',
        'format': '{provider} devolvió una respuesta con un formato inesperado. Compruebe el nombre del modelo.',
        'unexpected': 'Error inesperado al contactar con {provider}. Los detalles están en el registro de errores.',
        'detail': 'Mensaje del proveedor:', 'status': 'La solicitud API ha fallado.',
    },
    'it': {
        'auth': '{provider} ha rifiutato la chiave API (HTTP {code}). Controlla la chiave e che sia abilitata per questa API.',
        'model': '{provider} non conosce il modello «{model}» o non è disponibile per questo account (HTTP {code}). Controlla il nome in «Modello API».',
        'rate': '{provider} ha limitato la richiesta (HTTP {code}): troppe richieste o credito/quota esauriti. Riprova più tardi o controlla la fatturazione.',
        'bad_request': '{provider} ha rifiutato la richiesta come non valida (HTTP {code}). Controlla il nome del modello e la chiave API.',
        'server': '{provider} è momentaneamente non disponibile o sovraccarico (HTTP {code}). Riprova più tardi.',
        'http': '{provider} ha risposto con HTTP {code}.',
        'network': '{provider} non è raggiungibile. Controlla la connessione Internet, il proxy o il firewall.',
        'timeout': '{provider} non ha risposto entro 180 secondi. Riprova.',
        'blocked': '{provider} ha bloccato o rifiutato la risposta per motivi di sicurezza. Riformula l’idea e riprova.',
        'truncated': 'La risposta di {provider} è stata troncata (limite di lunghezza raggiunto) e non è stata applicata. Riprova.',
        'empty': '{provider} ha restituito una risposta vuota. Riprova.',
        'format': '{provider} ha restituito una risposta in un formato inatteso. Controlla il nome del modello.',
        'unexpected': 'Errore imprevisto nella richiesta a {provider}. I dettagli sono nel registro degli errori.',
        'detail': 'Messaggio del fornitore:', 'status': 'Richiesta API non riuscita.',
    },
}
# CLI access (local provider CLI); {code} is the process exit code.
AI_CLI_ERROR_TEXTS = {
    'de': {
        'cli_invalid': 'Ungültiger CLI-Befehl oder CLI-Modell. Nur Programmname bzw. Pfad ohne Sonderzeichen wie & | < > ^ % eintragen.',
        'cli_missing': 'Die {provider}-CLI wurde nicht gefunden. CLI installieren (z. B. Claude Code, Gemini CLI oder Codex CLI) oder im Feld „CLI-Befehl“ den vollständigen Pfad angeben.',
        'cli_start': 'Die {provider}-CLI konnte nicht gestartet werden.',
        'cli_failed': 'Die {provider}-CLI wurde mit Fehlercode {code} beendet. Ist die CLI angemeldet? Einmal in einem Terminal starten und einloggen, dann erneut versuchen.',
        'cli_timeout': 'Die {provider}-CLI hat nicht innerhalb von 5 Minuten geantwortet und wurde abgebrochen.',
    },
    'en': {
        'cli_invalid': 'Invalid CLI command or CLI model. Enter only a program name or path without special characters such as & | < > ^ %.',
        'cli_missing': 'The {provider} CLI was not found. Install the CLI (e.g. Claude Code, Gemini CLI or Codex CLI) or enter its full path in “CLI command”.',
        'cli_start': 'The {provider} CLI could not be started.',
        'cli_failed': 'The {provider} CLI exited with error code {code}. Is the CLI signed in? Start it once in a terminal, sign in, then try again.',
        'cli_timeout': 'The {provider} CLI did not respond within 5 minutes and was stopped.',
    },
    'fr': {
        'cli_invalid': 'Commande CLI ou modèle CLI non valide. Saisissez uniquement un nom de programme ou un chemin sans caractères spéciaux comme & | < > ^ %.',
        'cli_missing': 'La CLI {provider} est introuvable. Installez la CLI (p. ex. Claude Code, Gemini CLI ou Codex CLI) ou indiquez son chemin complet dans « Commande CLI ».',
        'cli_start': 'La CLI {provider} n’a pas pu être démarrée.',
        'cli_failed': 'La CLI {provider} s’est terminée avec le code d’erreur {code}. La CLI est-elle connectée ? Lancez-la une fois dans un terminal, connectez-vous, puis réessayez.',
        'cli_timeout': 'La CLI {provider} n’a pas répondu en 5 minutes et a été arrêtée.',
    },
    'es': {
        'cli_invalid': 'Comando CLI o modelo CLI no válido. Introduzca solo un nombre de programa o una ruta sin caracteres especiales como & | < > ^ %.',
        'cli_missing': 'No se encontró la CLI de {provider}. Instale la CLI (p. ej. Claude Code, Gemini CLI o Codex CLI) o indique su ruta completa en «Comando CLI».',
        'cli_start': 'No se pudo iniciar la CLI de {provider}.',
        'cli_failed': 'La CLI de {provider} terminó con el código de error {code}. ¿Ha iniciado sesión en la CLI? Iníciela una vez en un terminal, inicie sesión y vuelva a intentarlo.',
        'cli_timeout': 'La CLI de {provider} no respondió en 5 minutos y se detuvo.',
    },
    'it': {
        'cli_invalid': 'Comando CLI o modello CLI non valido. Inserisci solo il nome del programma o un percorso senza caratteri speciali come & | < > ^ %.',
        'cli_missing': 'La CLI di {provider} non è stata trovata. Installa la CLI (ad es. Claude Code, Gemini CLI o Codex CLI) o indica il percorso completo in «Comando CLI».',
        'cli_start': 'Impossibile avviare la CLI di {provider}.',
        'cli_failed': 'La CLI di {provider} è terminata con il codice di errore {code}. La CLI ha effettuato l’accesso? Avviala una volta in un terminale, accedi e riprova.',
        'cli_timeout': 'La CLI di {provider} non ha risposto entro 5 minuti ed è stata interrotta.',
    },
}
AI_ERROR_TEXTS = {lang: {**AI_API_ERROR_TEXTS[lang], **AI_CLI_ERROR_TEXTS[lang]} for lang in AI_API_ERROR_TEXTS}


_JSON_ANSWER_RULE = ('Antworte ausschließlich als JSON-Objekt mit den Schlüsseln "style" und "lyrics" '
                     '(beide Strings). Keine Markdown-Codeblöcke.')


def ai_cli_prompt(prompt):
    """Same request as the API mode, plus a note that no files or tools are needed."""
    return prompt + '\nArbeite ohne Werkzeuge und ohne Dateizugriff; gib nur das JSON-Objekt als Antwort aus.'


def ai_browser_prompt(prompt):
    """Browser workflow (copy & paste into the chat): two copy boxes instead of API-only JSON."""
    return prompt.replace(_JSON_ANSWER_RULE,
                          'Erstelle den Prompt in zwei separaten Copy-Boxen. '
                          'Die erste Copy-Box enthält ausschließlich den Style, die zweite ausschließlich die Lyrics. '
                          'Beschrifte sie mit STYLE und LYRICS.')


def project_song_id(con, project_id):
    """Existing song entry of a project (the AI target), without changing anything."""
    row = con.execute('SELECT id FROM songs WHERE project_id=? ORDER BY id LIMIT 1', (project_id,)).fetchone()
    return row[0] if row else None


def ensure_project_song(con, project_id):
    """Create the missing song entry of a project (title = project name); no files are touched."""
    row = con.execute('SELECT name FROM projects WHERE id=?', (project_id,)).fetchone()
    if row is None:
        raise BandDataError('project_missing')
    existing = project_song_id(con, project_id)
    if existing is not None:
        return existing, False
    with con:
        new_id = con.execute('INSERT INTO songs(project_id,title) VALUES(?,?)', (project_id, row[0])).lastrowid
    return new_id, True


def save_prompt_version(con, sid, provider, model, style, lyrics, brief=''):
    """Store a reviewed Style/Lyrics pair as a new prompt version; the active song stays unchanged."""
    style = _clean_text(style, 'style', STYLE_LIMIT)
    lyrics = _clean_text(lyrics, 'lyrics', LYRICS_LIMIT)
    brief = _clean_text(brief, 'brief', BRIEF_LIMIT, required=False)
    if provider not in AI_PROVIDERS:
        raise BandDataError('invalid_provider')
    model = _clean_text(model, 'model', 120, required=False)
    if con.execute('SELECT 1 FROM songs WHERE id=?', (sid,)).fetchone() is None:
        raise BandDataError('song_missing')
    with con:
        return con.execute('INSERT INTO prompt_versions(song_id,provider,model,style,lyrics,brief) VALUES(?,?,?,?,?,?)',
                           (sid, provider, model, style, lyrics, brief)).lastrowid


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
