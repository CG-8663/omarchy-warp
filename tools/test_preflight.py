import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import preflight


class PreflightTests(unittest.TestCase):
    def test_reports_missing_commands_without_claiming_install(self):
        with patch.object(preflight.shutil, "which", return_value=None):
            data = preflight.report(Path("/tmp/warp-home"))
        self.assertEqual(data["missing_commands"], list(preflight.COMMANDS))
        self.assertEqual(data["missing_optional_commands"], list(preflight.OPTIONAL_COMMANDS))
        self.assertFalse(data["ready_for_install_preview"])
        self.assertFalse(data["executed_source_binaries"])
        self.assertIn("browser-only", data["receiver"])
        self.assertIn("optional resource agent", data["optional_note"])

    def test_optional_absence_does_not_block_preview(self):
        def which(name):
            return None if name in preflight.OPTIONAL_COMMANDS else "/usr/bin/" + name
        with patch.object(preflight.shutil, "which", side_effect=which):
            data = preflight.report(Path("/tmp/warp-home"))
        self.assertEqual(data["missing_commands"], [])
        self.assertEqual(data["missing_optional_commands"], list(preflight.OPTIONAL_COMMANDS))
        self.assertTrue(data["ready_for_install_preview"])

    def test_layout_stays_under_supplied_home(self):
        with tempfile.TemporaryDirectory() as temp:
            data = preflight.report(Path(temp))
        for value in data["layout"].values():
            self.assertTrue(value.startswith(temp))


if __name__ == "__main__":
    unittest.main()
