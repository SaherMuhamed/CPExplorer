<div align="center">

```
 ██████╗██████╗     ███████╗██╗  ██╗██████╗ ██╗      ██████╗ ██████╗ ███████╗██████╗
██╔════╝██╔══██╗    ██╔════╝╚██╗██╔╝██╔══██╗██║     ██╔═══██╗██╔══██╗██╔════╝██╔══██╗
██║     ██████╔╝    █████╗   ╚███╔╝ ██████╔╝██║     ██║   ██║██████╔╝█████╗  ██████╔╝
██║     ██╔═══╝     ██╔══╝   ██╔██╗ ██╔═══╝ ██║     ██║   ██║██╔══██╗██╔══╝  ██╔══██╗
╚██████╗██║         ███████╗██╔╝ ██╗██║     ███████╗╚██████╔╝██║  ██║███████╗██║  ██║
 ╚═════╝╚═╝         ╚══════╝╚═╝  ╚═╝╚═╝     ╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
```

**Android Content Provider Recon & Exploitation Toolkit**

*A professional-grade Python GUI for penetration testers to enumerate, query, and exploit Android Content Providers via ADB — without writing a single shell command by hand.*

---

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776ab?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey?style=for-the-badge)](.)
[![ADB](https://img.shields.io/badge/Requires-ADB-3ddc84?style=for-the-badge&logo=android&logoColor=white)](https://developer.android.com/studio/releases/platform-tools)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![PenTest](https://img.shields.io/badge/Use%20Case-PenTest%20%2F%20Bug%20Bounty-red?style=for-the-badge)](.)

</div>

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Running the Tool](#running-the-tool)
- [Feature Walkthrough](#feature-walkthrough)
  - [Device & Package](#1-device--package)
  - [Content Provider Query](#2-content-provider-query)
  - [Write Operations](#3-write-operations)
  - [Call Method](#4-call-method)
  - [Intent Broadcaster](#5-intent-broadcaster)
  - [Logcat Capture](#6-logcat-capture)
  - [File Browser](#7-file-browser)
  - [SQLite Inspector](#8-sqlite-inspector)
  - [Permission Auditor](#9-permission-auditor)
  - [Exported Component Scanner](#10-exported-component-scanner)
  - [Network Info](#11-network-info)
  - [Screenshot](#12-screenshot)
  - [Export Results](#13-export-results)
  - [Raw ADB Command](#14-raw-adb-command)
- [ADB Commands Reference](#adb-commands-reference)
- [Building a Standalone EXE](#building-a-standalone-exe)
- [Attack Scenario Examples](#attack-scenario-examples)
- [Project Structure](#project-structure)
- [Disclaimer](#disclaimer)
- [License](#license)

---

## Overview

**CP Explorer** is a dark-themed desktop GUI tool built for Android mobile penetration testers and bug bounty hunters. It wraps the most critical `adb shell` reconnaissance and exploitation workflows into a clean, tabbed interface — letting you focus on findings instead of memorising command syntax.

The tool is purpose-built around **Android Content Providers** (the most commonly misconfigured IPC mechanism on Android), but has grown to cover the full mobile attack surface: permission analysis, exported component scanning, intent fuzzing, on-device SQLite inspection, logcat monitoring, filesystem access, and network recon — all from a single window.

**Who is this for?**
- Mobile application penetration testers
- Bug bounty hunters targeting Android apps
- Android security researchers
- CTF competitors working on Android challenges
- Red teamers with Android devices in scope

---

## Features

### Content Provider Operations
| Feature | Description |
|---|---|
| **Enumerate Providers** | Auto-extracts all `content://` URIs from `dumpsys package` output, with exported flag and permission details |
| **Query** | Full `content query` with projection, selection, selection args, and sort order |
| **Read** | `content read` to stream raw bytes from a URI |
| **Insert** | `content insert` with type-safe binding (`s`=string, `i`=int, `b`=boolean, `f`=float, `l`=long) |
| **Update** | `content update` with column binding and optional WHERE clause |
| **Delete** | `content delete` with WHERE clause and confirmation guard |
| **Call Method** | `content call` to invoke custom provider methods with extras |

### Device Intelligence
| Feature | Description |
|---|---|
| **Android Version** | Resolves SDK integer to marketing name (e.g. SDK 34 → Android 14 (U)) |
| **CPU Architecture** | Detects arm64-v8a, armeabi-v7a, x86_64, x86 with human description |
| **Full Fingerprint** | 15-property sweep: manufacturer, model, build type, SELinux state, root detection, kernel version |
| **Network Info** | IP addresses, routing table, open connections, DNS servers, WiFi SSID, proxy settings |
| **Screenshot** | `screencap` + `adb pull` — saves PNG to local disk and auto-opens it |

### App Security Analysis
| Feature | Description |
|---|---|
| **Permission Auditor** | Classifies all app permissions as dangerous/normal; highlights granted dangerous permissions in red |
| **Exported Component Scanner** | Finds exported Activities, Services, Receivers, and Providers; auto-generates `am start` / `am broadcast` exploit commands |
| **App Data Paths** | Shows `dataDir`, `codePath`, `nativeLibraryPath`; lists accessible databases and SharedPreferences files |

### Dynamic Testing
| Feature | Description |
|---|---|
| **Intent Broadcaster** | `am broadcast` with action, component, data URI, and extras |
| **Activity Starter** | `am start` to launch exported activities directly |
| **Logcat Capture** | Dumps last 200 lines with optional tag filter; colour-coded by severity (E/W/D/I) |

### Data & Filesystem
| Feature | Description |
|---|---|
| **File Browser** | `ls -la`, `cat`, and `adb pull` against any device path |
| **SQLite Inspector** | List tables, run arbitrary SQL, view schema — directly on device without pulling the file |
| **Export to JSON** | Save query results from Table View as a formatted `.json` file |
| **Export to CSV** | Save query results from Table View as a `.csv` file |

### UI & Workflow
| Feature | Description |
|---|---|
| **Multi-device support** | Device selector with serial + model label; auto-refreshes badge on switch |
| **URI History** | Last 25 queried URIs stored in a clickable list |
| **Table View** | All query results rendered in a sortable, filterable Treeview grid |
| **Command Log** | Full history of every ADB command executed in the session |
| **Raw ADB** | Execute any arbitrary `adb` command directly from the UI |
| **Rounded buttons** | Canvas-based buttons with true border-radius and hover/press states |
| **Threaded execution** | All ADB calls run in daemon threads — the UI never freezes |

---

## Architecture

The project follows a clean **MVC (Model-View-Controller)** pattern:

```
main.py                         ← Entry point; creates Tk root, wires controller + view
│
├── core/
│   ├── adb_runner.py           ← MODEL: raw ADB subprocess wrapper (ADBRunner, ADBResult)
│   └── app.py                  ← CONTROLLER: AppController owns all Tk variables,
│                                  orchestrates threading, calls ADBRunner, updates View
│
├── ui/
│   ├── main_window.py          ← VIEW root: wraps Tk window, instantiates panels
│   ├── sidebar.py              ← Left panel: all input controls & section groups
│   ├── output_panel.py         ← Right panel: tabbed Output / Table / Device Info / Log
│   ├── widgets.py              ← Reusable components: FlatButton (Canvas-based rounded),
│   │                              LabeledEntry, TerminalOutput, StatusBar, DeviceInfoCard
│   ├── theme.py                ← Design tokens: colours, fonts (OS-adaptive), spacing
│   └── styles.py               ← ttk dark theme overrides
│
└── utils/
    └── parsers.py              ← Pure functions: parse content rows, extract URIs,
                                   parse permissions, parse exported components,
                                   SDK→name mapping, ABI descriptions
```

**Key design decisions:**
- `AppController` holds all `tk.StringVar` / `tk.IntVar` objects — they are only created after `tk.Tk()` exists
- The View never calls ADB directly — it only invokes `controller.on_*()` methods
- All ADB work is in daemon threads; UI updates go through `root.after(0, lambda: ...)`
- `ADBRunner` is stateless and instantiated per-call with the current device serial

---

## Prerequisites

### 1. Python 3.10 or newer
Download from [python.org](https://www.python.org/downloads/).

Verify:
```bash
python --version
# Python 3.10.x or higher
```

### 2. tkinter
Bundled with Python on Windows and macOS. On Linux:
```bash
# Debian / Ubuntu
sudo apt install python3-tk

# Fedora / RHEL
sudo dnf install python3-tkinter

# Arch
sudo pacman -S tk
```

### 3. Android Debug Bridge (ADB)
Install [Android Platform Tools](https://developer.android.com/studio/releases/platform-tools):

```bash
# Windows (via winget)
winget install Google.PlatformTools

# macOS (via Homebrew)
brew install android-platform-tools

# Ubuntu / Debian
sudo apt install adb
```

Verify ADB is in your PATH:
```bash
adb version
# Android Debug Bridge version 1.0.41
```

### 4. Enable ADB on the target device
```
Settings → Developer Options → USB Debugging → Enable
```
Connect via USB and accept the RSA key prompt on device.

Verify:
```bash
adb devices
# List of devices attached
# emulator-5554   device
```

---

## Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/CPExplorer.git
cd CPExplorer
```

No `pip install` is needed. The tool uses **only Python standard library** modules (`tkinter`, `subprocess`, `threading`, `json`, `csv`, `re`, `shlex`, `os`).

---

## Running the Tool

```bash
python main.py
```

On first launch the tool will:
1. Auto-scan for connected ADB devices
2. Populate the device dropdown
3. Fetch SDK level, architecture, and Android version for the selected device
4. Display the live device badge in the top bar

---

## Feature Walkthrough

### 1. Device & Package

**Device Selector**
The top dropdown lists all devices returned by `adb devices -l` with their serial number and model name. Click **⟳** to refresh. Switching devices automatically re-fetches the device badge (SDK, ABI, Android version).

**Android Version**
```
⚙ Android Ver  →  adb shell getprop ro.build.version.sdk
```
Resolves the integer SDK level to its marketing name:

| SDK | Name |
|-----|------|
| 28 | Android 9 Pie |
| 29 | Android 10 (Q) |
| 30 | Android 11 (R) |
| 31 | Android 12 (S) |
| 33 | Android 13 (T) |
| 34 | Android 14 (U) |
| 35 | Android 15 (V) |

**CPU Architecture**
```
⚙ CPU Arch  →  adb shell getprop ro.product.cpu.abi
```
Maps ABI strings to human descriptions:

| ABI | Description |
|-----|-------------|
| `arm64-v8a` | ARM 64-bit — modern flagship |
| `armeabi-v7a` | ARM 32-bit — legacy device |
| `x86_64` | x86 64-bit — emulator / Intel tablet |
| `x86` | x86 32-bit — emulator / older Intel |

**Full Device Fingerprint**
Collects 15 properties in a single sweep and displays them in the **Device Info** tab with colour-coded values:
- SDK level → cyan
- CPU ABI → green
- SELinux Enforcing → amber; Permissive → red *(potential privilege escalation)*
- Root detected → red *(su binary found)*
- Build type `userdebug` / `eng` → amber *(debug builds expose more attack surface)*

**Enumerate Providers**
Enter a package name and click **⬡ Enum Providers**. The tool runs:
```bash
adb shell dumpsys package <package>
```
And parses the output to extract:
- All `content://` authority URIs
- `exported=true/false` flag per provider
- `readPermission` / `writePermission` requirements

Discovered URIs are automatically added to the URI History list.

---

### 2. Content Provider Query

Enter a `content://` URI in the URI field and click **▶ QUERY**.

```bash
adb shell content query --uri content://com.example.app/users
```

**Optional parameters:**

| Field | Flag | Example |
|-------|------|---------|
| Projection | `--projection` | `_id,username,email` |
| Selection | `--where` | `role=? AND active=1` |
| Selection Args | `--arg` | `admin` |
| Sort Order | `--sort` | `_id DESC` |

Results appear in both the **Output** terminal and the **Table View** tab. The Table View supports:
- Click on any column header to sort ascending/descending
- Live filter bar — type to filter across all columns in real time
- Export to JSON or CSV

---

### 3. Write Operations

**INSERT**
```bash
adb shell content insert \
  --uri content://com.example.app/users \
  --bind username:s:hacker --bind role:s:admin
```

**UPDATE**
```bash
adb shell content update \
  --uri content://com.example.app/users \
  --bind role:s:admin \
  --where "_id=5"
```

**DELETE**
```bash
adb shell content delete \
  --uri content://com.example.app/users \
  --where "_id=5"
```

> ⚠ DELETE without a WHERE clause will delete all rows. The tool shows a confirmation dialog and warns explicitly when no WHERE clause is set.

**Value type binding codes:**

| Code | Type | Example |
|------|------|---------|
| `s` | String | `username:s:admin` |
| `i` | Integer | `age:i:25` |
| `b` | Boolean | `active:b:true` |
| `f` | Float | `score:f:9.5` |
| `l` | Long | `timestamp:l:1700000000` |

---

### 4. Call Method

Invoke a custom method on a content provider:
```bash
adb shell content call \
  --uri content://com.example.app/auth \
  --method getToken \
  --extra account:s:user@example.com
```

Use this to test custom `call()` implementations that may bypass standard query restrictions — a common vulnerability in poorly-written providers.

---

### 5. Intent Broadcaster

**Send Broadcast**
```bash
adb shell am broadcast \
  -a com.example.REFRESH_TOKEN \
  -n com.example.app/.receivers.TokenReceiver \
  --es token "INJECTED_VALUE"
```

**Start Activity**
```bash
adb shell am start \
  -a android.intent.action.VIEW \
  -n com.example.app/.ui.DeepLinkActivity \
  -d "myapp://admin/panel"
```

**Extras format** (`--es` / `--ei` / `--ez`):
```
--es key value          # string extra
--ei key 42             # integer extra
--ez key true           # boolean extra
--eia key 1,2,3         # int array
```

---

### 6. Logcat Capture

Dumps the last 200 logcat lines. Supports optional tag filter:

```bash
# All logs
adb logcat -d -v time -t 200

# Filtered by tag
adb logcat -d -v time MyApp:V *:S
```

Output is colour-coded by priority:
- `E` (Error) → red
- `W` (Warning) → amber
- `D` (Debug) → green
- `I`/`V` → dim white

**Tip:** Use the tag filter to monitor a specific package's logs in real time during dynamic testing.

---

### 7. File Browser

| Button | Command | Description |
|--------|---------|-------------|
| **📁 LS** | `adb shell ls -la <path>` | List directory with permissions, sizes, dates |
| **📄 CAT** | `adb shell cat <path>` | Print file contents to terminal |
| **⬇ PULL** | `adb pull <remote> <local>` | Pull file to local disk via save dialog |

Common paths to investigate:

```
/data/data/<package>/                   ← App private data (needs root or run-as)
/data/data/<package>/databases/         ← SQLite databases
/data/data/<package>/shared_prefs/      ← XML preference files
/data/data/<package>/files/             ← Arbitrary app files
/sdcard/Android/data/<package>/         ← External storage (world-readable)
/proc/net/                              ← Network socket info
```

---

### 8. SQLite Inspector

Directly query `.db` files on the device — no pull required (needs root or `run-as` access).

**List Tables**
```bash
adb shell sqlite3 /data/data/com.example.app/databases/main.db '.tables'
```

**Run Query**
```bash
adb shell sqlite3 -header -csv \
  /data/data/com.example.app/databases/main.db \
  "SELECT * FROM users"
```

**View Schema**
```bash
adb shell sqlite3 /data/data/com.example.app/databases/main.db '.schema'
```

Results are parsed as CSV and displayed in the terminal with the header row highlighted.

---

### 9. Permission Auditor

Runs `dumpsys package <pkg>` and classifies every permission against a list of 33 known **dangerous permissions** (as defined by Android's permission model):

**Dangerous permissions tracked:**

```
READ_CONTACTS       WRITE_CONTACTS      CAMERA
RECORD_AUDIO        READ_SMS            SEND_SMS
ACCESS_FINE_LOCATION  ACCESS_BACKGROUND_LOCATION
READ_CALL_LOG       READ_PHONE_STATE    CALL_PHONE
READ_EXTERNAL_STORAGE  WRITE_EXTERNAL_STORAGE
MANAGE_EXTERNAL_STORAGE  GET_ACCOUNTS
BODY_SENSORS        ACTIVITY_RECOGNITION
BLUETOOTH_SCAN      BLUETOOTH_CONNECT   BLUETOOTH_ADVERTISE
USE_BIOMETRIC       USE_FINGERPRINT     ANSWER_PHONE_CALLS
... and more
```

Output colour codes:
- `✔ GRANTED` in **red** — granted dangerous permission (high interest)
- `✘ denied` in dim — not yet granted

---

### 10. Exported Component Scanner

Parses `dumpsys package <pkg>` to identify all exported components and groups them by type:

| Component Type | Exploit Vector |
|---|---|
| **Activities** | Direct launch via `am start -n` — bypass authentication, access hidden screens |
| **Services** | Invoke via `am startservice -n` — trigger background operations |
| **Receivers** | Send via `am broadcast -n` — inject data, trigger privileged operations |
| **Providers** | Query via `content query --uri` — data exfiltration |

For each exported component the tool auto-generates the ready-to-run exploit command:
```
⚠  .ui.AdminActivity
       → adb shell am start -n com.example.app/.ui.AdminActivity
```

---

### 11. Network Info

Collects network state in a single sweep:

```bash
adb shell ip addr show          # Interface addresses
adb shell ip route              # Routing table
adb shell netstat -tunp         # Open TCP/UDP connections
adb shell getprop net.dns1      # Primary DNS
adb shell getprop net.dns2      # Secondary DNS
adb shell dumpsys wifi | grep mWifiInfo  # WiFi SSID / BSSID
adb shell getprop net.gprs.http-proxy    # HTTP proxy
```

---

### 12. Screenshot

Captures the current device screen and saves it locally:
```bash
adb shell screencap -p /sdcard/cp_explorer_screenshot.png
adb pull /sdcard/cp_explorer_screenshot.png <local_path>
```
A file-save dialog lets you choose the output path. The file is auto-opened after saving.

---

### 13. Export Results

After running a **QUERY**, the Table View is populated with rows. Two export formats are available:

**JSON Export**
```json
[
  {"_id": "1", "username": "admin", "role": "administrator"},
  {"_id": "2", "username": "guest", "role": "user"}
]
```

**CSV Export**
```csv
_id,username,role
1,admin,administrator
2,guest,user
```

---

### 14. Raw ADB Command

Execute any arbitrary ADB command not covered by the dedicated panels:

```bash
adb shell pm grant com.example.app android.permission.READ_SMS
adb shell settings get global adb_enabled
adb shell wm size
adb shell input tap 500 800
```

---

## ADB Commands Reference

Complete list of ADB commands used internally by the tool:

```bash
# ── Device ────────────────────────────────────────────────────────────────────
adb devices -l
adb shell getprop ro.build.version.sdk
adb shell getprop ro.build.version.release
adb shell getprop ro.product.cpu.abi
adb shell getprop ro.product.cpu.abi2
adb shell getprop ro.product.manufacturer
adb shell getprop ro.product.model
adb shell getprop ro.product.brand
adb shell getprop ro.product.device
adb shell getprop ro.build.id
adb shell getprop ro.build.type
adb shell getprop ro.build.tags
adb shell getprop ro.build.fingerprint
adb shell uname -r
adb shell getenforce
adb shell which su

# ── Content Provider ──────────────────────────────────────────────────────────
adb shell content query  --uri <uri> [--projection <cols>] [--where <sel>] [--arg <val>] [--sort <col>]
adb shell content read   --uri <uri>
adb shell content insert --uri <uri> --bind <col>:<type>:<val>
adb shell content update --uri <uri> --bind <col>:<type>:<val> [--where <clause>]
adb shell content delete --uri <uri> [--where <clause>]
adb shell content call   --uri <uri> --method <method> [--extra <key>:<type>:<val>]

# ── Package & Permissions ─────────────────────────────────────────────────────
adb shell pm list packages
adb shell dumpsys package <package>
adb shell pm dump <package>

# ── Intents ───────────────────────────────────────────────────────────────────
adb shell am broadcast -a <action> [-n <component>] [-d <uri>] [--es <key> <val>]
adb shell am start     -a <action> [-n <component>] [-d <uri>] [--es <key> <val>]

# ── Logcat ────────────────────────────────────────────────────────────────────
adb logcat -d -v time -t 200
adb logcat -d -v time <TAG>:V *:S
adb logcat -c

# ── Filesystem ────────────────────────────────────────────────────────────────
adb shell ls -la <path>
adb shell cat <path>
adb pull <remote> <local>
adb shell find <path> [-name <pattern>]

# ── SQLite ────────────────────────────────────────────────────────────────────
adb shell sqlite3 <db> '.tables'
adb shell sqlite3 -header -csv <db> '<query>'
adb shell sqlite3 <db> '.schema'

# ── Network ───────────────────────────────────────────────────────────────────
adb shell ip addr show
adb shell ip route
adb shell netstat -tunp
adb shell getprop net.dns1
adb shell getprop net.dns2
adb shell dumpsys wifi

# ── Screenshot ────────────────────────────────────────────────────────────────
adb shell screencap -p /sdcard/screenshot.png
adb pull /sdcard/screenshot.png <local>
```

---

## Building a Standalone EXE

Package the tool into a single portable binary using [PyInstaller](https://pyinstaller.org).

### Step 1 — Install PyInstaller

```bash
pip install pyinstaller
```

### Step 2 — Build

```bash
# Using the included spec (recommended)
pyinstaller build.spec

# Or manual one-liner
pyinstaller main.py \
  --name CPExplorer \
  --onefile \
  --windowed \
  --clean
```

### Step 3 — Locate the binary

```
dist/
└── CPExplorer.exe      (Windows)
    CPExplorer          (Linux / macOS)
```

### Platform Notes

**Windows** — No extra steps needed. The binary is self-contained.

**macOS** — If Gatekeeper blocks the binary:
```bash
xattr -d com.apple.quarantine dist/CPExplorer
# or sign it:
codesign --deep --force --sign - dist/CPExplorer
```

**Linux** — Mark as executable:
```bash
chmod +x dist/CPExplorer
./dist/CPExplorer
```

> **Important:** The built binary still requires `adb` to be present in the system `PATH` on the target machine. For fully portable deployment, place `adb` (or `adb.exe`) in the same directory as the binary.

---

## Attack Scenario Examples

### Scenario 1 — Unauthenticated Data Exfiltration

An app exposes a content provider with `exported=true` and no `readPermission`.

```
1. Enter package name → click ⬡ Enum Providers
2. See: content://com.bank.app/transactions   exported=true   permission=(none)
3. Click URI in history → click ▶ QUERY
4. Result: 847 rows including account numbers, balances, transaction history
5. Click ⬇ JSON to export the full dataset
```

### Scenario 2 — Privilege Escalation via Content Provider UPDATE

```
URI:     content://com.example.app/users
Column:  role
Value:   administrator
Type:    s
WHERE:   username='attacker'
→ Click ✎ UPDATE
→ Re-query to confirm role changed
```

### Scenario 3 — Exported Activity Launch (Authentication Bypass)

```
1. Enter package name → click 🔍 Component Scan
2. See: ⚠ .ui.AdminDashboardActivity  (exported=true)
        → adb shell am start -n com.example.app/.ui.AdminDashboardActivity
3. Paste the generated command into Raw ADB → Execute
4. Admin panel opens without authentication
```

### Scenario 4 — SQLite Credential Harvest

```
1. Enter package → click 📁 App Data
2. Identify: /data/data/com.example.app/databases/users.db
3. Copy path to SQLite Inspector DB Path field
4. Click 📋 Tables → reveals: users, sessions, tokens
5. Enter query: SELECT * FROM users
6. Click ▶ Query → credentials dumped directly
```

### Scenario 5 — Sensitive Data in Logcat

```
1. Leave Tag Filter blank → click 📋 Dump Logcat
2. Search output for: password, token, key, secret, Bearer
3. Find: D/AuthManager: Login successful, token=eyJhbGc...
```

---

## Project Structure

```
CPExplorer/
│
├── main.py                     ← Entry point
│
├── core/
│   ├── __init__.py
│   ├── adb_runner.py           ← ADB engine: ADBRunner class, ADBResult dataclass
│   └── app.py                  ← MVC Controller: AppController class
│
├── ui/
│   ├── __init__.py
│   ├── theme.py                ← Design tokens (colours, OS-adaptive fonts, spacing)
│   ├── styles.py               ← ttk dark theme overrides
│   ├── widgets.py              ← Custom widgets: FlatButton (Canvas/rounded),
│   │                              LabeledEntry, SectionHeader, TerminalOutput,
│   │                              StatusBar, DeviceInfoCard, ToolTip
│   ├── sidebar.py              ← Left panel: 9 collapsible control sections
│   ├── output_panel.py         ← Right panel: Output / Table / Device Info / Log tabs
│   └── main_window.py          ← Root window: title bar, device card, layout shell
│
├── utils/
│   ├── __init__.py
│   └── parsers.py              ← Pure parsing functions:
│                                  parse_content_rows, extract_content_uris,
│                                  parse_permissions, parse_exported_components,
│                                  sdk_to_android_name, abi_to_description
│
├── assets/                     ← Icons, resources (optional)
├── build.spec                  ← PyInstaller build config
├── requirements.txt            ← Runtime: none / Build: pyinstaller
├── LICENSE
└── README.md
```

---

## Disclaimer

> This tool is intended **exclusively for authorised security testing, penetration testing engagements, and security research** on devices and applications you own or have explicit written permission to test.
>
> Using this tool against devices, applications, or data without proper authorisation is **illegal** under the Computer Fraud and Abuse Act (CFAA), the Computer Misuse Act (CMA), and equivalent laws in most jurisdictions.
>
> The author(s) accept **no liability** for any misuse, damage, or legal consequences resulting from the use of this software. Always obtain proper written authorisation before testing.

---

## License

MIT © 2024 — see [LICENSE](LICENSE) for full terms.

---

<div align="center">

*Built for the security community — use responsibly.*

</div>
