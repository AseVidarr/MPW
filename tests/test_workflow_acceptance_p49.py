import importlib.util
import sqlite3
import tempfile
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('workflow_audit', ROOT/'scripts/audit-workflows.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class WorkflowAcceptanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (ROOT/'source/mpw_core.py').read_text(encoding='utf-8')  # init_database, save_song_record
        cls.desktop = (ROOT/'source/workstation.py').read_text(encoding='utf-8')

    def test_real_schema_end_to_end(self):
        results = module.run(self.source)
        self.assertTrue(all(results.values()),results)
        self.assertGreaterEqual(len(results),7)

    def test_isolated_database_root(self):
        init = module.load_schema_initializer(self.source)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)/'isolated'
            con = init(root)
            try:
                self.assertEqual(con.execute('PRAGMA foreign_keys').fetchone()[0],1)
                self.assertTrue((root/'workstation.db').exists())
            finally: con.close()
        self.assertFalse(root.exists())

    def test_schema_change_detected(self):
        damaged = self.source.replace('CREATE TABLE IF NOT EXISTS prompt_versions(', 'CREATE TABLE IF NOT EXISTS removed_versions(')
        with self.assertRaises(sqlite3.OperationalError):
            module.run(damaged)

    def test_source_contains_atomic_prompt_history(self):
        # Since the browser GUI the rule lives in save_song_record, shared by desktop and web.
        shared = self.source[self.source.index('def save_song_record('):self.source.index('def preset_items_missing(')]
        self.assertIn('with con:', shared)
        self.assertIn('INSERT INTO prompt_versions', shared)
        desktop = self.desktop[self.desktop.index('    def save_song(self):'):self.desktop.index('    def show_production_dashboard(self):')]
        self.assertIn('save_song_record(self.con, sid,', desktop)

if __name__ == '__main__':
    unittest.main()
