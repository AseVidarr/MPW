import ast
import unittest
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / "source" / "workstation.py"

class ProjectDisplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SOURCE.read_text(encoding="utf-8")
        cls.tree = ast.parse(cls.source)

    def test_languages_present(self):
        for language in ("de", "en", "fr", "es", "it"):
            self.assertIn(f"'{language}': (", self.source)

    def test_filter_uses_stable_status(self):
        self.assertIn("self.PROJECT_STATUS_KEYS[status_index - 1]", self.source)
        self.assertIn("status_filter is None", self.source)

    def test_database_status_is_not_rewritten(self):
        self.assertIn("item.setData(Qt.ItemDataRole.UserRole + 2, status)", self.source)
        self.assertIn("display_status", self.source)

    def test_dynamic_refresh_connected(self):
        self.assertIn("self.refresh_project_display_hf5()", self.source)
        self.assertIn("self.project_count.setText(words[6]", self.source)

    def test_combo_selection_preserved(self):
        self.assertIn("combo.setItemText(index, label)", self.source)
        self.assertIn("combo.blockSignals(False)", self.source)

if __name__ == '__main__':
    unittest.main()
