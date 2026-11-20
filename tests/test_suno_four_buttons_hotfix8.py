import unittest
from pathlib import Path

SOURCE = (Path(__file__).resolve().parents[1] / "source" / "workstation.py").read_text(encoding="utf-8")

class FourButtonLayoutTests(unittest.TestCase):
    def test_four_equal_width_actions(self):
        block = SOURCE[SOURCE.index("        actions = QHBoxLayout()", SOURCE.index("    def build_songs(")):SOURCE.index("        layout.addLayout(actions)", SOURCE.index("    def build_songs("))]
        self.assertEqual(block.count("actions.addWidget("), 4)
        for name in ("info", "save", "workflow", "dashboard"):
            self.assertIn(f"actions.addWidget({name}, 1)", block)
    def test_infos_action_is_connected(self):
        self.assertIn("info.clicked.connect(self.open_song_infos)", SOURCE)

if __name__ == '__main__':
    unittest.main()
