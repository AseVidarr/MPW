import ast
import unittest
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / 'source' / 'workstation.py'

class BandsTranslationHotfix3(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SOURCE.read_text(encoding='utf-8')
        cls.tree = ast.parse(cls.source)

    def test_four_languages_have_field_translations(self):
        for key in ('Band / Künstler', 'Hauptgenre', 'Zweitgenre', 'Gruppe'):
            self.assertIn(repr(key) + ':', self.source)
        for lang in ('en', 'fr', 'es', 'it'):
            self.assertIn(repr(lang) + ': {', self.source)

    def test_preset_actions_translated(self):
        for key in ('Band-Hardware als Preset speichern', 'Preset auf Band anwenden', 'Preset löschen'):
            self.assertGreaterEqual(self.source.count(repr(key)), 2)

    def test_existing_generic_translation_pipeline_preserved(self):
        self.assertIn('UI_FIELD_TRANSLATIONS[_lang].update(_items)', self.source)
        self.assertIn('UI_CONTROL_TRANSLATIONS[_lang].update(_items)', self.source)
        self.assertIn('mpw_original_field_text', self.source)
        self.assertIn('mpw_original_button_text', self.source)

if __name__ == '__main__':
    unittest.main()
