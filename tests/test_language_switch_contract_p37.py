"""Preview 37: isolated language-switch contract tests (no Qt installation required)."""
import ast
import unittest
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / "source" / "workstation.py"
TREE = ast.parse(SOURCE.read_text(encoding="utf-8"))
APP = next(n for n in TREE.body if isinstance(n, ast.ClassDef) and n.name == "Workstation")
LANGS = ("de", "en", "fr", "es", "it")

CORE_TREE = ast.parse((SOURCE.parent / "mpw_core.py").read_text(encoding="utf-8"))


def constant(name):
    """Translation table: a literal in the Workstation class or in the shared core (mpw_core.py)."""
    for body in (APP.body, CORE_TREE.body):
        for n in body:
            if (isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in n.targets)
                    and not isinstance(n.value, ast.Attribute)):
                return ast.literal_eval(n.value)
    raise AssertionError("missing class translation table: " + name)

def method(name):
    return next(n for n in APP.body if isinstance(n, ast.FunctionDef) and n.name == name)

class FakeCombo:
    def __init__(self, states):
        self.items = [[x, x] for x in states]
        self.index = 2
        self.blocked = False
        self.events = []
    def currentData(self): return self.items[self.index][1]
    def count(self): return len(self.items)
    def blockSignals(self, value):
        self.blocked = value
        self.events.append(value)
    def setItemData(self, index, data): self.items[index][1] = data
    def setItemText(self, index, text): self.items[index][0] = text
    def setCurrentIndex(self, index): self.index = index

class LanguageSwitchContracts(unittest.TestCase):
    def test_translation_table_completeness(self):
        tables = ("CONFIG_TEXT_P33", "CONFIG_TEXT_P34", "APPEARANCE_TEXT_P35", "BACKGROUND_MESSAGES_P36")
        for table in tables:
            values = constant(table)
            self.assertEqual(set(values), set(LANGS), table)
            sizes = {lang: len(values[lang]) for lang in LANGS}
            self.assertEqual(len(set(sizes.values())), 1, (table, sizes))
            self.assertGreater(next(iter(sizes.values())), 0)

    def test_platform_status_switch_preserves_canonical_values(self):
        states = next(ast.literal_eval(n.value) for n in ast.parse((SOURCE.parent / "mpw_core.py").read_text(encoding="utf-8")).body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "STATES" for t in n.targets))
        labels = constant("PLATFORM_STATUS_LABELS")
        self.assertEqual(set(labels), set(LANGS) - {"de"})
        self.assertTrue(all(len(labels[lang]) == len(states) for lang in labels))
        names = ("refresh_platform_status_choices", "localized_platform_status")
        namespace = {"STATES": states}
        module = ast.Module(body=[method(n) for n in names], type_ignores=[])
        exec(compile(ast.fix_missing_locations(module), str(SOURCE), "exec"), namespace)
        class Stub:
            refresh_platform_status_choices = namespace[names[0]]
            localized_platform_status = namespace[names[1]]
            PLATFORM_STATUS_LABELS = labels
            def effective_language(self): return self.lang
        obj = Stub()
        obj.platform_status = FakeCombo(states)
        for lang in ("en", "fr", "es", "it", "de", "fr", "de"):
            obj.lang = lang
            obj.refresh_platform_status_choices()
            combo = obj.platform_status
            self.assertEqual(combo.index, 2)
            self.assertEqual([v[1] for v in combo.items], states)
            self.assertEqual([v[0] for v in combo.items], list(labels.get(lang, states)))
            self.assertFalse(combo.blocked)
            self.assertEqual(combo.events[-2:], [True, False])

    def test_language_refresh_wires_relevant_controls(self):
        code = ast.get_source_segment(SOURCE.read_text(encoding="utf-8"), method("refresh_language_controls"))
        for call in ("refresh_platform_status_choices()", "refresh_configuration_text_p33()", "refresh_configuration_text_p34()", "refresh_appearance_text_p35()"):
            self.assertIn(call, code)
        # The current design refreshes background gallery through the appearance dialog.
        self.assertIn("refresh_platforms()", code)

if __name__ == "__main__": unittest.main()
