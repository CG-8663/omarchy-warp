# Omarchy Warp desktop tool: beginning of install

**Public pre-release. Not recommended to use.**

This document records the first per-user desktop install that was exercised on one Omarchy laptop. It is published so the work is visible. It is not a supported product install, not a security review, and not permission to run a live extended display.

Do not treat a green unit test, a GTK window, or a bar icon as a working remote desktop.

## What is in this repository

| Path | What it is |
|---|---|
| `tools/preflight.py` | Read-only dependency report. Does not start Warp, bind ports, or run recovered binaries. |
| `tools/install.py` | Per-user preview/apply/rollback for native Omarchy *source* launchers. Preview is the default. |
| `omarchy-plugin/` | Optional ⚡ bar widget. Not installed by `install.py`. |
| `web/index.html` | Static browser-receiver shell. No VNC, no live session. |
| Recovered `warp-dashboard` / `warp-control` / `omarchy-warp` binaries | **Not in this tree.** |

`install.py` still needs a private source packet that contains those binaries and `provenance.json`. That packet is review input, not a public download.

## What this first install does

On an Omarchy Linux laptop, as the desktop user, with no `sudo` and no package-manager changes:

1. Report missing commands (`python3 tools/preflight.py`).
2. Preview the file plan against a disposable home.
3. Apply into `~/.local/share/omarchy-warp/<version>`, with launchers in `~/.local/bin` and a `.desktop` file.
4. Optionally enable the ⚡ bar widget through Omarchy plugin IPC (no shell-killing deploy script).

It does **not**:

- install the native macOS receiver, resource agent, or broker
- copy another account's `hosts.json` or SSH keys
- start wayvnc, websockify, or a display session
- run `scripts/deploy-dashboard-laptop.sh` (that helper restarts the Omarchy shell)

Starting a display still follows the recovered SSH-receiver path. That path is out of first-release scope. The required remote end is a browser on macOS, Windows or Linux, which is not implemented here yet.

## Checks

From the repository root:

```bash
python3 -m unittest tools.test_preflight tools.test_install web.test_index -v
python3 tools/preflight.py --root "$HOME"
python3 tools/install.py --source /path/to/private-source-packet --web web/index.html --icon assets/omarchy-warp-concept.png --root /tmp/warp-home
```

`ready_for_install_preview` means the listed commands exist. It is not permission to install.

Apply only after a disposable-home run has succeeded:

```bash
python3 tools/install.py --source /path/to/private-source-packet --web web/index.html --icon assets/omarchy-warp-concept.png --root "$HOME"
python3 tools/install.py --source /path/to/private-source-packet --web web/index.html --icon assets/omarchy-warp-concept.png --root "$HOME" --apply
```

Rollback the last snapshot with `python3 tools/install.py --root "$HOME" --rollback`.

## Optional ⚡ bar widget

The lightning bolt is an Omarchy bar widget, not a file on the wallpaper. Enable it only after the standalone dashboard binary is on `PATH` (`~/.local/bin/warp-dashboard`).

```bash
export OMARCHY_PATH=/usr/share/omarchy
install -d ~/.config/omarchy/plugins/io.chronara.omarchy-warp
install -m 644 omarchy-plugin/manifest.json omarchy-plugin/BarWidget.qml \
  ~/.config/omarchy/plugins/io.chronara.omarchy-warp/
omarchy-plugin-validate ~/.config/omarchy/plugins/io.chronara.omarchy-warp
omarchy-shell shell rescanPlugins
omarchy-plugin-enable io.chronara.omarchy-warp --section right
```

This uses the running shell's plugin IPC. Do not copy QML into the plugin directory by running the recovered `deploy-dashboard-laptop.sh`; that script kills Quickshell.

Clicking ⚡ toggles `warp-dashboard`. Pairing a computer or starting a display is still unfinished.

## Honest status of the Super Kevin trial

Observed on one Omarchy laptop:

- Preflight commands present (including `wayvnc`).
- Disposable-home install, conflict refusal, and rollback unit tests passed.
- Live apply wrote versioned launchers and `io.chronara.OmarchyWarp.desktop`.
- GTK dashboard opened. Hosts list was empty (placeholder example hosts were not kept as paired machines).
- ⚡ appeared on the top-right bar after `omarchy-plugin-enable`.
- Companion browser and Super Kevin avatar processes were not restarted for that plugin enable.

Not observed, and not claimed:

- a working browser-only receiver on macOS, Windows or Linux
- a reviewed websockify environment
- three distinct successful live display workflows
- security review of the recovered control path

If you are reading this on GitHub: look, comment, or wait. Do not run it on a machine you care about.
