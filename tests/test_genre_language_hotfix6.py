import ast
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = (ROOT / 'source' / 'workstation.py').read_text(encoding='utf-8')
TREE = ast.parse(SOURCE)

class GenreLanguageHotfixTests(unittest.TestCase):
    def test_five_languages_defined(self):
        klass = next(n for n in TREE.body if isinstance(n, ast.ClassDef) and n.name == 'Workstation')
        assignment = next(n for n in klass.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'GENRE_STATIC_HF6' for t in n.targets))
        data = ast.literal_eval(assignment.value)
        self.assertEqual(set(data), {'de','en','fr','es','it'})
        self.assertTrue(all(len(v)==3 for v in data.values()))
    def test_language_refresh_wired(self):
        self.assertIn('self.refresh_genre_static_hf6()\n        self.refresh_suno_language_hf7()\n        self.refresh_project_display_hf5()', SOURCE)
    def test_user_genres_not_changed(self):
        klass = next(n for n in TREE.body if isinstance(n, ast.ClassDef) and n.name == 'Workstation')
        method = next(n for n in klass.body if isinstance(n, ast.FunctionDef) and n.name == 'refresh_genre_static_hf6')
        calls = [n.func.attr for n in ast.walk(method) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)]
        self.assertEqual(calls.count('setPlaceholderText'), 2)
        self.assertEqual(calls.count('setToolTip'), 1)
        self.assertNotIn('setText', calls)
        self.assertNotIn('addItems', calls)

if __name__ == '__main__': unittest.main()
