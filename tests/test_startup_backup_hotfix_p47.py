import ast
from pathlib import Path
import unittest

SOURCE = Path(__file__).resolve().parents[1] / "source" / "workstation.py"

class BackupStartupRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
        cls.methods = {node.name: node for clsnode in tree.body if isinstance(clsnode, ast.ClassDef) and clsnode.name == "Workstation" for node in clsnode.body if isinstance(node, ast.FunctionDef)}

    def test_backup_does_not_access_later_appearance_dictionary(self):
        refs = [n for n in ast.walk(self.methods["build_backup"]) if isinstance(n, ast.Attribute) and n.attr == "appearance_text_p35"]
        self.assertEqual(refs, [])

    def test_backup_precedes_configuration(self):
        calls = [n.func.attr for n in ast.walk(self.methods["__init__"]) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and isinstance(n.func.value, ast.Name) and n.func.value.id == "self"]
        self.assertLess(calls.index("build_backup"), calls.index("build_configuration"))

    def test_appearance_dictionary_initialized_in_configuration(self):
        assigns = [n for n in ast.walk(self.methods["build_configuration"]) if isinstance(n, ast.Assign) for target in n.targets if isinstance(target, ast.Attribute) and target.attr == "appearance_text_p35"]
        self.assertTrue(assigns)

if __name__ == "__main__": unittest.main()
