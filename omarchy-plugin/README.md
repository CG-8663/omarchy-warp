# Omarchy Warp plugin

Bar widget for [Omarchy](https://omarchy.org): pair a trusted LAN or Tailscale computer from the ⚡ slot.

- Local LAN is trusted (no fingerprint ceremony).
- Tailscale destinations use Tailscale SSH.
- If key login is missing, the panel asks once for that computer’s account password and installs this laptop’s public key. SSH tunnels stay in use after that.

## Install

From this repository on an Omarchy laptop:

```bash
./install.sh --plugin
```

Or copy this folder:

```bash
cp -a omarchy-plugin ~/.config/omarchy/plugins/io.chronara.omarchy-warp
omarchy plugin validate ~/.config/omarchy/plugins/io.chronara.omarchy-warp
omarchy plugin enable io.chronara.omarchy-warp --section right
omarchy-shell shell rescanPlugins
```

`omarchy plugin add <git-url>` expects `manifest.json` at the clone root. This plugin lives in `omarchy-plugin/` inside the Omarchy Warp repo, so use `install.sh --plugin` or the copy steps above.

## Test

1. The ⚡ appears on the laptop panel (`eDP-1` only).
2. Click it. The panel lists paired computers.
3. Pair with a LAN or Tailscale address. If SSH keys are not yet authorized, enter the destination password once.
4. Do not start a live extended display from this panel; use **Open dashboard** for the full GTK app.
