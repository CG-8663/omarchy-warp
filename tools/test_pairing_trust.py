import os
import socket
import tempfile
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent
BIN = ROOT.parent / "bin" / "warp-control"
if not BIN.is_file():
    BIN = ROOT / "warp-control"

warp = SourceFileLoader("warp_control", str(BIN)).load_module()


class FakeResult:
    def __init__(self, stdout="", returncode=0):
        self.stdout = stdout
        self.returncode = returncode


class PairingTrustTests(unittest.TestCase):
    def test_cgnat_is_tailscale_ssh(self):
        self.assertTrue(warp.uses_tailscale_ssh("100.107.141.118", "tailscale"))
        self.assertTrue(warp.uses_tailscale_ssh("100.64.0.1"))
        self.assertFalse(warp.uses_tailscale_ssh("192.168.68.55", "ethernet-lan"))

    def test_default_user_comes_from_the_environment(self):
        with patch.dict(os.environ, {"USER": "superkevin"}, clear=False):
            self.assertEqual(warp.default_ssh_user(""), "superkevin")
            self.assertEqual(warp.default_ssh_user("jamest"), "jamest")

    def test_preview_fills_user_and_skips_fingerprint_on_trusted_lan(self):
        def fake_run(args, timeout=20, check=True, env=None):
            return FakeResult("")

        info = [(socket.AF_INET, socket.SOCK_STREAM, 0, "", ("192.168.68.55", 22))]
        with tempfile.TemporaryDirectory() as temp:
            warp.CONFIG = Path(temp)
            warp.SETTINGS = Path(temp) / "settings.json"
            warp.HOSTS = Path(temp) / "hosts.json"
            warp.KEYS = Path(temp) / "known_hosts"
            with patch.dict(os.environ, {"USER": "superkevin"}, clear=False), \
                 patch.object(warp, "run", side_effect=fake_run), \
                 patch.object(socket, "getaddrinfo", return_value=info):
                preview = warp.pairing_preview({"name": "Studio Mac", "ethernet-lan": "192.168.68.55"})
        self.assertEqual(preview["sshUser"], "superkevin")
        self.assertFalse(preview["needsFingerprint"])
        self.assertTrue(preview["lanTrusted"])
        self.assertEqual(preview["fingerprint"], "trusted-lan")

    def test_tailscale_preview_does_not_require_openssh_keyscan(self):
        info = [(socket.AF_INET, socket.SOCK_STREAM, 0, "", ("100.107.141.118", 22))]
        with tempfile.TemporaryDirectory() as temp:
            warp.CONFIG = Path(temp)
            warp.SETTINGS = Path(temp) / "settings.json"
            with patch.dict(os.environ, {"USER": "superkevin"}, clear=False), \
                 patch.object(socket, "getaddrinfo", return_value=info), \
                 patch.object(warp, "run") as mocked:
                preview = warp.pairing_preview({"name": "Studio Mac", "tailscale": "100.107.141.118"})
        mocked.assert_not_called()
        self.assertEqual(preview["fingerprint"], "tailscale-ssh")
        self.assertFalse(preview["needsFingerprint"])

    def test_local_public_key_reads_ed25519(self):
        with tempfile.TemporaryDirectory() as temp:
            ssh_dir = Path(temp) / ".ssh"
            ssh_dir.mkdir()
            (ssh_dir / "id_ed25519.pub").write_text("ssh-ed25519 AAAA test@host\n")
            with patch.object(Path, "home", return_value=Path(temp)):
                self.assertEqual(warp.local_public_key(), "ssh-ed25519 AAAA test@host")

    def test_pair_confirm_asks_for_password_when_key_auth_fails(self):
        info = [(socket.AF_INET, socket.SOCK_STREAM, 0, "", ("192.168.68.55", 22))]
        with tempfile.TemporaryDirectory() as temp:
            warp.CONFIG = Path(temp)
            warp.SETTINGS = Path(temp) / "settings.json"
            warp.HOSTS = Path(temp) / "hosts.json"
            warp.KEYS = Path(temp) / "known_hosts"
            preview = {
                "name": "Studio Mac",
                "sshUser": "jamest",
                "transports": [{"kind": "ethernet-lan", "address": "192.168.68.55", "priority": 1}],
                "keyLines": [],
                "fingerprint": "trusted-lan",
                "unreachable": [],
                "needsFingerprint": False,
                "lanTrusted": True,
            }
            with patch.dict(os.environ, {"USER": "superkevin", "WARP_PAIR_PASSWORD_FILE": ""}, clear=False), \
                 patch.object(socket, "getaddrinfo", return_value=info), \
                 patch.object(warp, "pairing_preview", return_value=preview), \
                 patch.object(warp, "pair_password", return_value=None), \
                 patch.object(warp, "ssh", side_effect=warp.WarpError("Permission denied")):
                with self.assertRaises(warp.WarpNeedsPassword) as caught:
                    warp.pair_confirm(preview)
        self.assertEqual(caught.exception.preview["fingerprint"], "trusted-lan")


if __name__ == "__main__":
    unittest.main()
