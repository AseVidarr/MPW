from contextlib import contextmanager
import importlib.util
import sqlite3
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/verify-sqlite-upgrade.py'
spec = importlib.util.spec_from_file_location('sqlite_upgrade_p46', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

@contextmanager
def connect(path):
    """Commit and always close; a bare `with sqlite3.connect()` leaves the file locked on Windows."""
    con = sqlite3.connect(path)
    try:
        with con:
            yield con
    finally:
        con.close()

class MPWSchemaMediaP46(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.db = self.root / 'mpw.sqlite'
        with connect(self.db) as con:
            con.execute('CREATE TABLE media_assets(id INTEGER PRIMARY KEY, relative_path TEXT)')
            con.execute('CREATE TABLE albums(id INTEGER PRIMARY KEY, cover_path TEXT)')
    def put(self, table, path):
        col = 'relative_path' if table == 'media_assets' else 'cover_path'
        with connect(self.db) as con:
            con.execute(f'INSERT INTO {table}({col}) VALUES(?)', (path,))
    def test_valid_relative_media(self):
        (self.root/'media').mkdir()
        (self.root/'media'/'song.wav').write_bytes(b'data')
        self.put('media_assets', 'media/song.wav')
        r = module.inspect_database(self.db, mpw_root=self.root)
        self.assertTrue(r['ok'])
        self.assertEqual(r['mpw_relative_paths_checked'], 1)
    def test_missing_relative_cover(self):
        self.put('albums', 'covers/absent.png')
        r = module.inspect_database(self.db, mpw_root=self.root)
        self.assertFalse(r['ok'])
        self.assertEqual(len(r['missing_mpw_media']), 1)
    def test_missing_root_is_not_silently_accepted(self):
        self.put('media_assets', 'media/song.wav')
        r = module.inspect_database(self.db)
        self.assertFalse(r['ok'])
        self.assertEqual(r['mpw_relative_paths_unresolved'], 1)
    def test_path_escape_rejected(self):
        self.put('media_assets', '../outside.wav')
        r = module.inspect_database(self.db, mpw_root=self.root)
        self.assertFalse(r['ok'])
        self.assertEqual(len(r['unsafe_mpw_paths']), 1)
    def test_existing_album_cover(self):
        (self.root/'covers').mkdir()
        (self.root/'covers'/'art.png').write_bytes(b'png')
        self.put('albums', 'covers/art.png')
        self.assertTrue(module.inspect_database(self.db, mpw_root=self.root)['ok'])

if __name__ == '__main__': unittest.main()
