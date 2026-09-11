# Omarchy Warp desktop tool: beginning of install

**Early beta. Public, but not recommended to use.**

This document records the first per-user desktop install. It is not a supported product install, not a security review, and not permission to run a live extended display.

Do not treat a green unit test, a GTK window, or a bar icon as a working remote desktop.

## Easy install

On an Omarchy Linux laptop, as the desktop user:

```bash
git clone git@github.com:CG-8663/omarchy-warp.git
cd omarchy-warp
./install.sh
```

Optional ⚡ bar widget:

```bash
./install.sh --plugin
```

Print the plan without writing files:

```bash
./install.sh --preview
```

No `sudo`. No package manager. Rollback with `python3 tools/install.py --rollback`.

## What the installer writes

| Path | What it is |
|---|---|
| `~/.local/share/omarchy-warp/0.1.0-beta/` | Versioned dashboard, control, and workspace helpers |
| `~/.local/bin/warp-dashboard` | Launcher (and `warp-control`, `omarchy-warp`, `omarchy-warp-workspace`) |
| `~/.local/share/applications/io.chronara.OmarchyWarp.desktop` | Desktop entry |
| `~/.config/omarchy-warp/hosts.json` | Empty pairing file if none exists |
| `~/.config/omarchy/plugins/io.chronara.omarchy-warp/` | Only with `--plugin` |

## What it does not do

- install the native macOS receiver, resource agent, or broker
- copy another account's `hosts.json` or SSH keys
- start wayvnc, websockify, or a display session
- run `pacman` or restart the Omarchy shell
- use the recovered `deploy-dashboard-laptop.sh` helper (that script kills Quickshell)

Starting a display still follows the old SSH-receiver path. That path is out of first-release scope. The required remote end is a browser on macOS, Windows or Linux, which is not implemented here yet.

## Checks

```bash
python3 -m unittest tools.test_preflight tools.test_install web.test_index -v
python3 tools/preflight.py --root "$HOME"
./install.sh --preview --root /tmp/warp-home
```

`ready_for_install_preview` means the listed commands exist. It is not a working remote-desktop session.

## Honest status of the Super Kevin trial

Observed on one Omarchy laptop:

- `./install.sh` path: versioned launchers, desktop entry, empty hosts file.
- GTK dashboard opened.
- ⚡ appeared on the top-right bar after `--plugin` / `omarchy-plugin-enable`.
- Companion browser and Super Kevin avatar processes were not restarted for that plugin enable.

Not observed, and not claimed:

- a working browser-only receiver on macOS, Windows or Linux
- a reviewed websockify environment
- three distinct successful live display workflows
- security review of the control path

If you are reading this on GitHub: look, comment, or wait. Do not run it on a machine you care about.
