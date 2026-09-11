#!/usr/bin/env python3
"""Per-user Omarchy source install for WARP. Preview by default. No package manager."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import time
from pathlib import Path

VERSION = "0.1.0-source"
LAUNCHER_MARKER = "# omarchy-warp-launcher"
DESKTOP_ID = "io.chronara.OmarchyWarp.desktop"
APPLICATION_ID = "io.chronara.OmarchyWarp"

REQUIRED_BINS = {
    "bin/warp-dashboard": "warp-dashboard",
    "bin/warp-control": "warp-control",
    "bin/omarchy-warp": "omarchy-warp",
    "bin/omarchy-warp-workspace": "omarchy-warp-workspace",
}
FORBIDDEN_RELATIVE = (
    "bin/omarchy-warp-receiver",
    "bin/omarchy-warp-agent",
    "bin/warp-broker",
    "omarchy-plugin/BarWidget.qml",
    "omarchy-plugin/manifest.json",
    "scripts/deploy-dashboard-laptop.sh",
)
COMMANDS = ("python3", "bash", "jq", "hyprctl", "ssh", "ip", "systemctl", "wayvnc")


class InstallError(RuntimeError):
    pass


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def provenance_hashes(source: Path) -> dict[str, str]:
    manifest = source / "provenance.json"
    if not manifest.is_file():
        return {}
    data = json.loads(manifest.read_text())
    return {item["path"]: item["sha256"] for item in data.get("files", []) if "path" in item and "sha256" in item}


def layout(root: Path) -> dict[str, Path]:
    return {
        "root": root,
        "share": root / ".local/share/omarchy-warp",
        "version": root / ".local/share/omarchy-warp" / VERSION,
        "current": root / ".local/share/omarchy-warp/current",
        "bin": root / ".local/bin",
        "config": root / ".config/omarchy-warp",
        "state": root / ".local/state/omarchy-warp",
        "backups": root / ".local/state/omarchy-warp/backups",
        "applications": root / ".local/share/applications",
        "desktop": root / ".local/share/applications" / DESKTOP_ID,
        "hosts": root / ".config/omarchy-warp/hosts.json",
    }


def launcher_text(target: Path) -> str:
    return (
        "#!/usr/bin/env bash\n"
        f"{LAUNCHER_MARKER} version={VERSION}\n"
        "set -euo pipefail\n"
        f'exec "{target}" "$@"\n'
    )


def desktop_text(paths: dict[str, Path], icon: Path | None) -> str:
    exec_path = paths["bin"] / "warp-dashboard"
    icon_line = f"Icon={icon}\n" if icon else "Icon=video-display\n"
    return (
        "[Desktop Entry]\n"
        "Version=1.0\n"
        "Type=Application\n"
        "Name=Omarchy Warp\n"
        "Comment=Browser extended desktop for this Omarchy laptop\n"
        f"Exec={exec_path}\n"
        f"{icon_line}"
        "Terminal=false\n"
        "Categories=Utility;\n"
        "StartupNotify=true\n"
        f"StartupWMClass={APPLICATION_ID}\n"
    )


def is_our_launcher(path: Path) -> bool:
    if not path.is_file():
        return False
    try:
        first = path.read_text(errors="replace").splitlines()[:4]
    except OSError:
        return False
    return any(line.startswith(LAUNCHER_MARKER) for line in first)


def verify_source(source: Path) -> dict[str, Path]:
    if not source.is_dir():
        raise InstallError(f"Source tree is missing: {source}")
    hashes = provenance_hashes(source)
    files: dict[str, Path] = {}
    for relative, name in REQUIRED_BINS.items():
        path = source / relative
        if not path.is_file() or path.stat().st_size == 0:
            raise InstallError(f"Required file missing: {relative}")
        expected = hashes.get(relative)
        if expected and sha256(path) != expected:
            raise InstallError(f"Hash mismatch for {relative}")
        files[name] = path
    return files


def preflight_missing() -> list[str]:
    return [name for name in COMMANDS if shutil.which(name) is None]


def plan(root: Path, source: Path, web: Path | None, icon: Path | None) -> dict:
    paths = layout(root)
    bins = verify_source(source)
    missing = preflight_missing()
    actions: list[dict] = []
    conflicts: list[str] = []

    for name, src in bins.items():
        dest_bin = paths["version"] / "bin" / name
        launcher = paths["bin"] / name
        actions.append({"op": "install-file", "from": str(src), "to": str(dest_bin), "mode": 0o755})
        if launcher.exists() and not is_our_launcher(launcher) and sha256(launcher) != sha256(src):
            conflicts.append(str(launcher))
        actions.append({"op": "write-launcher", "to": str(launcher), "target": str(dest_bin)})

    if web:
        if not web.is_file():
            raise InstallError(f"Web shell missing: {web}")
        actions.append({"op": "install-file", "from": str(web), "to": str(paths["version"] / "web" / "index.html"), "mode": 0o644})

    if icon and icon.is_file():
        dest_icon = paths["version"] / "assets" / icon.name
        actions.append({"op": "install-file", "from": str(icon), "to": str(dest_icon), "mode": 0o644})
        icon = dest_icon
    else:
        icon = None

    actions.append({"op": "write-desktop", "to": str(paths["desktop"])})
    actions.append({"op": "symlink-current", "to": str(paths["current"]), "target": str(paths["version"])})
    example = source / "config/hosts.example.json"
    if example.is_file():
        actions.append({"op": "install-file", "from": str(example), "to": str(paths["version"] / "config/hosts.example.json"), "mode": 0o644})
    if not paths["hosts"].exists():
        actions.append({"op": "create-hosts-empty", "to": str(paths["hosts"])})

    return {
        "role": "omarchy-source-install",
        "version": VERSION,
        "root": str(root),
        "source": str(source),
        "receiver": "browser-only; native receiver, agent, broker and shell plugin are not installed",
        "missing_commands": missing,
        "ready_for_install_preview": not missing,
        "conflicts": conflicts,
        "forbidden_not_installed": list(FORBIDDEN_RELATIVE),
        "copies_jamest_hosts": False,
        "package_manager": False,
        "restarts_omarchy_shell": False,
        "actions": actions,
        "layout": {key: str(value) for key, value in paths.items()},
        "icon": str(icon) if icon else None,
    }


def snapshot(paths: dict[str, Path], actions: list[dict]) -> Path:
    stamp = time.strftime("%Y%m%d-%H%M%S")
    backup = paths["backups"] / f"install-{stamp}"
    backup.mkdir(parents=True, exist_ok=True, mode=0o700)
    saved: list[dict] = []
    seen: set[str] = set()
    for action in actions:
        dest = Path(action["to"])
        key = str(dest)
        if key in seen:
            continue
        seen.add(key)
        if dest.exists() or dest.is_symlink():
            store = backup / "files" / f"{len(saved):02d}-{dest.name}"
            store.parent.mkdir(parents=True, exist_ok=True)
            if dest.is_symlink() or dest.is_file():
                shutil.copy2(dest, store, follow_symlinks=False)
            saved.append({"path": key, "backup": str(store), "existed": True})
        else:
            saved.append({"path": key, "backup": None, "existed": False})
    (backup / "manifest.json").write_text(json.dumps({"version": VERSION, "files": saved}, indent=2) + "\n")
    os.chmod(backup / "manifest.json", 0o600)
    return backup


def write_private(path: Path, text: str, mode: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    os.chmod(path, mode)


def apply_plan(spec: dict) -> dict:
    if spec["missing_commands"]:
        raise InstallError("Missing commands: " + ", ".join(spec["missing_commands"]))
    if spec["conflicts"]:
        raise InstallError("Refusing unknown existing files:\n" + "\n".join(spec["conflicts"]))
    paths = {key: Path(value) for key, value in spec["layout"].items()}
    for directory in ("share", "bin", "config", "state", "backups", "applications"):
        paths[directory].mkdir(parents=True, exist_ok=True)
    os.chmod(paths["config"], 0o700)
    os.chmod(paths["state"], 0o700)
    os.chmod(paths["backups"], 0o700)
    backup = snapshot(paths, spec["actions"])
    installed: list[str] = []
    try:
        for action in spec["actions"]:
            op = action["op"]
            dest = Path(action["to"])
            if op == "install-file":
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(action["from"], dest)
                os.chmod(dest, action["mode"])
            elif op == "write-launcher":
                write_private(dest, launcher_text(Path(action["target"])), 0o755)
            elif op == "write-desktop":
                icon = Path(spec["icon"]) if spec.get("icon") else None
                write_private(dest, desktop_text(paths, icon), 0o644)
            elif op == "symlink-current":
                target = Path(action["target"])
                if dest.is_symlink() or dest.exists():
                    dest.unlink()
                dest.symlink_to(target)
            elif op == "create-hosts-empty":
                write_private(dest, json.dumps({"version": 1, "hosts": []}, indent=2) + "\n", 0o600)
            else:
                raise InstallError(f"Unknown action {op}")
            installed.append(str(dest))
        (paths["version"] / "MANIFEST.json").write_text(
            json.dumps({"version": VERSION, "backup": str(backup), "installed": installed}, indent=2) + "\n"
        )
    except Exception:
        rollback(backup)
        raise
    return {"applied": True, "version": VERSION, "backup": str(backup), "installed": installed}


def rollback(backup: Path) -> None:
    manifest = json.loads((backup / "manifest.json").read_text())
    for item in reversed(manifest["files"]):
        dest = Path(item["path"])
        if item["existed"]:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item["backup"], dest, follow_symlinks=False)
        elif dest.exists() or dest.is_symlink():
            dest.unlink()


def latest_backup(root: Path) -> Path:
    backups = layout(root)["backups"]
    candidates = sorted(backups.glob("install-*"), key=lambda p: p.name)
    if not candidates:
        raise InstallError("No install backup to roll back")
    return candidates[-1]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=str(Path.home()), help="Install home. Use a temp dir for tests.")
    parser.add_argument("--source", help="Recovered source packet (bin/ + provenance.json).")
    parser.add_argument("--web", help="Browser-receiver shell HTML from the public tree.")
    parser.add_argument("--icon", help="Optional PNG/SVG icon.")
    parser.add_argument("--apply", action="store_true", help="Write files. Default is preview only.")
    parser.add_argument("--rollback", action="store_true", help="Restore the latest install snapshot.")
    args = parser.parse_args()
    root = Path(args.root).expanduser().resolve()
    if args.rollback:
        backup = latest_backup(root)
        rollback(backup)
        print(json.dumps({"rolled_back": str(backup)}, indent=2))
        return
    if not args.source:
        raise SystemExit("--source is required unless --rollback")
    source = Path(args.source).expanduser().resolve()
    web = Path(args.web).expanduser().resolve() if args.web else None
    icon = Path(args.icon).expanduser().resolve() if args.icon else None
    spec = plan(root, source, web, icon)
    if not args.apply:
        print(json.dumps(spec, indent=2))
        return
    result = apply_plan(spec)
    spec.update(result)
    print(json.dumps(spec, indent=2))


if __name__ == "__main__":
    try:
        main()
    except InstallError as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(2)
