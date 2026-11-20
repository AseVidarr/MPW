import ast
import pathlib
import unittest

SOURCE = pathlib.Path(__file__).resolve().parents[1] / 'source' / 'workstation.py'

class GuideEnglishHF19Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SOURCE.read_text(encoding='utf-8')
        cls.tree = ast.parse(cls.source)
        cls.cls = next(n for n in cls.tree.body if isinstance(n, ast.ClassDef) and n.name == 'Workstation')

    def test_both_english_entries_present(self):
        assignment = next(n for n in self.cls.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'GUIDE_EN_HF19' for t in n.targets))
        data = ast.literal_eval(assignment.value)['Medien Explorer']
        self.assertEqual(set(data), {'Pfad kopieren', 'Nur lesender Medien Explorer'})
        for item in data.values():
            self.assertEqual(len(item['en']), 2)
            self.assertTrue(all(item['en']))

    def test_lookup_applies_new_entries_after_previous_translations(self):
        method = next(n for n in self.cls.body if isinstance(n, ast.FunctionDef) and n.name == '_guide_translation_lookup')
        text = ast.get_source_segment(self.source, method)
        self.assertIn("add(self.GUIDE_EN_HF18.get(name, {}))", text)
        self.assertIn("add(self.GUIDE_EN_HF19.get(name, {}))", text)
        self.assertLess(text.index('GUIDE_EN_HF18.get'), text.index('GUIDE_EN_HF19.get'))

    def test_original_german_guide_is_unchanged(self):
        self.assertIn('Pfad kopieren', self.source)
        self.assertIn('Nur lesender Medien Explorer', self.source)

if __name__ == '__main__':
    unittest.main()
