"""Preview 40: isolated persistence and language recovery regression tests."""
import ast
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[1] / 'source' / 'workstation.py'
TREE = ast.parse(SOURCE.read_text(encoding='utf-8'))
APP = next(n for n in TREE.body if isinstance(n, ast.ClassDef) and n.name == 'Workstation')

def extract(*names, root):
    nodes = [n for n in APP.body if isinstance(n, ast.FunctionDef) and n.name in names]
    assert len(nodes) == len(names), 'Missing configuration method'
    class Locale:
        @staticmethod
        def system():
            class System:
                @staticmethod
                def name(): return 'fr_FR'
            return System()
    # app_configuration delegates to the Qt-free core (mpw_core.app_configuration)
    core_tree = ast.parse((SOURCE.parent / 'mpw_core.py').read_text(encoding='utf-8'))
    core_ns = {'ROOT': root, 'json': json, 'Path': Path}
    core_fn = [n for n in core_tree.body if isinstance(n, ast.FunctionDef) and n.name == 'app_configuration']
    exec(compile(ast.Module(body=core_fn, type_ignores=[]), 'mpw_core.py', 'exec'), core_ns)
    import types
    ns = {'ROOT': root, 'json': json, 'QLocale': Locale,
          'mpw_core': types.SimpleNamespace(app_configuration=core_ns['app_configuration'])}
    exec(compile(ast.fix_missing_locations(ast.Module(body=nodes, type_ignores=[])), str(SOURCE), 'exec'), ns)
    return ns

class PersistenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.ns = extract('app_configuration', 'save_app_configuration', 'effective_language', 'change_ui_language', root=self.root)
        class App:
            app_configuration = self.ns['app_configuration']
            save_app_configuration = self.ns['save_app_configuration']
            effective_language = self.ns['effective_language']
            change_ui_language = self.ns['change_ui_language']
            LANGUAGE_NAMES = ('de','en','fr','es','it')
            def error(self, message): raise AssertionError(message)
            def refresh_language_controls(self): self.refresh_count += 1
        self.app = App()
        self.app.refresh_count = 0
        self.path = self.root / 'app_configuration.json'

    def test_round_trip_each_language_and_auto(self):
        self.app.save_app_configuration(startup_tab='Songs & Suno', last_tab='Konfiguration', background_scaling='contain')
        for lang in ('de','en','fr','es','it','auto','de'):
            self.app.save_app_configuration(ui_language=lang)
            self.assertEqual(self.app.app_configuration()['ui_language'], lang)
            self.assertEqual(self.app.effective_language(), 'fr' if lang == 'auto' else lang)
            self.assertEqual(self.app.app_configuration()['startup_tab'], 'Songs & Suno')
            self.assertEqual(self.app.app_configuration()['background_scaling'], 'contain')
            self.assertFalse(self.path.with_suffix('.json.tmp').exists())

    def test_missing_invalid_and_non_object_config(self):
        self.assertEqual(self.app.app_configuration(), {})
        self.assertEqual(self.app.effective_language(), 'fr')
        for raw in ('{invalid', '[]', 'null', '"abc"'):
            self.path.write_text(raw, encoding='utf-8')
            self.assertEqual(self.app.app_configuration(), {})
        self.path.write_text('{"ui_language":"xx"}', encoding='utf-8')
        self.assertEqual(self.app.effective_language(), 'fr')

    def test_change_language_validates_and_refreshes(self):
        class Choice:
            value = 'de'
            def currentData(self): return self.value
        self.app.language_choice = Choice()
        for value in ('de','en','fr','es','it','auto'):
            self.app.language_choice.value = value
            self.app.change_ui_language()
            self.assertEqual(self.app.app_configuration()['ui_language'], value)
        self.assertEqual(self.app.refresh_count, 6)
        self.app.language_choice.value = 'invalid'
        self.app.change_ui_language()
        self.assertEqual(self.app.refresh_count, 6)
        self.assertEqual(self.app.app_configuration()['ui_language'], 'auto')

    def test_preserves_unrelated_preferences_and_unicode(self):
        prefs = {'startup_tab':'Plattensammlung', 'last_tab':'Medien & Player', 'custom_note':'Été – música 🎵', 'theme':'custom'}
        self.path.write_text(json.dumps(prefs, ensure_ascii=False), encoding='utf-8')
        self.app.save_app_configuration(ui_language='it')
        self.assertEqual(self.app.app_configuration(), {**prefs, 'ui_language':'it'})
        self.assertEqual(list(self.root.iterdir()), [self.path])

    def test_no_music_database_access_in_config_methods(self):
        for name in ('app_configuration','save_app_configuration','effective_language','change_ui_language'):
            method = next(n for n in APP.body if isinstance(n, ast.FunctionDef) and n.name == name)
            source = ast.unparse(method)
            for forbidden in ('sqlite3', 'self.con', 'self.db', 'DATABASE_PATH'):
                self.assertNotIn(forbidden, source)

if __name__ == '__main__': unittest.main()
