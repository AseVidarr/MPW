import ast
import pathlib
import unittest

SOURCE = pathlib.Path(__file__).resolve().parents[1] / 'source' / 'workstation.py'

class BackupLanguageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = SOURCE.read_text(encoding='utf-8')
        cls.tree = ast.parse(cls.text)
        cls.workstation = next(n for n in cls.tree.body if isinstance(n, ast.ClassDef) and n.name == 'Workstation')
        cls.methods = {n.name: n for n in cls.workstation.body if isinstance(n, ast.FunctionDef)}

    def test_five_languages(self):
        assignment = next(n for n in self.workstation.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'BACKUP_I18N_HF12' for t in n.targets))
        translations = ast.literal_eval(assignment.value)
        self.assertEqual(set(translations), {'de','en','fr','es','it'})
        self.assertTrue(all(len(v)==11 for v in translations.values()))

    def test_refresh_wired_to_language_switch(self):
        method = ast.get_source_segment(self.text, self.methods['refresh_language_controls'])
        self.assertIn('self.refresh_backup_language_hf12()', method)

    def test_retention_keeps_original_data(self):
        method = ast.get_source_segment(self.text, self.methods['refresh_backup_language_hf12'])
        self.assertIn('itemData(i)', method)
        self.assertIn('blockSignals(True)', method)
        self.assertNotIn('setItemData(', method)

    def test_dynamic_status_translated(self):
        method = ast.get_source_segment(self.text, self.methods['update_backup_status'])
        self.assertIn('translate_backup_status_hf12', method)
        self.assertIn('newest.name', method)

if __name__ == '__main__':
    unittest.main()
