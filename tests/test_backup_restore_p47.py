"""Regression tests for the actual MPW backup/restore functions; only temporary files."""
import ast
from contextlib import closing, contextmanager
from datetime import datetime
import json
from pathlib import Path
import shutil
import sqlite3
import tempfile
import unittest
import zipfile

SOURCE = Path(__file__).resolve().parents[1] / 'source/mpw_core.py'  # backup functions live in the Qt-free core
NAMES = ('check_database_integrity', '_write_backup_archive', 'validate_backup', 'restore_backup')

def load_backup_functions():
    tree = ast.parse(SOURCE.read_text(encoding='utf-8'))
    funcs = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in NAMES]
    if {f.name for f in funcs} != set(NAMES):
        raise AssertionError('Backup functions missing')
    namespace = dict(Path=Path, sqlite3=sqlite3, tempfile=tempfile, shutil=shutil,
                     zipfile=zipfile, closing=closing, datetime=datetime, json=json)
    exec(compile(ast.Module(body=funcs, type_ignores=[]), str(SOURCE), 'exec'), namespace)
    return namespace

FN = load_backup_functions()

@contextmanager
def connect(path):
    """Commit and always close; a bare `with connect()` leaves the file locked on Windows."""
    con = sqlite3.connect(path)
    try:
        with con:
            yield con
    finally:
        con.close()

class BackupRestoreP47(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / 'mpw'
        self.root.mkdir()
        self.db = self.root / 'workstation.db'
        self.archive = self.base / 'backup.zip'
        self.create_database(self.db, 'before')

    @staticmethod
    def create_database(path, title):
        with connect(path) as con:
            for table in ('bands', 'projects', 'songs', 'releases', 'media_assets'):
                con.execute(f'CREATE TABLE {table} (id INTEGER PRIMARY KEY, title TEXT)')
            con.execute('INSERT INTO songs(title) VALUES (?)', (title,))

    def backup(self):
        with connect(self.db) as con:
            FN['_write_backup_archive'](con, self.root, self.archive)
        self.assertTrue(FN['validate_backup'](self.archive))

    def title(self):
        with connect(self.db) as con:
            return con.execute('SELECT title FROM songs').fetchone()[0]

    def test_valid_backup_restores_database_after_changes(self):
        self.backup()
        with connect(self.db) as con:
            con.execute("UPDATE songs SET title='changed'")
        FN['restore_backup'](self.archive, self.root)
        self.assertEqual(self.title(), 'before')

    def test_restore_preserves_external_media_and_settings(self):
        media = self.root / 'media' / 'song.wav'
        media.parent.mkdir()
        media.write_bytes(b'important-audio')
        settings = self.root / 'app_settings.json'
        settings.write_text('{"language":"fr"}', encoding='utf-8')
        self.backup()
        FN['restore_backup'](self.archive, self.root)
        self.assertEqual(media.read_bytes(), b'important-audio')
        self.assertEqual(settings.read_text(encoding='utf-8'), '{"language":"fr"}')

    def test_missing_required_tables_rejected_without_touching_live_db(self):
        with connect(self.base / 'wrong.db') as con:
            con.execute('CREATE TABLE unrelated (id INTEGER)')
        with zipfile.ZipFile(self.archive, 'w') as z:
            z.write(self.base / 'wrong.db', 'workstation.db')
        original = self.db.read_bytes()
        with self.assertRaises(ValueError):
            FN['restore_backup'](self.archive, self.root)
        self.assertEqual(self.db.read_bytes(), original)

    def test_archive_path_traversal_rejected_without_touching_live_db(self):
        self.backup()
        with zipfile.ZipFile(self.archive, 'a') as z:
            z.writestr('../escape.txt', 'bad')
        original = self.db.read_bytes()
        with self.assertRaises(ValueError):
            FN['restore_backup'](self.archive, self.root)
        self.assertEqual(self.db.read_bytes(), original)
        self.assertFalse((self.base / 'escape.txt').exists())

    def test_backup_contains_database_not_media(self):
        media = self.root / 'media' / 'track.wav'
        media.parent.mkdir()
        media.write_bytes(b'audio')
        self.backup()
        with zipfile.ZipFile(self.archive) as z:
            self.assertEqual(set(z.namelist()), {'workstation.db', 'backup_info.txt'})

if __name__ == '__main__':
    unittest.main()
