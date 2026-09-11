import QtQuick
import QtQuick.Layouts
import Quickshell
import Quickshell.Io
import qs.Commons
import qs.Ui

Panel {
  id: root
  moduleName: "io.chronara.omarchy-warp"
  ipcTarget: "io.chronara.omarchy-warp"
  manageIpc: false

  property var anchorItem: null
  property var hostWidget: null
  readonly property var barIdentity: hostWidget || root
  readonly property color contentForeground: bar ? bar.foreground : Color.foreground
  readonly property string contentFontFamily: bar ? bar.fontFamily : Style.font.family
  readonly property string warpControl: Quickshell.env("HOME") + "/.local/bin/warp-control"

  property var hosts: []
  property string statusText: "Pair a computer on the trusted LAN or over Tailscale."
  property var pendingPreview: ({})
  property bool needsPassword: false
  property string pairName: ""
  property string pairAddress: ""
  property string pairPassword: ""
  property bool busy: false

  function refreshHosts() {
    hostsProc.running = true
  }

  function loadHosts(text) {
    var data
    try { data = JSON.parse(text) } catch (e) { statusText = "Could not read paired computers."; return }
    if (data && data.error) { statusText = String(data.error); return }
    hosts = data instanceof Array ? data : []
    if (hosts.length === 0) statusText = "No paired computers yet."
    else statusText = hosts.length + " paired computer" + (hosts.length === 1 ? "" : "s") + "."
  }

  function handleControl(text) {
    busy = false
    var data
    try { data = JSON.parse(text) } catch (e) { statusText = "Warp control failed."; return }
    if (data && data.error === "needs-password") {
      pendingPreview = data.preview || pendingPreview
      needsPassword = true
      statusText = data.message || "Host verified. Enter the account password on that computer to install this laptop’s key."
      return
    }
    if (data && data.error) { statusText = String(data.error); return }
    needsPassword = false
    pairPassword = ""
    pendingPreview = ({})
    if (data && data.name) statusText = "Paired " + data.name + "."
    refreshHosts()
  }

  function startPair() {
    if (!pairName.trim() || !pairAddress.trim()) {
      statusText = "Enter a name and a LAN or Tailscale address."
      return
    }
    busy = true
    needsPassword = false
    statusText = "Checking the destination…"
    previewProc.running = true
  }

  function confirmPair(withPassword) {
    busy = true
    statusText = withPassword ? "Installing this laptop’s SSH key…" : "Trying Tailscale SSH, then this laptop’s key…"
    confirmProc.secret = withPassword ? pairPassword : ""
    confirmProc.running = true
  }

  function openDashboard() {
    Quickshell.execDetached([root.warpControl.replace("warp-control", "warp-dashboard")])
  }

  Component.onCompleted: refreshHosts()

  Process {
    id: hostsProc
    command: [root.warpControl, "hosts"]
    stdout: StdioCollector { waitForEnd: true; onStreamFinished: root.loadHosts(text) }
  }

  Process {
    id: previewProc
    command: [root.warpControl, "pair-preview", JSON.stringify({
      name: root.pairName.trim(),
      "ethernet-lan": root.pairAddress.trim(),
      sshUser: Quickshell.env("USER") || ""
    })]
    stdout: StdioCollector {
      waitForEnd: true
      onStreamFinished: {
        var data
        try { data = JSON.parse(text) } catch (e) { root.busy = false; root.statusText = "Pair preview failed."; return }
        root.busy = false
        if (data && data.error) { root.statusText = String(data.error); return }
        root.pendingPreview = data
        root.confirmPair(false)
      }
    }
  }

  Process {
    id: confirmProc
    property string secret: ""
    stdinEnabled: true
    command: [root.warpControl, "pair-confirm", JSON.stringify(root.pendingPreview && root.pendingPreview.name ? root.pendingPreview : {})]
    environment: ({ "WARP_PAIR_PASSWORD_STDIN": secret !== "" ? "1" : "0" })
    stdout: StdioCollector { waitForEnd: true; onStreamFinished: root.handleControl(text) }
    onStarted: {
      if (secret !== "") write(secret + "\n")
      secret = ""
    }
  }

  Loader {
    active: !!root.bar && !!root.anchorItem
    sourceComponent: panelComp
  }

  Component {
    id: panelComp
    KeyboardPanel {
      id: panel
      anchorItem: root.anchorItem
      owner: root.barIdentity
      bar: root.bar
      open: root.opened
      centerOnBar: true
      contentWidth: fittedContentWidth(Style.space(420))
      contentHeight: fittedContentHeight(body.implicitHeight + Style.space(24))

      Column {
        id: body
        width: parent.width
        spacing: Style.space(10)

      Text {
        width: parent.width
        text: "Omarchy Warp"
        color: root.contentForeground
        font.family: root.contentFontFamily
        font.pixelSize: Style.font.heading
      }

      Text {
        width: parent.width
        wrapMode: Text.WordWrap
        text: "Trusted LAN + Tailscale SSH. A one-time password installs this laptop’s key. Tunnels stay on SSH after that."
        color: Qt.darker(root.contentForeground, 1.4)
        font.family: root.contentFontFamily
        font.pixelSize: Style.font.bodySmall
      }

      Repeater {
        model: root.hosts
        delegate: Text {
          width: body.width
          text: "• " + modelData.name
          color: root.contentForeground
          font.family: root.contentFontFamily
          font.pixelSize: Style.font.body
        }
      }

      TextField {
        width: parent.width
        placeholderText: "Computer name"
        text: root.pairName
        foreground: root.contentForeground
        onTextChanged: root.pairName = text
      }

      TextField {
        width: parent.width
        placeholderText: "LAN or Tailscale address"
        text: root.pairAddress
        foreground: root.contentForeground
        onTextChanged: root.pairAddress = text
      }

      TextField {
        width: parent.width
        visible: root.needsPassword
        password: true
        placeholderText: "Account password on that computer"
        text: root.pairPassword
        foreground: root.contentForeground
        onTextChanged: root.pairPassword = text
      }

      Row {
        spacing: Style.space(8)
        Button {
          text: root.needsPassword ? "Install key and pair" : "Pair this computer"
          enabled: !root.busy
          onClicked: root.needsPassword ? root.confirmPair(true) : root.startPair()
        }
        Button {
          text: "Open dashboard"
          enabled: !root.busy
          onClicked: root.openDashboard()
        }
      }

      Text {
        width: parent.width
        wrapMode: Text.WordWrap
        text: root.statusText
        color: root.contentForeground
        font.family: root.contentFontFamily
        font.pixelSize: Style.font.bodySmall
      }
    }
    }
  }
}
