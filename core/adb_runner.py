"""
core/adb_runner.py — Low-level ADB command execution engine
"""

import subprocess
import shlex
from dataclasses import dataclass
from typing import Optional


@dataclass
class ADBResult:
    stdout: str
    stderr: str
    returncode: int
    command: str

    @property
    def ok(self) -> bool:
        return self.returncode == 0

    @property
    def output(self) -> str:
        return self.stdout or self.stderr


class ADBRunner:
    """Handles raw ADB subprocess execution with device targeting."""

    def __init__(self, device_serial: Optional[str] = None, timeout: int = 15):
        self.device_serial = device_serial
        self.timeout = timeout

    def _flag(self) -> str:
        return f"-s {self.device_serial}" if self.device_serial else ""

    def run(self, command: str, timeout: Optional[int] = None) -> ADBResult:
        t = timeout or self.timeout
        try:
            result = subprocess.run(
                command, shell=True, capture_output=True,
                text=True, timeout=t
            )
            return ADBResult(
                stdout=result.stdout.strip(),
                stderr=result.stderr.strip(),
                returncode=result.returncode,
                command=command,
            )
        except subprocess.TimeoutExpired:
            return ADBResult("", "Command timed out", 1, command)
        except FileNotFoundError:
            return ADBResult("", "adb not found — is it in your PATH?", 1, command)
        except Exception as e:
            return ADBResult("", str(e), 1, command)

    def shell(self, shell_cmd: str, timeout: Optional[int] = None) -> ADBResult:
        flag = self._flag()
        full = f"adb {flag} shell {shell_cmd}".strip()
        return self.run(full, timeout)

    def adb(self, adb_cmd: str, timeout: Optional[int] = None) -> ADBResult:
        flag = self._flag()
        full = f"adb {flag} {adb_cmd}".strip()
        return self.run(full, timeout)

    # ── Device ───────────────────────────────────────────────────────────────
    def get_devices(self) -> list[dict]:
        result = self.run("adb devices -l")
        devices = []
        for line in result.stdout.splitlines()[1:]:
            line = line.strip()
            if not line or "offline" in line:
                continue
            if "device" in line:
                parts = line.split()
                serial = parts[0]
                info = {"serial": serial, "model": "", "transport": "", "product": ""}
                for p in parts[1:]:
                    if ":" in p:
                        k, v = p.split(":", 1)
                        if k == "model":        info["model"] = v
                        if k == "transport_id": info["transport"] = v
                        if k == "product":      info["product"] = v
                devices.append(info)
        return devices

    def get_android_version(self) -> ADBResult:
        return self.shell("getprop ro.build.version.sdk")

    def get_architecture(self) -> ADBResult:
        return self.shell("getprop ro.product.cpu.abi")

    def get_device_info(self) -> dict:
        props = {
            "Android SDK":  "getprop ro.build.version.sdk",
            "Android Ver":  "getprop ro.build.version.release",
            "CPU ABI":      "getprop ro.product.cpu.abi",
            "CPU ABI2":     "getprop ro.product.cpu.abi2",
            "Manufacturer": "getprop ro.product.manufacturer",
            "Model":        "getprop ro.product.model",
            "Brand":        "getprop ro.product.brand",
            "Device":       "getprop ro.product.device",
            "Build ID":     "getprop ro.build.id",
            "Build Type":   "getprop ro.build.type",
            "Build Tags":   "getprop ro.build.tags",
            "Fingerprint":  "getprop ro.build.fingerprint",
            "Kernel":       "uname -r",
            "SELinux":      "getenforce",
            "Root (su)":    "which su",
        }
        result = {}
        for label, cmd in props.items():
            r = self.shell(cmd)
            result[label] = r.stdout if r.ok else f"[error: {r.stderr}]"
        return result

    # ── Content Provider ──────────────────────────────────────────────────────
    def content_query(self, uri: str, projection: str = "", where: str = "",
                      sel_args: str = "", sort: str = "") -> ADBResult:
        cmd = f"content query --uri {shlex.quote(uri)}"
        if projection: cmd += f" --projection {shlex.quote(projection)}"
        if where:      cmd += f" --where {shlex.quote(where)}"
        if sel_args:   cmd += f" --arg {shlex.quote(sel_args)}"
        if sort:       cmd += f" --sort {shlex.quote(sort)}"
        return self.shell(cmd, timeout=20)

    def content_read(self, uri: str) -> ADBResult:
        return self.shell(f"content read --uri {shlex.quote(uri)}", timeout=20)

    def content_insert(self, uri: str, col: str, val: str, val_type: str = "s") -> ADBResult:
        return self.shell(
            f"content insert --uri {shlex.quote(uri)} "
            f"--bind {shlex.quote(col)}:{val_type}:{shlex.quote(val)}"
        )

    def content_update(self, uri: str, col: str, val: str,
                       val_type: str = "s", where: str = "") -> ADBResult:
        cmd = (f"content update --uri {shlex.quote(uri)} "
               f"--bind {shlex.quote(col)}:{val_type}:{shlex.quote(val)}")
        if where: cmd += f" --where {shlex.quote(where)}"
        return self.shell(cmd)

    def content_delete(self, uri: str, where: str = "") -> ADBResult:
        cmd = f"content delete --uri {shlex.quote(uri)}"
        if where: cmd += f" --where {shlex.quote(where)}"
        return self.shell(cmd)

    def content_call(self, uri: str, method: str, extras: str = "") -> ADBResult:
        cmd = f"content call --uri {shlex.quote(uri)} --method {shlex.quote(method)}"
        if extras: cmd += f" {extras}"
        return self.shell(cmd)

    def enumerate_providers(self, package: str) -> ADBResult:
        return self.shell(f"dumpsys package {shlex.quote(package)}", timeout=20)

    def list_packages(self, flags: str = "") -> ADBResult:
        return self.shell(f"pm list packages {flags}")

    # ── NEW: Permission Auditor ───────────────────────────────────────────────
    def get_dangerous_permissions(self, package: str) -> ADBResult:
        """Dump granted dangerous permissions for a package."""
        return self.shell(f"dumpsys package {shlex.quote(package)}", timeout=20)

    def get_all_permissions(self, package: str) -> ADBResult:
        return self.shell(f"pm list permissions -g -d", timeout=20)

    # ── NEW: Intent Broadcaster ───────────────────────────────────────────────
    def send_broadcast(self, action: str, component: str = "",
                       extras: str = "", uri: str = "") -> ADBResult:
        cmd = f"am broadcast -a {shlex.quote(action)}"
        if component: cmd += f" -n {shlex.quote(component)}"
        if uri:       cmd += f" -d {shlex.quote(uri)}"
        if extras:    cmd += f" {extras}"
        return self.shell(cmd, timeout=15)

    def start_activity(self, action: str = "", component: str = "",
                       uri: str = "", extras: str = "") -> ADBResult:
        cmd = "am start"
        if action:    cmd += f" -a {shlex.quote(action)}"
        if component: cmd += f" -n {shlex.quote(component)}"
        if uri:       cmd += f" -d {shlex.quote(uri)}"
        if extras:    cmd += f" {extras}"
        return self.shell(cmd, timeout=15)

    # ── NEW: Logcat Capture ───────────────────────────────────────────────────
    def logcat_dump(self, tag_filter: str = "", lines: int = 200) -> ADBResult:
        """Get last N lines of logcat, optionally filtered by tag."""
        flag = self._flag()
        if tag_filter:
            cmd = f"adb {flag} logcat -d -v time {shlex.quote(tag_filter)}:V *:S"
        else:
            cmd = f"adb {flag} logcat -d -v time -t {lines}"
        return self.run(cmd.strip(), timeout=20)

    def logcat_clear(self) -> ADBResult:
        flag = self._flag()
        return self.run(f"adb {flag} logcat -c".strip())

    # ── NEW: File System Browser ──────────────────────────────────────────────
    def ls(self, path: str) -> ADBResult:
        return self.shell(f"ls -la {shlex.quote(path)}", timeout=10)

    def cat_file(self, path: str) -> ADBResult:
        return self.shell(f"cat {shlex.quote(path)}", timeout=15)

    def pull_file(self, remote_path: str, local_path: str) -> ADBResult:
        flag = self._flag()
        return self.run(
            f"adb {flag} pull {shlex.quote(remote_path)} {shlex.quote(local_path)}".strip(),
            timeout=30,
        )

    def find_files(self, path: str, name_pattern: str = "") -> ADBResult:
        cmd = f"find {shlex.quote(path)}"
        if name_pattern:
            cmd += f" -name {shlex.quote(name_pattern)}"
        cmd += " 2>/dev/null"
        return self.shell(cmd, timeout=20)

    # ── NEW: SQLite Inspector ─────────────────────────────────────────────────
    def sqlite_tables(self, db_path: str) -> ADBResult:
        return self.shell(
            f"sqlite3 {shlex.quote(db_path)} '.tables'", timeout=10
        )

    def sqlite_query(self, db_path: str, query: str) -> ADBResult:
        return self.shell(
            f"sqlite3 -header -csv {shlex.quote(db_path)} {shlex.quote(query)}",
            timeout=15,
        )

    def sqlite_schema(self, db_path: str, table: str = "") -> ADBResult:
        if table:
            q = f".schema {table}"
        else:
            q = ".schema"
        return self.shell(f"sqlite3 {shlex.quote(db_path)} {shlex.quote(q)}", timeout=10)

    # ── NEW: Network Info ─────────────────────────────────────────────────────
    def get_network_info(self) -> dict:
        cmds = {
            "IP Address":   "ip addr show",
            "Routes":       "ip route",
            "Connections":  "netstat -tunp 2>/dev/null || ss -tunp",
            "DNS":          "getprop net.dns1",
            "DNS2":         "getprop net.dns2",
            "WiFi SSID":    "dumpsys wifi | grep 'mWifiInfo'",
            "Proxy":        "getprop net.gprs.http-proxy",
        }
        result = {}
        for label, cmd in cmds.items():
            r = self.shell(cmd)
            result[label] = r.stdout if r.stdout else "(none)"
        return result

    # ── NEW: App Data Paths ───────────────────────────────────────────────────
    def get_app_data_paths(self, package: str) -> ADBResult:
        return self.shell(
            f"pm dump {shlex.quote(package)} | grep -E 'dataDir|codePath|resourcePath|nativeLibraryPath'",
            timeout=10,
        )

    def list_app_databases(self, package: str) -> ADBResult:
        return self.shell(
            f"ls -la /data/data/{shlex.quote(package)}/databases/ 2>/dev/null || "
            f"run-as {shlex.quote(package)} ls -la databases/ 2>/dev/null",
            timeout=10,
        )

    def list_app_shared_prefs(self, package: str) -> ADBResult:
        return self.shell(
            f"ls -la /data/data/{shlex.quote(package)}/shared_prefs/ 2>/dev/null || "
            f"run-as {shlex.quote(package)} ls -la shared_prefs/ 2>/dev/null",
            timeout=10,
        )

    def cat_shared_pref(self, package: str, filename: str) -> ADBResult:
        return self.shell(
            f"run-as {shlex.quote(package)} cat shared_prefs/{shlex.quote(filename)} 2>/dev/null || "
            f"cat /data/data/{shlex.quote(package)}/shared_prefs/{shlex.quote(filename)} 2>/dev/null",
            timeout=10,
        )

    # ── NEW: Exported Component Scanner ──────────────────────────────────────
    def get_exported_activities(self, package: str) -> ADBResult:
        return self.shell(f"dumpsys package {shlex.quote(package)}", timeout=20)

    # ── NEW: Screenshot ──────────────────────────────────────────────────────
    def screenshot(self, local_path: str) -> ADBResult:
        flag = self._flag()
        remote = "/sdcard/cp_explorer_screenshot.png"
        r1 = self.shell(f"screencap -p {remote}")
        if not r1.ok:
            return r1
        return self.run(
            f"adb {flag} pull {remote} {shlex.quote(local_path)}".strip(),
            timeout=15,
        )
    