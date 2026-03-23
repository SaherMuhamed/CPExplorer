"""
core/app.py — Main application controller (MVC Controller layer)
"""

import tkinter as tk
from tkinter import messagebox, filedialog
import threading
import os
import json
import csv
import re
from datetime import datetime

from core.adb_runner import ADBRunner
from utils.parsers import (
    parse_content_rows, extract_content_uris,
    sdk_to_android_name, abi_to_description,
    parse_permissions, parse_exported_components,
)
from ui import theme as T


class AppController:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.runner = ADBRunner()
        self._logcat_running = False
        self._logcat_thread  = None
        self._init_vars()

    # ── Tkinter Variables ─────────────────────────────────────────────────────
    def _init_vars(self):
        self.device_var         = tk.StringVar()
        self.package_var        = tk.StringVar()
        self.uri_var            = tk.StringVar(value="content://")
        self.projection_var     = tk.StringVar()
        self.selection_var      = tk.StringVar()
        self.sel_args_var       = tk.StringVar()
        self.sort_order_var     = tk.StringVar()
        self.col_var            = tk.StringVar()
        self.val_var            = tk.StringVar()
        self.val_type_var       = tk.StringVar(value="s")
        self.where_var          = tk.StringVar()
        self.method_var         = tk.StringVar()
        self.extra_var          = tk.StringVar()
        self.raw_cmd_var        = tk.StringVar()
        # Intent
        self.intent_action_var  = tk.StringVar()
        self.intent_comp_var    = tk.StringVar()
        self.intent_uri_var     = tk.StringVar()
        self.intent_extras_var  = tk.StringVar()
        # Logcat
        self.logcat_filter_var  = tk.StringVar()
        # File browser
        self.fb_path_var        = tk.StringVar(value="/data/data")
        # SQLite
        self.sqlite_db_var      = tk.StringVar()
        self.sqlite_query_var   = tk.StringVar(value="SELECT * FROM ")

        self.device_var.trace_add("write", self._on_device_changed)

    def set_view(self, view):
        self.view = view

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _get_runner(self) -> ADBRunner:
        serial = self.device_var.get().split()[0] if self.device_var.get() else None
        return ADBRunner(device_serial=serial)

    def _thread(self, fn, *args):
        threading.Thread(target=fn, args=args, daemon=True).start()

    def _status(self, msg: str, state: str = "idle"):
        self.root.after(0, lambda: self.view.status_bar.set(msg, state))

    def _set_cmd(self, cmd: str):
        self.root.after(0, lambda: self.view.status_bar.set_cmd(cmd))

    def _header(self, title: str, cmd: str = ""):
        self.root.after(0, lambda: self.view.output_panel.header(title, cmd))

    def _writeln(self, text: str = "", tag: str = ""):
        self.root.after(0, lambda: self.view.output_panel.writeln(text, tag))

    def _log(self, cmd: str):
        self.root.after(0, lambda: self.view.output_panel.log_command(cmd))
        self._set_cmd(cmd)

    def _switch_tab(self, idx: int):
        self.root.after(0, lambda: self.view.output_panel.switch_to(idx))

    def _add_uri_history(self, uri: str):
        lb = self.view.sidebar.uri_list
        existing = list(lb.get(0, "end"))
        if uri not in existing:
            self.root.after(0, lambda: lb.insert(0, uri))
            if lb.size() > 25:
                self.root.after(0, lambda: lb.delete(25, "end"))

    def _on_device_changed(self, *_):
        self._thread(self._fetch_device_badge)

    def _fetch_device_badge(self):
        r = self._get_runner()
        sdk = r.get_android_version().stdout.strip()
        abi = r.get_architecture().stdout.strip()
        ver = r.shell("getprop ro.build.version.release").stdout.strip()
        if sdk or abi:
            self.root.after(0, lambda: self.view.device_card.update(sdk, abi, ver))

    # ── Device ────────────────────────────────────────────────────────────────
    def on_refresh_devices(self):
        self._status("Scanning for devices…", "busy")
        self._thread(self._refresh_devices)

    def _refresh_devices(self):
        runner = ADBRunner()
        devices = runner.get_devices()
        labels = []
        for d in devices:
            label = d["serial"]
            if d["model"]:
                label += f"  [{d['model']}]"
            labels.append(label)

        def update():
            self.view.sidebar.device_combo["values"] = labels
            if labels:
                self.view.sidebar.device_combo.current(0)
                self._status(f"{len(labels)} device(s) found", "ok")
                self._thread(self._fetch_device_badge)
            else:
                self._status("No devices found — check ADB", "error")
        self.root.after(0, update)

    # ── Device Info ───────────────────────────────────────────────────────────
    def on_get_android_version(self):
        self._status("Fetching Android version…", "busy")
        self._thread(self._get_android_version)

    def _get_android_version(self):
        r = self._get_runner()
        result = r.get_android_version()
        self._log(result.command)
        self._header("ANDROID VERSION", result.command)
        if result.ok and result.stdout:
            sdk = result.stdout.strip()
            name = sdk_to_android_name(sdk)
            self._writeln(f"  SDK Level : {sdk}", "key")
            self._writeln(f"  Android   : {name}", "success")
            self.root.after(0, lambda: self.view.device_card.update(sdk=sdk))
            self._status(f"Android SDK {sdk} — {name}", "ok")
        else:
            self._writeln(f"  Error: {result.stderr}", "error")
            self._status("Failed", "error")
        self._switch_tab(0)

    def on_get_architecture(self):
        self._status("Fetching CPU architecture…", "busy")
        self._thread(self._get_architecture)

    def _get_architecture(self):
        r = self._get_runner()
        result = r.get_architecture()
        self._log(result.command)
        self._header("CPU ARCHITECTURE", result.command)
        if result.ok and result.stdout:
            abi = result.stdout.strip()
            self._writeln(f"  ABI  : {abi}", "key")
            self._writeln(f"  Desc : {abi_to_description(abi)}", "success")
            self.root.after(0, lambda: self.view.device_card.update(abi=abi))
            self._status(f"Architecture: {abi}", "ok")
        else:
            self._writeln(f"  Error: {result.stderr}", "error")
            self._status("Failed", "error")
        self._switch_tab(0)

    def on_full_device_info(self):
        self._status("Collecting device fingerprint…", "busy")
        self._thread(self._full_device_info)

    def _full_device_info(self):
        r = self._get_runner()
        info = r.get_device_info()
        self._log("adb shell [device fingerprint sweep]")
        self.root.after(0, lambda: self.view.output_panel.populate_device_info(info))
        sdk = info.get("Android SDK", "")
        abi = info.get("CPU ABI", "")
        ver = info.get("Android Ver", "")
        self.root.after(0, lambda: self.view.device_card.update(sdk, abi, ver))
        self._status("Device fingerprint collected", "ok")

    # ── NEW: Network Info ─────────────────────────────────────────────────────
    def on_network_info(self):
        self._status("Gathering network info…", "busy")
        self._thread(self._network_info)

    def _network_info(self):
        r = self._get_runner()
        self._header("NETWORK INFORMATION")
        info = r.get_network_info()
        for label, val in info.items():
            self._writeln(f"\n  ── {label} ──", "key")
            for line in val.splitlines():
                self._writeln(f"  {line}", "val")
        self._status("Network info collected", "ok")
        self._switch_tab(0)

    # ── NEW: Screenshot ───────────────────────────────────────────────────────
    def on_screenshot(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png")],
            initialfile=f"screenshot_{datetime.now().strftime('%H%M%S')}.png",
            title="Save Screenshot",
        )
        if not path:
            return
        self._status("Taking screenshot…", "busy")
        self._thread(self._screenshot, path)

    def _screenshot(self, local_path: str):
        r = self._get_runner()
        result = r.screenshot(local_path)
        self._header("SCREENSHOT", result.command)
        if result.ok:
            self._writeln(f"  ✔ Saved → {local_path}", "success")
            self._status("Screenshot saved", "ok")
            # Try to open it
            try:
                os.startfile(local_path)
            except Exception:
                pass
        else:
            self._writeln(f"  ✘ {result.stderr}", "error")
            self._status("Screenshot failed", "error")
        self._switch_tab(0)

    # ── Package / Provider ────────────────────────────────────────────────────
    def on_list_packages(self):
        self._status("Listing packages…", "busy")
        self._thread(self._list_packages)

    def _list_packages(self):
        r = self._get_runner()
        result = r.list_packages()
        self._log(result.command)
        self._header("INSTALLED PACKAGES", result.command)
        if not result.ok:
            self._writeln(f"  Error: {result.stderr}", "error")
            self._status("Failed", "error")
            return
        pkgs = sorted(line.replace("package:", "").strip()
                      for line in result.stdout.splitlines() if line.strip())
        for p in pkgs:
            self._writeln(f"  {p}")
        self._writeln()
        self._writeln(f"  ► {len(pkgs)} packages", "success")
        self._status(f"{len(pkgs)} packages listed", "ok")
        self._switch_tab(0)

    def on_enumerate_providers(self):
        pkg = self.package_var.get().strip()
        if not pkg:
            messagebox.showwarning("Input Required", "Enter a package name.")
            return
        self._status(f"Enumerating providers for {pkg}…", "busy")
        self._thread(self._enumerate_providers, pkg)

    def _enumerate_providers(self, pkg: str):
        r = self._get_runner()
        result = r.enumerate_providers(pkg)
        self._log(result.command)
        self._header(f"CONTENT PROVIDERS  —  {pkg}", result.command)
        if not result.ok and not result.stdout:
            self._writeln(f"  Error: {result.stderr}", "error")
            self._status("Enumeration failed", "error")
            return
        uris = extract_content_uris(result.stdout)
        if uris:
            self._writeln(f"  Found {len(uris)} URI(s):\n", "success")
            for u in uris:
                exp_color = "warn" if u["exported"] == "true" else "dim"
                self._writeln(f"  ► {u['uri']}", "bright")
                self._writeln(f"      exported   = {u['exported']}", exp_color)
                if u["permission"]:
                    self._writeln(f"      permission = {u['permission']}", "key")
                self._writeln()
                self._add_uri_history(u["uri"])
        else:
            self._writeln("  No content:// URIs found.", "warn")
        self._status(f"Found {len(uris)} URIs for {pkg}", "ok")
        self._switch_tab(0)

    # ── NEW: Permission Auditor ───────────────────────────────────────────────
    def on_permission_audit(self):
        pkg = self.package_var.get().strip()
        if not pkg:
            messagebox.showwarning("Input Required", "Enter a package name first.")
            return
        self._status(f"Auditing permissions for {pkg}…", "busy")
        self._thread(self._permission_audit, pkg)

    def _permission_audit(self, pkg: str):
        r = self._get_runner()
        result = r.get_dangerous_permissions(pkg)
        self._log(result.command)
        self._header(f"PERMISSION AUDIT  —  {pkg}", result.command)
        perms = parse_permissions(result.stdout)
        if perms["dangerous"]:
            self._writeln(f"  ⚠ Dangerous Permissions ({len(perms['dangerous'])}):", "warn")
            for p in perms["dangerous"]:
                status = "✔ GRANTED" if p["granted"] else "✘ denied"
                color  = "error" if p["granted"] else "dim"
                self._writeln(f"    {status}  {p['name']}", color)
        else:
            self._writeln("  No dangerous permissions found.", "success")
        if perms["normal"]:
            self._writeln(f"\n  Normal Permissions ({len(perms['normal'])}):", "dim")
            for p in perms["normal"][:20]:
                self._writeln(f"    • {p['name']}", "dim")
            if len(perms["normal"]) > 20:
                self._writeln(f"    … and {len(perms['normal'])-20} more", "dim")
        self._status(f"Audit complete — {len(perms['dangerous'])} dangerous perms", "ok")
        self._switch_tab(0)

    # ── NEW: Exported Component Scanner ──────────────────────────────────────
    def on_component_scan(self):
        pkg = self.package_var.get().strip()
        if not pkg:
            messagebox.showwarning("Input Required", "Enter a package name first.")
            return
        self._status(f"Scanning exported components for {pkg}…", "busy")
        self._thread(self._component_scan, pkg)

    def _component_scan(self, pkg: str):
        r = self._get_runner()
        result = r.get_exported_activities(pkg)
        self._log(result.command)
        self._header(f"EXPORTED COMPONENT SCAN  —  {pkg}", result.command)
        comps = parse_exported_components(result.stdout, pkg)
        total = sum(len(v) for v in comps.values())
        if total == 0:
            self._writeln("  No exported components found.", "success")
        for kind, items in comps.items():
            if not items:
                continue
            self._writeln(f"\n  ── {kind} ({len(items)}) ──", "key")
            for item in items:
                self._writeln(f"    ⚠  {item}", "warn")
                # Show am start / am broadcast hint
                if kind == "Activities":
                    self._writeln(f"         → adb shell am start -n {pkg}/{item}", "dim")
                elif kind == "Receivers":
                    self._writeln(f"         → adb shell am broadcast -n {pkg}/{item}", "dim")
                elif kind == "Services":
                    self._writeln(f"         → adb shell am startservice -n {pkg}/{item}", "dim")
        self._status(f"Found {total} exported components", "ok" if total == 0 else "warn")
        self._switch_tab(0)

    # ── NEW: App Data Explorer ────────────────────────────────────────────────
    def on_app_data_paths(self):
        pkg = self.package_var.get().strip()
        if not pkg:
            messagebox.showwarning("Input Required", "Enter a package name first.")
            return
        self._status("Fetching app data paths…", "busy")
        self._thread(self._app_data_paths, pkg)

    def _app_data_paths(self, pkg: str):
        r = self._get_runner()
        self._header(f"APP DATA PATHS  —  {pkg}")
        paths_r = r.get_app_data_paths(pkg)
        self._log(paths_r.command)
        if paths_r.stdout:
            for line in paths_r.stdout.splitlines():
                self._writeln(f"  {line.strip()}", "val")
        self._writeln("\n  ── Databases ──", "key")
        db_r = r.list_app_databases(pkg)
        self._log(db_r.command)
        if db_r.stdout:
            for line in db_r.stdout.splitlines():
                self._writeln(f"  {line}", "success" if ".db" in line else "val")
        else:
            self._writeln("  (none accessible — may need root)", "dim")

        self._writeln("\n  ── Shared Prefs ──", "key")
        sp_r = r.list_app_shared_prefs(pkg)
        self._log(sp_r.command)
        if sp_r.stdout:
            for line in sp_r.stdout.splitlines():
                self._writeln(f"  {line}", "warn" if ".xml" in line else "val")
        else:
            self._writeln("  (none accessible — may need root)", "dim")
        self._status("App data paths fetched", "ok")
        self._switch_tab(0)

    # ── NEW: Intent Broadcaster ───────────────────────────────────────────────
    def on_send_broadcast(self):
        action = self.intent_action_var.get().strip()
        if not action:
            messagebox.showwarning("Input Required", "Action is required.")
            return
        self._status(f"Sending broadcast: {action}…", "busy")
        self._thread(self._send_broadcast, action)

    def _send_broadcast(self, action: str):
        r = self._get_runner()
        result = r.send_broadcast(
            action,
            component=self.intent_comp_var.get().strip(),
            extras=self.intent_extras_var.get().strip(),
            uri=self.intent_uri_var.get().strip(),
        )
        self._log(result.command)
        self._header(f"BROADCAST  —  {action}", result.command)
        for line in (result.stdout or result.stderr).splitlines():
            self._writeln(f"  {line}", "success" if result.ok else "error")
        self._status("Broadcast sent" if result.ok else "Broadcast failed",
                     "ok" if result.ok else "error")
        self._switch_tab(0)

    def on_start_activity(self):
        action = self.intent_action_var.get().strip()
        comp   = self.intent_comp_var.get().strip()
        if not action and not comp:
            messagebox.showwarning("Input Required", "Action or Component required.")
            return
        self._status("Starting activity…", "busy")
        self._thread(self._start_activity, action, comp)

    def _start_activity(self, action: str, comp: str):
        r = self._get_runner()
        result = r.start_activity(
            action=action, component=comp,
            uri=self.intent_uri_var.get().strip(),
            extras=self.intent_extras_var.get().strip(),
        )
        self._log(result.command)
        self._header(f"START ACTIVITY  —  {comp or action}", result.command)
        for line in (result.stdout or result.stderr).splitlines():
            self._writeln(f"  {line}", "success" if result.ok else "error")
        self._status("Activity started" if result.ok else "Failed",
                     "ok" if result.ok else "error")
        self._switch_tab(0)

    # ── NEW: Logcat ───────────────────────────────────────────────────────────
    def on_logcat_dump(self):
        self._status("Dumping logcat…", "busy")
        self._thread(self._logcat_dump)

    def _logcat_dump(self):
        r = self._get_runner()
        filt = self.logcat_filter_var.get().strip()
        result = r.logcat_dump(tag_filter=filt)
        self._log(result.command)
        self._header(f"LOGCAT DUMP  {('— ' + filt) if filt else ''}", result.command)
        lines = result.stdout.splitlines()
        for line in lines:
            tag = "error" if " E " in line else "warn" if " W " in line else \
                  "success" if " D " in line else "dim"
            self._writeln(f"  {line}", tag)
        self._writeln(f"\n  ► {len(lines)} lines", "success")
        self._status(f"Logcat: {len(lines)} lines", "ok")
        self._switch_tab(0)

    def on_logcat_clear(self):
        r = self._get_runner()
        result = r.logcat_clear()
        self._status("Logcat cleared" if result.ok else "Clear failed",
                     "ok" if result.ok else "error")

    # ── NEW: File Browser ─────────────────────────────────────────────────────
    def on_fb_ls(self):
        path = self.fb_path_var.get().strip() or "/"
        self._status(f"Listing {path}…", "busy")
        self._thread(self._fb_ls, path)

    def _fb_ls(self, path: str):
        r = self._get_runner()
        result = r.ls(path)
        self._log(result.command)
        self._header(f"LS  {path}", result.command)
        for line in result.stdout.splitlines():
            # colour directories differently
            tag = "key" if line.startswith("d") else \
                  "warn" if line.startswith("l") else "val"
            self._writeln(f"  {line}", tag)
        if result.stderr:
            self._writeln(f"  {result.stderr}", "error")
        self._status("Done", "ok")
        self._switch_tab(0)

    def on_fb_cat(self):
        path = self.fb_path_var.get().strip()
        if not path:
            messagebox.showwarning("Input Required", "Enter a file path.")
            return
        self._status(f"Reading {path}…", "busy")
        self._thread(self._fb_cat, path)

    def _fb_cat(self, path: str):
        r = self._get_runner()
        result = r.cat_file(path)
        self._log(result.command)
        self._header(f"CAT  {path}", result.command)
        self._writeln(result.stdout or result.stderr or "(empty)",
                      "val" if result.ok else "error")
        self._status("Done", "ok")
        self._switch_tab(0)

    def on_fb_pull(self):
        remote = self.fb_path_var.get().strip()
        if not remote:
            messagebox.showwarning("Input Required", "Enter a remote path.")
            return
        local = filedialog.asksaveasfilename(
            initialfile=os.path.basename(remote),
            title="Save Pulled File",
        )
        if not local:
            return
        self._status(f"Pulling {remote}…", "busy")
        self._thread(self._fb_pull, remote, local)

    def _fb_pull(self, remote: str, local: str):
        r = self._get_runner()
        result = r.pull_file(remote, local)
        self._log(result.command)
        self._header(f"PULL  {remote}", result.command)
        if result.ok:
            self._writeln(f"  ✔ Saved → {local}", "success")
            self._status("File pulled", "ok")
        else:
            self._writeln(f"  ✘ {result.stderr}", "error")
            self._status("Pull failed", "error")
        self._switch_tab(0)

    # ── NEW: SQLite Inspector ─────────────────────────────────────────────────
    def on_sqlite_tables(self):
        db = self.sqlite_db_var.get().strip()
        if not db:
            messagebox.showwarning("Input Required", "Enter a database path.")
            return
        self._status("Listing tables…", "busy")
        self._thread(self._sqlite_tables, db)

    def _sqlite_tables(self, db: str):
        r = self._get_runner()
        result = r.sqlite_tables(db)
        self._log(result.command)
        self._header(f"SQLITE TABLES  —  {db}", result.command)
        if result.ok and result.stdout:
            tables = result.stdout.split()
            for t in tables:
                self._writeln(f"  ► {t}", "key")
            self._writeln(f"\n  {len(tables)} tables", "success")
        else:
            self._writeln(f"  {result.stderr or '(no tables or access denied)'}", "error")
        self._status("Done", "ok")
        self._switch_tab(0)

    def on_sqlite_query(self):
        db    = self.sqlite_db_var.get().strip()
        query = self.sqlite_query_var.get().strip()
        if not db or not query:
            messagebox.showwarning("Input Required", "DB path and query required.")
            return
        self._status("Running SQLite query…", "busy")
        self._thread(self._sqlite_query, db, query)

    def _sqlite_query(self, db: str, query: str):
        r = self._get_runner()
        result = r.sqlite_query(db, query)
        self._log(result.command)
        self._header(f"SQLITE QUERY", result.command)
        if result.ok and result.stdout:
            lines = result.stdout.splitlines()
            if lines:
                self._writeln(f"  {lines[0]}", "key")   # header row (CSV)
                self._writeln("  " + "─" * 60, "dim")
                for line in lines[1:]:
                    self._writeln(f"  {line}", "val")
                self._writeln(f"\n  ► {len(lines)-1} rows", "success")
        else:
            self._writeln(f"  {result.stderr or '(empty result)'}", "error")
        self._status("Query done", "ok")
        self._switch_tab(0)

    def on_sqlite_schema(self):
        db = self.sqlite_db_var.get().strip()
        if not db:
            messagebox.showwarning("Input Required", "Enter a database path.")
            return
        self._status("Fetching schema…", "busy")
        self._thread(self._sqlite_schema, db)

    def _sqlite_schema(self, db: str):
        r = self._get_runner()
        result = r.sqlite_schema(db)
        self._log(result.command)
        self._header(f"SQLITE SCHEMA  —  {db}", result.command)
        self._writeln(result.stdout or result.stderr or "(empty)", "val")
        self._status("Done", "ok")
        self._switch_tab(0)

    # ── Export Results ────────────────────────────────────────────────────────
    def on_export_json(self):
        """Export last query table rows as JSON."""
        rows = self.view.output_panel._tree_data
        if not rows:
            messagebox.showwarning("No Data", "Run a QUERY first to populate Table View.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON", "*.json")],
            title="Export as JSON",
        )
        if not path:
            return
        data = [row.data for row in rows]
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        self._status(f"Exported {len(data)} rows → {os.path.basename(path)}", "ok")
        messagebox.showinfo("Exported", f"Saved {len(data)} rows to:\n{path}")

    def on_export_csv(self):
        """Export last query table rows as CSV."""
        rows = self.view.output_panel._tree_data
        if not rows:
            messagebox.showwarning("No Data", "Run a QUERY first to populate Table View.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")],
            title="Export as CSV",
        )
        if not path:
            return
        from utils.parsers import extract_columns
        cols = extract_columns(rows)
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=cols)
            writer.writeheader()
            for row in rows:
                writer.writerow(row.data)
        self._status(f"Exported {len(rows)} rows → {os.path.basename(path)}", "ok")
        messagebox.showinfo("Exported", f"Saved {len(rows)} rows to:\n{path}")

    # ── Query ─────────────────────────────────────────────────────────────────
    def on_query(self):
        uri = self.uri_var.get().strip()
        if not uri or uri == "content://":
            messagebox.showwarning("Input Required", "Enter a content URI.")
            return
        self._status(f"Querying {uri}…", "busy")
        self._add_uri_history(uri)
        self._thread(self._query, uri)

    def _query(self, uri: str):
        r = self._get_runner()
        result = r.content_query(
            uri,
            projection=self.projection_var.get(),
            where=self.selection_var.get(),
            sel_args=self.sel_args_var.get(),
            sort=self.sort_order_var.get(),
        )
        self._log(result.command)
        self._header(f"QUERY  {uri}", result.command)
        if not result.ok and not result.stdout:
            self._writeln(f"  Error: {result.stderr}", "error")
            self._status("Query failed", "error")
            return
        rows = parse_content_rows(result.stdout)
        if rows:
            for row in rows:
                self._writeln(f"  Row {row.index:>4} │", "row_num")
                for k, v in row.data.items():
                    self._writeln(f"         {k:<24} = ", "key")
                    self._writeln(f" {v}", "val")
                self._writeln()
            self._writeln(f"  ► {len(rows)} rows returned", "success")
            self.root.after(0, lambda: self.view.output_panel.populate_table(rows))
            self.root.after(0, lambda: self.view.output_panel.row_count_lbl.configure(
                text=f"{len(rows)} rows"))
        elif result.stdout:
            for line in result.stdout.splitlines():
                self._writeln(f"  {line}")
        else:
            self._writeln("  (no rows returned)", "warn")
        if result.stderr:
            self._writeln(f"\n  stderr: {result.stderr}", "warn")
        self._status(f"{len(rows) if rows else 0} rows returned", "ok")
        self._switch_tab(0)

    def on_read(self):
        uri = self.uri_var.get().strip()
        if not uri:
            messagebox.showwarning("Input Required", "Enter a content URI.")
            return
        self._add_uri_history(uri)
        self._status(f"Reading {uri}…", "busy")
        self._thread(self._read, uri)

    def _read(self, uri: str):
        r = self._get_runner()
        result = r.content_read(uri)
        self._log(result.command)
        self._header(f"READ  {uri}", result.command)
        self._writeln(result.stdout or result.stderr or "(empty response)",
                      "success" if result.ok else "error")
        self._status("Read complete", "ok" if result.ok else "error")
        self._switch_tab(0)

    # ── Write ─────────────────────────────────────────────────────────────────
    def on_insert(self):
        uri = self.uri_var.get().strip()
        col = self.col_var.get().strip()
        val = self.val_var.get().strip()
        if not uri or not col:
            messagebox.showwarning("Input Required", "URI and Column required.")
            return
        self._thread(self._write_op, "INSERT", uri, col, val)

    def on_update(self):
        uri = self.uri_var.get().strip()
        col = self.col_var.get().strip()
        if not uri or not col:
            messagebox.showwarning("Input Required", "URI and Column required.")
            return
        self._thread(self._write_op, "UPDATE", uri, col, self.val_var.get().strip())

    def on_delete(self):
        uri   = self.uri_var.get().strip()
        where = self.where_var.get().strip()
        if not uri:
            messagebox.showwarning("Input Required", "URI required.")
            return
        msg = f"DELETE from:\n{uri}"
        if not where:
            msg += "\n\n⚠ No WHERE clause — ALL rows will be deleted!"
        if not messagebox.askyesno("Confirm DELETE", msg, icon="warning"):
            return
        self._thread(self._write_op, "DELETE", uri, "", "")

    def _write_op(self, op: str, uri: str, col: str, val: str):
        r = self._get_runner()
        vtype = self.val_type_var.get() or "s"
        where = self.where_var.get().strip()
        if op == "INSERT":
            result = r.content_insert(uri, col, val, vtype)
        elif op == "UPDATE":
            result = r.content_update(uri, col, val, vtype, where)
        else:
            result = r.content_delete(uri, where)
        self._log(result.command)
        self._header(f"{op}  →  {uri}", result.command)
        if result.stdout:
            self._writeln(f"  {result.stdout}", "success" if result.ok else "warn")
        if result.stderr:
            self._writeln(f"  {result.stderr}", "warn")
        self._writeln(f"\n  {'✔ Success' if result.ok else '✘ Failed'}",
                      "success" if result.ok else "error")
        self._status(f"{op} {'succeeded' if result.ok else 'failed'}",
                     "ok" if result.ok else "error")
        self._switch_tab(0)

    # ── Call ──────────────────────────────────────────────────────────────────
    def on_call_method(self):
        uri    = self.uri_var.get().strip()
        method = self.method_var.get().strip()
        if not uri or not method:
            messagebox.showwarning("Input Required", "URI and Method required.")
            return
        self._thread(self._call_method, uri, method)

    def _call_method(self, uri: str, method: str):
        r = self._get_runner()
        result = r.content_call(uri, method, self.extra_var.get())
        self._log(result.command)
        self._header(f"CALL  {method}  →  {uri}", result.command)
        self._writeln(result.stdout or result.stderr or "(empty)",
                      "success" if result.ok else "error")
        self._status(f"Call {method} {'ok' if result.ok else 'failed'}",
                     "ok" if result.ok else "error")
        self._switch_tab(0)

    # ── Raw ───────────────────────────────────────────────────────────────────
    def on_exec_raw(self):
        cmd = self.raw_cmd_var.get().strip()
        if not cmd:
            return
        self._status("Executing…", "busy")
        self._thread(self._exec_raw, cmd)

    def _exec_raw(self, cmd: str):
        result = ADBRunner().run(cmd, timeout=30)
        self._log(result.command)
        self._header("RAW COMMAND", result.command)
        for line in (result.stdout or "").splitlines():
            self._writeln(f"  {line}")
        if result.stderr:
            self._writeln(f"  {result.stderr}", "warn")
        self._writeln(f"\n  {'✔ Done' if result.ok else f'✘ Exit {result.returncode}'}",
                      "success" if result.ok else "error")
        self._status("Done", "ok" if result.ok else "error")
        self._switch_tab(0)

    # ── URI History ───────────────────────────────────────────────────────────
    def on_uri_select(self, event):
        lb = self.view.sidebar.uri_list
        sel = lb.curselection()
        if sel:
            self.uri_var.set(lb.get(sel[0]))

    def on_clear_uri_history(self):
        self.view.sidebar.uri_list.delete(0, "end")
        