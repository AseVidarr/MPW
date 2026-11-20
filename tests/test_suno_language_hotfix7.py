import unittest
from pathlib import Path

SRC = (Path(__file__).resolve().parents[1] / "source" / "workstation.py").read_text(encoding="utf-8")

class SunoHotfix7Tests(unittest.TestCase):
    def test_status_persistence_uses_data(self):
        self.assertIn("self.status.currentData()", SRC)
        self.assertIn("self.status.findData(row[0] or 'In Bearbeitung')", SRC)
    def test_actions_share_one_row(self):
        section = SRC.split('    def build_songs(self):', 1)[1].split('    def build_ai(self):', 1)[0]
        self.assertIn('layout.addLayout(actions)', section)
        self.assertIn("QPushButton('INFOS')", section)
    def test_languages_have_suno_text(self):
        for lang in ('de','en','fr','es','it'):
            self.assertIn("'"+lang+"': dict(title=", SRC)
        self.assertIn('self.refresh_suno_language_hf7()', SRC)

if __name__ == '__main__': unittest.main()
