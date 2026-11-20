"""Bands tab: 'Gruppe' and 'Instrumente / Hardware' are editable menus with saved values."""
import ast
from contextlib import closing
import json
import os
from pathlib import Path
import sqlite3
import unittest

SOURCE = Path(__file__).resolve().parents[1] / 'source' / 'workstation.py'
CORE = Path(__file__).resolve().parents[1] / 'source' / 'mpw_core.py'  # Qt-free core (module-level functions)
TEXT = CORE.read_text(encoding='utf-8') + '\n' + SOURCE.read_text(encoding='utf-8')
TREE = ast.parse(TEXT)


def load_function(name, cls=None):
    body = TREE.body
    if cls:
        body = next(n for n in TREE.body if isinstance(n, ast.ClassDef) and n.name == cls).body
    node = next(n for n in body if isinstance(n, ast.FunctionDef) and n.name == name)
    node.decorator_list = []
    ns = {'json': json}
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(SOURCE), 'exec'), ns)
    return ns[name]


choices = load_function('saved_hardware_choices')


class SavedHardwareChoices(unittest.TestCase):
    def setUp(self):
        self.con = sqlite3.connect(':memory:')
        self.addCleanup(self.con.close)
        self.con.execute('CREATE TABLE instruments(id INTEGER PRIMARY KEY, band_id INTEGER, category TEXT, details TEXT)')
        self.con.execute('CREATE TABLE hardware_presets(id INTEGER PRIMARY KEY, name TEXT, items_json TEXT)')
        self.con.executemany('INSERT INTO instruments(band_id,category,details) VALUES(?,?,?)', [
            (1, 'Gitarre', 'Gibson Les Paul'), (2, 'gitarre ', 'Fender Stratocaster'),
            (1, 'Mikrofon', 'Shure SM7B'), (2, 'Gitarre', 'Gibson Les Paul'), (3, '', ''), (3, None, None)])
        self.con.execute('INSERT INTO hardware_presets(name,items_json) VALUES(?,?)',
                         ('Studio', json.dumps([['Synth', 'Moog Minimoog'], ['Mikrofon', 'Neumann U87']])))
        self.con.execute('INSERT INTO hardware_presets(name,items_json) VALUES(?,?)', ('kaputt', '{not json'))

    def test_groups_from_all_bands_and_presets_without_duplicates(self):
        groups, details = choices(self.con)
        self.assertEqual(groups, ['Gitarre', 'Mikrofon', 'Synth'])
        self.assertEqual(details, ['Fender Stratocaster', 'Gibson Les Paul', 'Moog Minimoog', 'Neumann U87', 'Shure SM7B'])

    def test_details_follow_known_group_case_insensitive(self):
        self.assertEqual(choices(self.con, ' GITARRE')[1], ['Fender Stratocaster', 'Gibson Les Paul'])
        self.assertEqual(choices(self.con, 'Mikrofon')[1], ['Neumann U87', 'Shure SM7B'])

    def test_unknown_or_empty_group_shows_all_details(self):
        self.assertEqual(len(choices(self.con, 'Neue Gruppe')[1]), 5)
        self.assertEqual(len(choices(self.con, '')[1]), 5)

    def test_read_only(self):
        before = list(self.con.iterdump())
        choices(self.con, 'Gitarre')
        self.assertEqual(before, list(self.con.iterdump()))


missing = load_function('preset_items_missing')


class PresetToOtherBand(unittest.TestCase):
    def test_only_missing_entries_without_duplicates(self):
        existing = [('Gitarre', 'Gibson Les Paul'), ('Mikrofon', 'Shure SM7B')]
        preset = [['gitarre ', 'gibson les paul'], ['Synth', 'Moog'], ['Synth', 'moog '], ['', 'leer'], ['Bass', 'Fender P']]
        self.assertEqual(missing(existing, preset), [('Synth', 'Moog'), ('Bass', 'Fender P')])

    def test_empty_band_gets_whole_preset_and_full_band_gets_nothing(self):
        preset = [['Synth', 'Moog'], ['Bass', 'Fender P']]
        self.assertEqual(missing([], preset), [('Synth', 'Moog'), ('Bass', 'Fender P')])
        self.assertEqual(missing([('Synth', 'Moog'), ('Bass', 'Fender P')], preset), [])

    def test_wiring_target_band_and_translations(self):
        self.assertIn("('Preset zur Band hinzufügen', self.add_hardware_preset_to_band)", TEXT)
        self.assertIn("QLabel('Zielband')", TEXT)
        for fn in ('add_hardware_preset_to_band', 'apply_hardware_preset'):
            body = TEXT[TEXT.index(f'    def {fn}(self):'):]
            body = body[:body.index('\n    def ', 10)]
            self.assertIn('_selected_preset_and_target()', body, fn)
            self.assertIn('show_band_hardware(bid)', body, fn)
        cls = next(n for n in TREE.body if isinstance(n, ast.ClassDef) and n.name == 'Workstation')
        node = next(n for n in cls.body if isinstance(n, ast.Assign) and getattr(n.targets[0], 'id', '') == 'PRESET_TRANSFER_TEXTS')
        texts = ast.literal_eval(node.value)
        self.assertEqual(set(texts), {'de', 'en', 'fr', 'es', 'it'})
        for lang, items in texts.items():
            self.assertEqual(set(items), set(texts['de']), lang)
            for value in items.values():
                value.format(name='N', band='B', new=1, skipped=2)
        for key in ("'Zielband': 'Target band'", "'Preset zur Band hinzufügen': 'Add preset to band'"):
            self.assertIn(key, TEXT)


class HardwareMenuWiring(unittest.TestCase):
    def test_fields_are_editable_menus_and_accessors_fit(self):
        self.assertIn("self.inst_cat = self.combo(inf,'Gruppe')", TEXT)
        self.assertIn("self.inst_detail = self.combo(inf,'Instrumente / Hardware')", TEXT)
        for bad in ('inst_cat.text()', 'inst_detail.text()', 'inst_cat.setText(', 'inst_detail.setText(',
                    'inst_cat.clear()', 'inst_detail.clear()'):
            self.assertNotIn(bad, TEXT, bad)
        self.assertIn('self.refresh_instrument_choices()', TEXT)

    def test_fill_keeps_typed_text_with_real_qt_widget(self):
        os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
        try:
            from PySide6.QtWidgets import QApplication, QComboBox
        except ImportError:
            self.skipTest('PySide6 nicht installiert')
        app = QApplication.instance() or QApplication([])
        fill = load_function('_fill_editable_combo', 'Workstation')
        combo = QComboBox(); combo.setEditable(True)
        combo.setEditText('Neu getippt')
        fill(combo, ['Gitarre', 'Mikrofon'])
        self.assertEqual([combo.itemText(i) for i in range(combo.count())], ['Gitarre', 'Mikrofon'])
        self.assertEqual(combo.currentText(), 'Neu getippt')
        # load_instrument uses setCurrentText; on editable menus it sets the shown text.
        combo.setCurrentText('Mikrofon')
        self.assertEqual(combo.currentText(), 'Mikrofon')
        combo.clearEditText()
        self.assertEqual((combo.currentText(), combo.count()), ('', 2))
        self.assertIsNotNone(app)


if __name__ == '__main__':
    unittest.main()
