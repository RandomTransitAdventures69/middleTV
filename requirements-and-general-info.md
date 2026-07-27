# TV OS Requirements

## Required

- Debian (or Debian-based Linux distribution)
- Python 3.10 or newer
- Root/admin account access
- Keyboard for navigation
- Internet connection (for online apps)

---

## Recommended Hardware

- 64-bit x86_64 processor (Intel/AMD)
- 4GB RAM or more
- SSD storage recommended
- 1080p or higher display
- USB keyboard

---

## Supported Devices

### Desktop PCs / Mini PCs
**Recommended platform**

TV OS works best on standard x86_64 computers.

### Raspberry Pi 4/5
**ARM64 support**

Raspberry Pi support (since 1. i have a few pis, 2. theyre mine jeff geerling and 3, its linux so it might work?????????)

### Repurposed Laptops

Older laptops can be converted into TV OS systems.

---

## Architecture Support

| Architecture | Status |
|---|---|
| x86_64 | ✅ Recommended |
| ARM64 (windows) | never coming lol |
| Apple Silicon | 🟡 Planned |
| Intel macOS | 🟡 Planned |

---

## Notes

Although not required, **x86_64 hardware is recommended** for the best compatibility and application support.

Some features, such as web-based apps, may require additional dependencies.

---

## Installation Requirements

The installer currently requires:

- Debian-based distribution
- Internet access
- Permission to install system packages

Supported distributions include:

- Debian
- Ubuntu
- Linux Mint
- Pop!_OS
- Other Debian-based distributions
- middleOS (hey i made that!)
---

## Recommended Setup

For the best experience:
1. Rasperry Pi 5 (8GB)
2. Rasperry Pi OS
3. TV
4. Logitech k400r
5. Ethernet



## Minimum (for both arm AND x86)

- Dual-core CPU
- 4GB RAM
- 16GB storage
- 1366x768 display

## Recommended (for x86)

- Intel N100 or better
- 8GB RAM
- 128GB SSD
- Ethernet
- Logitech K400-style keyboard



# Apps

TV OS includes a collection of TV-friendly applications designed for keyboard navigation and large screens.

## Available Apps

| App | Status | Description |
|---|---|---|
| 🌦 Weather | ✅ Available | Shows current weather conditions using a weather API |
| 🎬 Jellyfin | ✅ Available | Access your Jellyfin media server |
| ▶️ YouTube | ✅ Available | Watch YouTube using an embedded browser |
| 🎵 YouTube Music | ✅ Available | Listen to YouTube Music using an embedded browser |
| ⚙ Settings | 🟡 In Development | Configure TV OS settings |
| 🖥 Server Dashboard |  never lol its too many tokens | Monitor local servers and services |

---

## Planned Apps

| App | Status | Description |
|---|---|---|
| 🌐 Browser | Planned | General purpose web browser |
| 🎵 Local Music | Planned | Play local music files |
| 📁 File Manager | Planned | Browse local storage |
| 📺 RF | Planned | wow look RF :0 |
| 🎮 Game Launcher | Planned | Launch games and emulators |
| 📡 Network Tools | Planned | View network information and diagnostics |
| 🔔 Notifications | Planned | System notifications |



---

## Future Platform Apps

| Platform | Status |
|---|---|
| Linux x86_64 | ✅ Main platform |
| Linux ARM64 | ✅ Main platform |
| Windows | ✅ Main platform |
| macOS Intel | 🟡 Planned |
| macOS Apple Silicon | 🟡 Planned |
| Android x86 | ❌ never lol |

---

## App Design Goals

All TV OS apps are designed for:

- Large displays
- Keyboard navigation
- Remote-friendly controls
- Fullscreen operation
- Low-power devices
