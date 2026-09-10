"""Read-only WARP source-side dependency report. Does not start sessions or bind ports."""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

COMMANDS = ("python3", "bash", "jq", "hyprctl", "ssh", "ip", "systemctl", "wayvnc")
OPTIONAL_COMMANDS = ("ffmpeg", "pactl")


def report(path: Path | None = None) -> dict:
    root = Path(path) if path else Path.home()
    missing = [name for name in COMMANDS if shutil.which(name) is None]
    missing_optional = [name for name in OPTIONAL_COMMANDS if shutil.which(name) is None]
    layout = {
        "share": str(root / ".local/share/omarchy-warp"),
        "bin": str(root / ".local/bin"),
        "config": str(root / ".config/omarchy-warp"),
        "state": str(root / ".local/state/omarchy-warp"),
    }
    return {
        "role": "omarchy-source-preflight",
        "receiver": "browser-only; no native receiver required on macOS, Windows or Linux",
        "missing_commands": missing,
        "missing_optional_commands": missing_optional,
        "optional_note": "ffmpeg and pactl belong to the optional resource agent, not the browser receiver",
        "layout": layout,
        "ready_for_install_preview": not missing,
        "executed_source_binaries": False,
    }


def main():
    parser = argparse.ArgumentParser(description="Report WARP source dependencies without changing the desktop.")
    parser.add_argument("--root", default=str(Path.home()), help="Fake home for tests; default is the current home.")
    args = parser.parse_args()
    print(json.dumps(report(Path(args.root)), indent=2))


if __name__ == "__main__":
    main()
