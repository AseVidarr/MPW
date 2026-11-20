"""Preview 38: tab coverage, translation invariants, and language-refresh contracts."""
import ast
import re
import string
import unittest
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / "source" / "workstation.py"
TEXT = SOURCE.read_text(encoding="utf-8")
TREE = ast.parse(TEXT)
APP = next(n for n in TREE.body if isinstance(n, ast.ClassDef) and n.name == "Workstation")
LANGS = {"de", "en", "fr", "es", "it"}


def table(name):
    for n in APP.body:
        if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in n.targets):
            return ast.literal_eval(n.value)
    raise AssertionError(f"missing table: {name}")


def method(name):
    return next(n for n in APP.body if isinstance(n, ast.FunctionDef) and n.name == name)


def fields(value):
    return {field for _, field, _, _ in string.Formatter().parse(value) if field is not None}


class AllTabLanguageContracts(unittest.TestCase):
    def test_exactly_fourteen_tabs_with_unique_keys(self):
        calls = [n for n in ast.walk(APP) if isinstance(n, ast.Call)
                 and isinstance(n.func, ast.Attribute) and n.func.attr == "addTab"
                 and isinstance(n.func.value, ast.Attribute) and n.func.value.attr == "tabs"
                 and len(n.args) >= 2 and isinstance(n.args[1], ast.Constant)]
        names = [n.args[1].value for n in calls]
        self.assertEqual(len(names), 14, names)
        self.assertEqual(len(set(names)), 14, names)
        self.assertTrue(all(isinstance(x, str) and x.strip() for x in names))
        self.assertEqual(len(names), 14)

    def test_all_tabs_have_five_language_labels(self):
        names = [n.args[1].value for n in ast.walk(APP) if isinstance(n, ast.Call)
                 and isinstance(n.func, ast.Attribute) and n.func.attr == "addTab"
                 and isinstance(n.func.value, ast.Attribute) and n.func.value.attr == "tabs"
                 and len(n.args) >= 2 and isinstance(n.args[1], ast.Constant)]
        sections = table("UI_SECTION_TRANSLATIONS")
        self.assertEqual(set(sections), LANGS - {"de"})
        for lang in LANGS - {"de"}:
            for name in names:
                self.assertIn(name, sections[lang], (lang, name))
                self.assertTrue(sections[lang][name].strip(), (lang, name))

    def test_core_translation_dictionaries_keep_same_keys(self):
        for name in ("UI_CONTROL_TRANSLATIONS", "UI_FIELD_TRANSLATIONS", "UI_TOOLTIP_TRANSLATIONS", "UI_SAFE_COMBO_TRANSLATIONS", "UI_SECTION_TRANSLATIONS"):
            values = table(name)
            self.assertEqual(set(values), LANGS - {"de"}, name)
            german = set(values["en"])
            for lang in LANGS - {"de"}:
                self.assertEqual(set(values[lang]), german, (name, lang))
                for key, value in values[lang].items():
                    self.assertIsInstance(value, str, (name, lang, key))
                    self.assertEqual(fields(value), fields(values["en"][key]), (name, lang, key))

    def test_tab_refresh_uses_stable_original_keys(self):
        code = ast.get_source_segment(TEXT, method("refresh_language_controls"))
        self.assertIn("self.tab_key(index)", code)
        self.assertIn("self.tabs.setTabText(index, translations.get(original, original))", code)
        self.assertIn("self.UI_SECTION_TRANSLATIONS.get(language, {})", code)
        self.assertIn("self.UI_SAFE_COMBO_NAMES", code)
        self.assertIn("Qt.ItemDataRole.UserRole + 1", code)
        self.assertIn("finally:", code)

    def test_language_switch_does_not_write_database_or_settings(self):
        # Contract limited to the refresh method, not its called helpers.
        code = ast.get_source_segment(TEXT, method("refresh_language_controls"))
        for unsafe in ("self.con.commit(", "self.con.execute(", "save_settings(", "write_text(", "unlink("):
            self.assertNotIn(unsafe, code)

if __name__ == "__main__":
    unittest.main()
