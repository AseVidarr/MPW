import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('startup_audit', ROOT/'scripts/audit-startup.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class StartupAuditTests(unittest.TestCase):
    def test_real_constructor(self):
        result = module.audit((ROOT/'source/workstation.py').read_text(encoding='utf-8'))
        self.assertGreaterEqual(result['build_count'], 14)
        self.assertFalse(result['issues'], result['issues'])
    def test_detects_uninitialized_dictionary(self):
        sample = "class Workstation:\n def __init__(self):\n  self.build_backup()\n def build_backup(self):\n  print(self.appearance_text_p35['note'])\n"
        self.assertTrue(module.audit(sample)['issues'])
    def test_does_not_touch_database(self):
        text = (ROOT/'scripts/audit-startup.py').read_text(encoding='utf-8')
        self.assertNotIn('sqlite3.connect', text)
        self.assertNotIn('PySide6', text.split('import ast')[1])

if __name__ == '__main__':
    unittest.main()
