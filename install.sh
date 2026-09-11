#!/usr/bin/env bash
# Early-beta per-user install. No sudo. No package manager.
set -euo pipefail
cd "$(dirname "$0")"

plugin=0
preview=0
root="${HOME}"
while (($#)); do
  case "$1" in
    --plugin) plugin=1 ;;
    --preview) preview=1 ;;
    --root)
      root="${2:-}"
      [[ -n $root ]] || { echo "install.sh: --root needs a path" >&2; exit 2; }
      shift
      ;;
    -h | --help)
      cat <<'EOF'
Install Omarchy Warp for this user (early beta, not recommended for daily use).

  ./install.sh              preview missing deps, then install launchers + desktop entry
  ./install.sh --plugin     also install the optional lightning-bolt bar widget
  ./install.sh --preview    print the file plan only
  ./install.sh --root DIR   install into a fake home (for tests)

Requires an Omarchy Linux session. Does not install the native receiver,
start a display, or run pacman.
EOF
      exit 0
      ;;
    *)
      echo "install.sh: unknown option $1" >&2
      exit 2
      ;;
  esac
  shift
done

echo "Omarchy Warp early beta. Public, but not recommended to use."
echo "This does not start a live extended display."
echo
python3 tools/preflight.py --root "$root"
echo
args=(--root "$root" --source "$PWD" --web "$PWD/web/index.html" --icon "$PWD/assets/omarchy-warp-concept.png")
((plugin)) && args+=(--plugin)
if ((preview)); then
  python3 tools/install.py "${args[@]}"
  exit 0
fi
python3 tools/install.py "${args[@]}" --apply
echo
echo "Launchers: ~/.local/bin/warp-dashboard"
echo "Desktop:   Omarchy Warp"
if ((plugin)); then
  echo "Bar widget copied. If the ⚡ is missing, run: omarchy-plugin-enable io.chronara.omarchy-warp --section right"
fi
echo "Rollback:  python3 tools/install.py --rollback"
