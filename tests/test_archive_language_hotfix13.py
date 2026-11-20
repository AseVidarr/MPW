"""Static translation contracts; Qt runtime acceptance is performed on Windows."""
import ast
import unittest
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / 'source' / 'workstation.py'

class ArchiveLanguageHotfix13Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = SOURCE.read_text(encoding='utf-8')
        tree = ast.parse(cls.text)
        cls.class_node = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'Workstation')
        cls.attrs = {}
        for node in cls.class_node.body:
            if isinstance(node, ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Name) and node.targets[0].id in ('ARCHIVE_I18N_HF13','ARCHIVE_COMBOS_HF13'):
                cls.attrs[node.targets[0].id] = ast.literal_eval(node.value)

    def test_all_languages_have_identical_archive_keys(self):
        translations = self.attrs['ARCHIVE_I18N_HF13']
        self.assertEqual(set(translations), {'de','en','fr','es','it'})
        self.assertTrue(all(set(v)==set(translations['de']) for v in translations.values()))
        self.assertIn('Archive management:', translations['en']['intro'])
        self.assertIn('Deletes all database', translations['en']['danger_note'])

    def test_all_languages_have_identical_filter_keys(self):
        translations = self.attrs['ARCHIVE_COMBOS_HF13']
        self.assertEqual(set(translations), {'de','en','fr','es','it'})
        self.assertTrue(all(set(v)==set(translations['de']) for v in translations.values()))
        self.assertEqual(translations['en']['new'], 'Newest first')

    def test_archive_language_refresh_is_wired(self):
        self.assertIn('self.refresh_archive_language_hf13()', self.text)
        self.assertIn('self.archive_sort_label_hf13 = QLabel', self.text)
        self.assertIn('self.archive_danger_note_hf13 = danger_note', self.text)
        self.assertIn('combo.blockSignals(True)', self.text)
        self.assertIn("'toggle_hide' if self.archive_toggle_hf13.isChecked() else 'toggle_show'", self.text)

if __name__ == '__main__': unittest.main()
