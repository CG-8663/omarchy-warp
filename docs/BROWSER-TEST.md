# Browser test workflow (Windows first)

**Early beta.** This checks the public viewer shell, not a live Warp session.

The remote end must work in a normal browser on Windows, macOS and Linux with no native Warp install. Until a source gateway exists, testers only open the static page.

## What to copy

From this repository, take the whole `web/` folder:

- `web/index.html`
- `web/credits/chronara-ai.png`
- `web/credits/super-kevin-standing.png`

Do not send recovered receiver binaries, SSH keys, or `hosts.json`.

## Windows

1. Copy `web/` onto the Windows machine, or serve it from the Omarchy laptop on the LAN: `python3 -m http.server 8769 --directory web`.
2. Open the page in **Edge**, then **Chrome**, then **Firefox** if installed.
3. For each browser, record Windows version, browser version, and whether these are true:
   - Early-beta label is visible.
   - No installer, extension or Python is requested.
   - Session status still says no source gateway is served.
   - Credits show Chronara AI, Super Kevin standing, and James Tervit as main developer.
   - Resize the window and use fullscreen. The page should remain readable.
4. Mark any missing browser as untested. Do not claim support you did not open.

Live pairing, pointer crossing, reconnect and teardown are later checks. They need the unfinished gateway.

## macOS and Linux browsers

Repeat the same page checks in Safari, Chrome, Firefox and Edge where those browsers exist. Same rule: untested combinations stay untested.

## After a live gateway exists

Then, and only then, repeat the matrix for authenticated pairing, mirror, extended display, keyboard and pointer, fullscreen, reconnect and teardown. Audio and microphone stay deferred until implemented.
