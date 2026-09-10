# First installable WARP release

Status: private implementation proposal based on recovered source. No prototype installation, live display exercise, security approval or publication is implied.

The first release must support an Omarchy Linux source and a browser receiver on macOS, Windows and Linux. James explicitly confirmed that the remote end is platform independent. The recovered VNC-over-SSH/macOS launcher is prototype evidence, not the product boundary. The required remote experience is to open an authenticated private viewer URL in a supported modern browser, without installing a native receiver, Python, Bash, SSH tooling or a browser extension on that machine. Mirror and an explicitly WARP-owned extended display are the acceptance cases. WebRTC, client audio and client microphone remain deferred until implemented and verified; the current launch record reports those client routes inactive.

## Package layout

| Role | Executable entry points | Runtime dependencies observed in source |
| --- | --- | --- |
| Omarchy source | warp-dashboard, warp-control, omarchy-warp, omarchy-warp-workspace | Python 3, PyGObject/GTK4, Bash, jq, Hyprland/hyprctl, OpenSSH tools, iproute2, systemd user manager, wayvnc, isolated Python websockify environment; Chromium for extended starter tiles |
| Remote receiver on macOS / Windows / Linux | Authenticated viewer URL | Modern browser only; no required native launcher, shell or receiver daemon |
| Source-side viewer gateway | To be implemented and reviewed | Serve public viewer assets and authenticated WebSocket sessions on the Omarchy source or an explicitly trusted gateway; keep raw VNC private |
| Recovered macOS launcher | omarchy-warp-receiver (legacy reference) | Current Bash/Python/SSH/open dependencies are limitations to remove from the required receiver flow |
| Browser assets | session template and viewer.js | noVNC 1.7.0 was observed in the original tree; select and pin a reviewed upstream archive, checksum and required license/source files before packaging |
| Optional resource agent | omarchy-warp-agent | ffmpeg and pactl; resource allocation is separate from functioning client audio transport and should not be enabled by the baseline installer |

Install native components per-user on the Omarchy source (or an explicitly selected trusted gateway). The remote browser needs no WARP installation. The following filesystem layout applies only to native components: Put application assets under a versioned directory beneath ~/.local/share/omarchy-warp and expose stable launchers under ~/.local/bin. Keep user configuration under ~/.config/omarchy-warp and owned runtime/session metadata under ~/.local/state/omarchy-warp. Preserve existing paired-host records, keys and destination state; do not copy jamest's account configuration to superkevin. Installation should preview changes, reject unknown existing files, make a rollback snapshot, and perform no automatic package-manager or system update.

## Implementation sequence

1. Add a read-only preflight reporting missing dependencies and unsupported roles without running source commands or changing desktop state. Resolve Python dependencies in an isolated environment with a reviewed lock. Do not copy the original virtual environment.
2. Package the recovered Linux control path and browser assets. Make warp-control the supported source-side session coordinator. Move asset serving and the authenticated WebSocket gateway to the source or an explicitly trusted gateway. Replace mandatory SSH launch into a receiver with a private viewer URL and explicit browser pairing/authorization. Existing SSH transport may remain an optional operator route, but cannot be required on the browser device. Remove hardcoded Mac paths; preserve manager add/select/list operations used by warp-control.
3. Correct web/index.html's module path from ../viewer.js to ./viewer.js. Resolve all session, viewer and noVNC imports against the final public asset tree and exercise both static entry points before release.
4. Replace the prototype receiver's generic whole-root HTTP server with a reviewed asset/session serving boundary. Current --directory "$root" includes unrelated configuration locations in the served tree. Serve only intended public assets and validated session responses. Design and review HTTPS/WSS, private interface binding, authenticated WebSocket admission, origin/Host validation, expiring pairing and session revocation. Do not expose unauthenticated VNC/websockify, assume loopback on the source is reachable from another computer, or put reusable credentials in URLs. This is a design issue requiring review, not a completed exploit finding.
5. Track exact gateway, browser-session, optional tunnel and display ownership. A listening port is not proof it belongs to the requested source/session. Detect port collisions, verify reused endpoints against owned metadata, pin host identity when optional SSH is used, and close only resources created for the selected session. Use explicit cleanup/reconnect operations.
6. Install the optional shell plugin only after the standalone dashboard is reliable. Keep plugin updates out of a watched directory while the shell is running; preserve the existing plugin and avoid restarting James's active companion session as a side effect.

## Browser compatibility requirement

Target modern browsers across all three remote operating systems. Record exact OS/browser versions and observed outcomes; this matrix is required testing, not a claim of existing support. No universal promise for obsolete browsers or every browser fork.

| Remote OS | Required initial browser coverage |
| --- | --- |
| macOS | Safari, Chrome, Firefox, Edge |
| Windows | Edge, Chrome, Firefox |
| Linux | Firefox, Chromium/Chrome; Edge where available |

For each available combination, verify authenticated pairing, mirror and extended display, rendering, resize/scaling, keyboard/pointer input, fullscreen, reconnect and teardown. Test OS-reserved shortcuts with explicit in-viewer controls rather than assuming every key reaches the page. Record unavailable combinations as untested. Audio and microphone are deferred as stated above.

## Release gates

- Meet the browser compatibility requirement across macOS, Windows and Linux before claiming cross-platform release readiness. Opening a URL must work without a platform-specific receiver installation.
- Review the exact application and installer patch independently, including configuration exposure, SSH argument validation, local browser access, port ownership, display ownership and teardown.
- Exercise install, upgrade, conflicting-file refusal and rollback in temporary homes before applying anything to superkevin.
- Test unknown/unreachable hosts, wrong host keys, occupied ports, missing noVNC, interrupted launch and receiver failure without changing unrelated displays, browser profiles or physical audio defaults.
- Perform bounded mirror/extended/reconnect/teardown exercises on the laptop under the shared practice lock, with camera evidence and restoration. Three distinct observed successful workflows are needed before calling a tested workflow reliable.
- Publish WARP only after those gates pass. No Omamail work belongs in this release; that project is parked.

## Kevin's handoff

Kevin has the original private source packet at ~/Projects/omarchy-warp-review/source-20260910-1455. His authenticated coding executor is still pending. Once connected, start with the read-only preflight and package layout, produce a small exact diff, obtain independent Codex review, and test in a disposable home. This document is a work brief, not permission to bypass a failed review or run arbitrary source commands.
