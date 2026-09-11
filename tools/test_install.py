import json
import os
import hashlib
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import install


def _write(path: Path, text: str, mode=0o644) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    os.chmod(path, mode)


def fake_source(root: Path) -> Path:
    source = root / "source"
    files = {}
    bodies = {
        "bin/warp-dashboard": "#!/usr/bin/env python3\nprint('dashboard')\n",
        "bin/warp-control": "#!/usr/bin/env python3\nprint('control')\n",
        "bin/omarchy-warp": "#!/usr/bin/env bash\necho warp\n",
        "bin/omarchy-warp-workspace": "#!/usr/bin/env bash\necho workspace\n",
        "bin/omarchy-warp-receiver": "#!/usr/bin/env bash\necho receiver\n",
        "bin/omarchy-warp-agent": "#!/usr/bin/env bash\necho agent\n",
        "config/hosts.example.json": '{"version":1,"hosts":[]}\n',
        "config/hosts.json": '{"version":1,"hosts":[{"id":"jamest-secret"}]}\n',
        "omarchy-plugin/BarWidget.qml": "text: \"bolt\"\n",
        "omarchy-plugin/manifest.json": '{"id":"io.chronara.omarchy-warp"}\n',
    }
    for relative, body in bodies.items():
        path = source / relative
        _write(path, body, 0o755 if relative.startswith("bin/") else 0o600)
        files[relative] = hashlib.sha256(body.encode()).hexdigest()
    _write(
        source / "provenance.json",
        json.dumps({"files": [{"path": path, "sha256": digest, "bytes": 1} for path, digest in files.items()]}),
    )
    return source


def which_ok(name: str) -> str:
    return "/usr/bin/" + name


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "home"
        self.root.mkdir()
        self.source = fake_source(Path(self.temp.name))
        self.web = Path(self.temp.name) / "index.html"
        self.web.write_text("<!doctype html><title>viewer</title>\n")
        self.which = patch.object(install.shutil, "which", side_effect=which_ok)
        self.which.start()

    def tearDown(self):
        self.which.stop()
        self.temp.cleanup()

    def test_preview_does_not_write(self):
        spec = install.plan(self.root, self.source, self.web, None)
        self.assertTrue(spec["ready_for_install_preview"])
        self.assertFalse((self.root / ".local").exists())
        self.assertIn("bin/omarchy-warp-receiver", spec["forbidden_not_installed"])
        self.assertFalse(spec["copies_jamest_hosts"])
        self.assertFalse(spec["package_manager"])
        self.assertFalse(spec["restarts_omarchy_shell"])

    def test_apply_uses_versioned_layout_and_skips_secrets(self):
        spec = install.plan(self.root, self.source, self.web, None)
        result = install.apply_plan(spec)
        self.assertTrue(result["applied"])
        dashboard = self.root / ".local/share/omarchy-warp" / install.VERSION / "bin/warp-dashboard"
        launcher = self.root / ".local/bin/warp-dashboard"
        self.assertTrue(dashboard.is_file())
        self.assertTrue(install.is_our_launcher(launcher))
        self.assertIn("print('dashboard')", dashboard.read_text())
        self.assertFalse((self.root / ".local/bin/omarchy-warp-receiver").exists())
        self.assertFalse((self.root / ".local/bin/omarchy-warp-agent").exists())
        self.assertFalse((self.root / ".config/omarchy/plugins").exists())
        hosts = json.loads((self.root / ".config/omarchy-warp/hosts.json").read_text())
        self.assertEqual(hosts["hosts"], [])
        self.assertTrue((self.root / ".local/share/applications/io.chronara.OmarchyWarp.desktop").is_file())
        self.assertTrue((self.root / ".local/share/omarchy-warp/current").is_symlink())
        self.assertTrue((self.root / ".local/share/omarchy-warp" / install.VERSION / "web/index.html").is_file())

    def test_unknown_existing_file_is_refused(self):
        dest = self.root / ".local/bin/warp-dashboard"
        _write(dest, "#!/bin/sh\necho stranger\n", 0o755)
        spec = install.plan(self.root, self.source, self.web, None)
        self.assertTrue(spec["conflicts"])
        with self.assertRaises(install.InstallError):
            install.apply_plan(spec)

    def test_our_launcher_can_be_upgraded(self):
        spec = install.plan(self.root, self.source, self.web, None)
        install.apply_plan(spec)
        launcher = self.root / ".local/bin/warp-dashboard"
        first = launcher.read_text()
        spec2 = install.plan(self.root, self.source, self.web, None)
        self.assertEqual(spec2["conflicts"], [])
        install.apply_plan(spec2)
        self.assertTrue(install.is_our_launcher(launcher))
        self.assertIn("omarchy-warp-launcher", launcher.read_text())
        self.assertTrue(launcher.read_text())
        self.assertNotEqual(first, "")  # still a launcher

    def test_rollback_removes_first_install(self):
        spec = install.plan(self.root, self.source, self.web, None)
        result = install.apply_plan(spec)
        backup = Path(result["backup"])
        self.assertTrue((self.root / ".local/bin/warp-dashboard").exists())
        install.rollback(backup)
        self.assertFalse((self.root / ".local/bin/warp-dashboard").exists())
        self.assertFalse((self.root / ".local/share/applications/io.chronara.OmarchyWarp.desktop").exists())

    def test_plugin_is_opt_in(self):
        spec = install.plan(self.root, self.source, self.web, None, plugin=True)
        install.apply_plan(spec)
        self.assertTrue((self.root / ".config/omarchy/plugins/io.chronara.omarchy-warp/BarWidget.qml").is_file())
        self.assertFalse((self.root / ".local/bin/omarchy-warp-receiver").exists())

    def test_repo_tree_is_a_complete_source(self):
        self.assertTrue((install.REPO / "bin/warp-dashboard").is_file())
        self.assertTrue((install.REPO / "web/index.html").is_file())
        self.assertTrue((install.REPO / "omarchy-plugin/BarWidget.qml").is_file())

    def test_missing_commands_block_apply(self):
        with patch.object(install.shutil, "which", return_value=None):
            spec = install.plan(self.root, self.source, self.web, None)
        self.assertFalse(spec["ready_for_install_preview"])
        with self.assertRaises(install.InstallError):
            install.apply_plan(spec)


if __name__ == "__main__":
    unittest.main()
