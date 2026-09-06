# Omarchy Warp


> **Status: early prototype. Testing for a first release.**


Omarchy Warp explores a simple idea: use a trusted browser on another machine as extra desktop space for an Omarchy laptop.


The project started with a practical problem. A laptop may have no external monitor connected, while another machine on the same network has displays and graphics resources available. Omarchy Warp is testing whether that remote machine can provide a browser-based extended display that behaves like an additional monitor rather than a second, mirrored window.


## The concept at a glance


```mermaid
flowchart TB
    subgraph D[Your extended desktop]
        direction LR
        A[Omarchy laptop
Primary desktop] <-. Pointer crosses the display edge .-> C[Warp extended display
Own workspace and tiles]
    end
    B[Trusted paired machine
Private browser session] -->|Private local network| C
```


The browser is the display surface. The laptop remains the primary computer. A paired machine supplies the additional screen without publishing a public remote-desktop service.


## What the prototype demonstrates


- Pair a trusted machine and start an extended display session.
- Open a private browser session on that machine over the local network.
- Treat the browser session as its own monitor with its own workspace and tiles.
- Move the pointer between the laptop and the virtual display as naturally as moving between physical monitors.
- Keep the laptop workspace and remote display workspace separate.


The demo focuses on the experience of gaining more usable desktop space without adding another cable.


## A session, step by step


```mermaid
sequenceDiagram
    participant U as User
    participant L as Omarchy laptop
    participant P as Paired machine
    participant B as Private browser display


    U->>L: Choose a trusted machine and Extended display
    L->>P: Establish a private, authenticated session
    P->>B: Open the isolated browser display
    B-->>L: Present an independent virtual monitor
    U->>L: Move pointer across the chosen display edge
    L-->>B: Send focus and input to the remote workspace
    U->>B: Close display when finished
    B-->>L: End session and release the virtual monitor
```


## The idea


A virtual monitor should feel familiar:


- The laptop remains the primary machine and keeps its existing desktop state.
- A remote browser becomes an independent extended display.
- Windows, focus, keyboard input and the pointer should follow the active display in a predictable way.
- Audio, microphone and dictation should eventually be routed deliberately, not accidentally captured by the wrong machine.


Omarchy Warp is not trying to turn every browser into an unmanaged public remote-desktop endpoint. The intended model is a private, trusted-device setup for a local network first, with secure remote access considered only after the local experience is solid.


## Current testing scope


The prototype is being tested on trusted devices on a local LAN. The current focus is on:
