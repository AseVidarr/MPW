from contextlib import contextmanager
import importlib.util
import sqlite3
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/verify-sqlite-upgrade.py'
spec = importlib.util.spec_from_file_location('sqlite_upgrade', SCRIPT)
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

class SQLiteUpgradeP45(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.db = self.root / 'sample.sqlite'
        with connect(self.db) as conn:
            conn.execute('PRAGMA foreign_keys=ON')
            conn.execute('CREATE TABLE songs(id INTEGER PRIMARY KEY, file_path TEXT)')
            conn.execute('CREATE TABLE tags(song_id INTEGER REFERENCES songs(id))')
            conn.execute('INSERT INTO songs(id) VALUES(1)')
    def test_valid_database_and_counts(self):
        result = module.inspect_database(self.db)
        self.assertTrue(result['ok'])
        self.assertEqual(result['table_counts']['songs'], 1)
    def test_missing_media_detected(self):
        with connect(self.db) as conn:
            conn.execute('UPDATE songs SET file_path=? WHERE id=1',(str(self.root/'missing.wav'),))
        result = module.inspect_database(self.db)
        self.assertFalse(result['ok'])
        self.assertEqual(len(result['missing_media']),1)
    def test_existing_media_passes(self):
        media=self.root/'song.wav';media.write_bytes(b'audio')
        with connect(self.db) as conn:
            conn.execute('UPDATE songs SET file_path=? WHERE id=1',(str(media),))
        self.assertTrue(module.inspect_database(self.db)['ok'])
    def test_foreign_key_violations_detected(self):
        with connect(self.db) as conn:
            conn.execute('PRAGMA foreign_keys=OFF')
            conn.execute('INSERT INTO tags VALUES(999)')
        result=module.inspect_database(self.db)
        self.assertFalse(result['ok'])
        self.assertEqual(result['foreign_key_violations'],1)
    def test_report_does_not_overwrite_or_touch_db(self):
        before=self.db.read_bytes()
        report=self.root/'report.json'
        self.assertEqual(module.main([str(self.db),'--output',str(report)]),3)
        self.assertFalse(report.exists())
        self.assertEqual(before,self.db.read_bytes())
        external=self.root/'reports';external.mkdir()
        self.assertEqual(module.main([str(self.db),'--output',str(external/'report.json')]),0)
        self.assertEqual(before,self.db.read_bytes())
        self.assertEqual(module.main([str(self.db),'--output',str(external/'report.json')]),3)

if __name__ == '__main__': unittest.main()
