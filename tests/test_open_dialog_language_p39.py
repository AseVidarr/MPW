"""Preview 39: isolated live-dialog and selection-preservation tests."""
import ast
import string
import unittest
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / 'source' / 'workstation.py'
TREE = ast.parse(SOURCE.read_text(encoding='utf-8'))
APP = next(node for node in TREE.body if isinstance(node, ast.ClassDef) and node.name == 'Workstation')
LANGS = ('de', 'en', 'fr', 'es', 'it')

def constant(name):
    for node in APP.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
            return ast.literal_eval(node.value)
    raise AssertionError('Missing translation table ' + name)

def method(name):
    return next(node for node in APP.body if isinstance(node, ast.FunctionDef) and node.name == name)

class Label:
    def __init__(self): self.text = None
    def setText(self, text): self.text = text
class Group(Label):
    def setTitle(self, text): self.text = text
class Dialog(Label):
    def setWindowTitle(self, text): self.text = text
class Combo:
    def __init__(self, pairs, selected):
        self.items = [list(pair) for pair in pairs]
        self.selected = selected
        self.blocked = False
        self.events = []
    def findData(self, data):
        return next((i for i, item in enumerate(self.items) if item[1] == data), -1)
    def setItemText(self, index, value): self.items[index][0] = value
    def blockSignals(self, blocked):
        self.blocked = blocked
        self.events.append(blocked)
    def currentData(self): return self.items[self.selected][1]

class OpenDialogLanguageTests(unittest.TestCase):
    def test_appearance_open_dialog_keeps_scaling_selection(self):
        names = ('refresh_appearance_text_p35',)
        ns = {'QGroupBox': Group, 'QDialog': Dialog}
        exec(compile(ast.fix_missing_locations(ast.Module(body=[method(x) for x in names], type_ignores=[])), str(SOURCE), 'exec'), ns)
        words = constant('APPEARANCE_TEXT_P35')
        class Stub:
            APPEARANCE_TEXT_P35 = words
            refresh_appearance_text_p35 = ns['refresh_appearance_text_p35']
            def effective_language(self): return self.lang
            def refresh_background_gallery(self): self.gallery_updates += 1
            def update_background_preview(self): self.preview_updates += 1
        obj = Stub()
        obj.appearance_text_p35 = {'dialog_title': Dialog()} if 'dialog_title' in words['de'] else {}
        # Include real available keys and all three widget categories.
        keys = list(words['de'])
        obj.appearance_text_p35 = {keys[0]: Dialog(), keys[1]: Group(), keys[2]: Label()}
        obj.background_gallery = object()
        obj.gallery_updates = obj.preview_updates = 0
        obj.background_scaling_choice = Combo([('x','cover'),('y','contain'),('z','stretch')], 1)
        for lang in ('en','fr','es','it','de','en','de'):
            obj.lang = lang
            obj.refresh_appearance_text_p35()
            self.assertEqual(obj.background_scaling_choice.currentData(), 'contain')
            self.assertEqual([v[1] for v in obj.background_scaling_choice.items], ['cover','contain','stretch'])
            self.assertEqual([v[0] for v in obj.background_scaling_choice.items], [words[lang][k] for k in ('scale_cover','scale_contain','scale_stretch')])
            self.assertFalse(obj.background_scaling_choice.blocked)
            self.assertEqual(obj.background_scaling_choice.events[-2:], [True,False])
            for key, widget in obj.appearance_text_p35.items(): self.assertEqual(widget.text, words[lang][key])
        self.assertEqual(obj.gallery_updates, 7)
        self.assertEqual(obj.preview_updates, 7)

    def test_configuration_open_dialog_keeps_startup_choice(self):
        ns = {'QGroupBox': Group}
        exec(compile(ast.fix_missing_locations(ast.Module(body=[method('refresh_configuration_text_p33')], type_ignores=[])), str(SOURCE), 'exec'), ns)
        words = constant('CONFIG_TEXT_P33')
        class Stub:
            CONFIG_TEXT_P33 = words
            refresh_configuration_text_p33 = ns['refresh_configuration_text_p33']
            def effective_language(self): return self.lang
        obj = Stub()
        obj.config_static_p33 = {0: Group(), 1: Label(), 2: Label()}
        obj.startup_tab_choice = Combo([('last','__last__'),('songs','songs'),('settings','settings')], 2)
        for lang in LANGS + ('de',):
            obj.lang = lang
            obj.refresh_configuration_text_p33()
            self.assertEqual(obj.startup_tab_choice.currentData(), 'settings')
            self.assertEqual(obj.startup_tab_choice.items[0], [words[lang][3], '__last__'])
            self.assertEqual(obj.startup_tab_choice.items[1][1], 'songs')
            self.assertFalse(obj.startup_tab_choice.blocked)
            for key, widget in obj.config_static_p33.items(): self.assertEqual(widget.text, words[lang][key])

    def test_background_messages_have_matching_placeholders(self):
        words = constant('BACKGROUND_MESSAGES_P36')
        self.assertEqual(set(words), set(LANGS))
        keys = set(words['de'])
        for lang in LANGS:
            self.assertEqual(set(words[lang]), keys)
            for key in keys:
                def fields(text): return {x for _, x, _, _ in string.Formatter().parse(text) if x is not None}
                self.assertEqual(fields(words[lang][key]), fields(words['de'][key]), (lang,key))

    def test_language_switch_does_not_replace_user_input(self):
        # AST contract: label-refresh functions may set presentation, not user inputs or persistent data.
        for name in ('refresh_appearance_text_p35','refresh_configuration_text_p33','refresh_configuration_text_p34'):
            node = method(name)
            calls = [n.func.attr for n in ast.walk(node) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute)]
            for unsafe in ('setCurrentText','setCurrentData','setCurrentIndex','setPlainText','setValue','commit','execute','save_app_configuration'):
                self.assertNotIn(unsafe, calls, (name,unsafe))

if __name__ == '__main__': unittest.main()
