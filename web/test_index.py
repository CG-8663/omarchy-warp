import unittest
from pathlib import Path

HTML = (Path(__file__).resolve().parent / "index.html").read_text()


class ViewerShellTests(unittest.TestCase):
    def test_no_remote_assets_scripts_or_forms(self):
        lowered = HTML.lower()
        self.assertNotIn("http://", lowered)
        self.assertNotIn("https://", lowered)
        self.assertNotIn("<script", lowered)
        self.assertNotIn("<form", lowered)
        self.assertNotIn("../viewer.js", HTML)

    def test_states_the_browser_receiver_rule(self):
        lowered = HTML.lower()
        self.assertIn("browser", lowered)
        self.assertIn("no native install", lowered)
        self.assertIn("macos", lowered)
        self.assertIn("windows", lowered)
        self.assertIn("linux", lowered)
        self.assertIn("name=\"viewport\"", HTML)

    def test_does_not_claim_a_live_session(self):
        lowered = HTML.lower()
        self.assertIn("no source gateway is served", lowered)
        self.assertNotIn("connected · omarchy laptop", lowered)


if __name__ == "__main__":
    unittest.main()
