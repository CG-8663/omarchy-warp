import QtQuick
import Quickshell
import qs.Ui as Ui

Ui.BarWidget {
  id: root
  moduleName: "io.chronara.omarchy-warp"
  // Warp is a host-side control. Showing it on HEADLESS outputs would allow
  // a remote monitor to recursively create another remote monitor.
  readonly property var hostWindow: QsWindow.window
  visible: !!hostWindow && !!hostWindow.screen && hostWindow.screen.name === "eDP-1"
  // The dashboard has its own process and cannot take down the desktop shell.
  // Keep the shell widget deliberately small: one click opens Warp; the next
  // click closes its independent dashboard process.
  function toggle() {
    Quickshell.execDetached([
      "/bin/sh", "-c",
      "if pgrep -u \"$(id -u)\" -f '[/]warp-dashboard' >/dev/null; then "
        + "pkill -u \"$(id -u)\" -f '[/]warp-dashboard'; "
        + "else warp-dashboard; fi"
    ])
  }

  implicitWidth: button.implicitWidth
  implicitHeight: button.implicitHeight

  Ui.WidgetButton {
    id: button
    anchors.fill: parent
    bar: root.bar
    tooltipText: "Omarchy Warp: pair a computer or start a display"
    text: "⚡"
    onPressed: root.toggle()
  }
}
