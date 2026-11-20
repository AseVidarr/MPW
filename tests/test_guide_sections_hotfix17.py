import ast, unittest
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / 'source' / 'workstation.py'

class GuideSectionsHotfix17(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SOURCE.read_text(encoding='utf-8')
        cls.tree = ast.parse(cls.source)
        cls.workstation = next(node for node in cls.tree.body if isinstance(node, ast.ClassDef) and node.name == 'Workstation')
        cls.attrs = {target.id: ast.literal_eval(node.value) for node in cls.workstation.body if isinstance(node, ast.Assign) for target in node.targets if isinstance(target, ast.Name) and target.id in ('DETAILED_TAB_GUIDES', 'GUIDE_MEDIA_EN_HF17', 'GUIDE_CANONICAL_SECTIONS_HF17')}
    def test_all_media_labels_covered(self):
        entries = self.attrs['DETAILED_TAB_GUIDES']['Medien & Player']
        self.assertTrue({label for _, label, _ in entries}.issubset(set(self.attrs['GUIDE_MEDIA_EN_HF17']) | {'Bezeichnung'}))
    def test_all_media_sections_have_english_translation(self):
        entries = self.attrs['DETAILED_TAB_GUIDES']['Medien & Player']
        sections = self.attrs['GUIDE_CANONICAL_SECTIONS_HF17']['Medien & Player']
        self.assertTrue(all('en' in sections[group] for group, _, _ in entries if group in sections))
    def test_renderer_uses_original_group_identity(self):
        self.assertIn('name, {}).get(original_group, {}).get(language, group)', self.source)
    def test_media_english_translation_has_no_german_fallback(self):
        for label, description in self.attrs['GUIDE_MEDIA_EN_HF17'].values():
            self.assertTrue(label and description)
            self.assertNotIn(' auswählen', description)

if __name__ == '__main__':
    unittest.main()
