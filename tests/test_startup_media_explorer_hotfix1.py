import ast
import pathlib
import unittest

SOURCE = pathlib.Path(__file__).resolve().parents[1] / "source" / "workstation.py"

class StartupMediaExplorerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
        cls.workstation = next(node for node in cls.tree.body if isinstance(node, ast.ClassDef) and node.name == "Workstation")
        cls.methods = {node.name: node for node in cls.workstation.body if isinstance(node, ast.FunctionDef)}

    def test_media_explorer_does_not_access_later_config_dictionary(self):
        method = self.methods["build_media_explorer"]
        refs = [node for node in ast.walk(method) if isinstance(node, ast.Attribute) and node.attr == "config_extra_p34"]
        self.assertEqual(refs, [], "Medien-Explorer darf config_extra_p34 nicht verwenden")

    def test_media_explorer_is_built_before_configuration(self):
        init = self.methods["__init__"]
        calls = [node.func.attr for node in ast.walk(init) if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name) and node.func.value.id == "self"]
        self.assertLess(calls.index("build_media_explorer"), calls.index("build_configuration"))

    def test_configuration_initializes_its_own_dictionary(self):
        method = self.methods["build_configuration"]
        assignments = [node for node in ast.walk(method) if isinstance(node, ast.Assign) for target in node.targets if isinstance(target, ast.Attribute) and target.attr == "config_extra_p34"]
        self.assertTrue(assignments)

if __name__ == "__main__":
    unittest.main()
