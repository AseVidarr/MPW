import ast
import pathlib
import unittest

SOURCE = pathlib.Path(__file__).resolve().parents[1] / "source" / "workstation.py"

class ConfigurationStartupTests(unittest.TestCase):
    def test_configuration_info_registered_before_refresh(self):
        text = SOURCE.read_text(encoding="utf-8")
        method = text[text.index("    def build_configuration("):text.index("    APPEARANCE_KEYS_P35 =", text.index("    def build_configuration("))]
        self.assertIn("self.config_extra_p34['info'] = info", method)
        self.assertLess(method.index("self.config_extra_p34['info'] = info"), method.index("self.refresh_configuration_text_p34()"))

    def test_all_configuration_keys_are_registered(self):
        text = SOURCE.read_text(encoding="utf-8")
        tree = ast.parse(text)
        cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "Workstation")
        keys = next(n.value for n in cls.body if isinstance(n, ast.Assign) and any(isinstance(x, ast.Name) and x.id == "CONFIG_KEYS_P34" for x in n.targets))
        names = [x.value for x in keys.elts]
        method = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == "build_configuration")
        assigned = set()
        for n in ast.walk(method):
            if isinstance(n, ast.Subscript) and isinstance(n.value, ast.Attribute) and n.value.attr == "config_extra_p34" and isinstance(n.slice, ast.Constant):
                assigned.add(n.slice.value)
        self.assertEqual(set(names), assigned | {"open_folder"})

    def test_python_source_compiles(self):
        compile(SOURCE.read_text(encoding="utf-8"), str(SOURCE), "exec")

if __name__ == '__main__':
    unittest.main()
