import ast
import pathlib
import unittest

SOURCE = pathlib.Path(__file__).resolve().parents[1] / "source" / "workstation.py"

class ReleaseLanguageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SOURCE.read_text(encoding="utf-8")
        cls.tree = ast.parse(cls.source)

    def test_all_five_languages(self):
        cls = next(x for x in self.tree.body if isinstance(x, ast.ClassDef) and x.name == "Workstation")
        assignment = next(x for x in cls.body if isinstance(x, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "RELEASE_FORM_I18N_HF10" for t in x.targets))
        values = ast.literal_eval(assignment.value)
        self.assertEqual(set(values), {"de", "en", "fr", "es", "it"})
        self.assertTrue(all(len(v) == 4 for v in values.values()))

    def test_form_label_references(self):
        for key in ("release_date_form_label", "release_check_form_label", "release_platform_url_label"):
            self.assertIn("self." + key + " =", self.source)

    def test_language_switch_refreshes_release(self):
        fn = self.source.split("    def refresh_language_controls(self):",1)[1].split("    # Preview 33:",1)[0]
        self.assertIn("self.refresh_releases_language_hf10()", fn)

    def test_no_database_mutation(self):
        fn = self.source.split("    def refresh_releases_language_hf10(self):",1)[1].split("    def refresh_configuration_text_p33",1)[0]
        self.assertNotIn("self.con.execute", fn)
        self.assertNotIn("commit(", fn)

if __name__ == "__main__": unittest.main()
