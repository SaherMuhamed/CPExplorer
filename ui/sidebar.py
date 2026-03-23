"""
ui/sidebar.py — Left control panel with all feature sections
"""

import tkinter as tk
from tkinter import ttk
from ui import theme as T
from ui.widgets import FlatButton, LabeledEntry, SectionHeader, Separator, ToolTip


class Sidebar(tk.Frame):
    def __init__(self, parent, controller, **kw):
        super().__init__(parent, bg=T.BG2, **kw)
        self.controller = controller
        self._build()

    def _build(self):
        canvas = tk.Canvas(self, bg=T.BG2, highlightthickness=0, bd=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scroll_frame = tk.Frame(canvas, bg=T.BG2)
        self.scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(
            int(-1 * (e.delta / 120)), "units"))

        f   = self.scroll_frame
        pad = {"padx": T.PAD, "pady": (3, 0)}

        tk.Frame(f, bg=T.BG2, height=10).pack()

        # ── ① Device & Package ────────────────────────────────────────────────
        SectionHeader(f, "① DEVICE & PACKAGE").pack(fill="x", **pad)
        tk.Frame(f, bg=T.BG2, height=6).pack()

        dev_frame = tk.Frame(f, bg=T.BG2)
        dev_frame.pack(fill="x", **pad)
        tk.Label(dev_frame, text="Device", font=T.FONT_LABEL, fg=T.TEXT_DIM,
                 bg=T.BG2, width=10, anchor="w").pack(side="left")
        self.device_combo = ttk.Combobox(
            dev_frame, textvariable=self.controller.device_var,
            state="readonly", font=T.FONT_MONO)
        self.device_combo.pack(side="left", fill="x", expand=True, ipady=3)
        refresh_btn = FlatButton(dev_frame, "⟳", self.controller.on_refresh_devices,
                                 color=T.BG4, padx=8)
        refresh_btn.pack(side="left", padx=(4, 0))
        ToolTip(refresh_btn, "Refresh device list")

        di_frame = tk.Frame(f, bg=T.BG2)
        di_frame.pack(fill="x", **pad)
        FlatButton(di_frame, "⚙ Android Ver", self.controller.on_get_android_version,
                   color=T.ACCENT).pack(side="left", padx=(0, 3))
        FlatButton(di_frame, "⚙ CPU Arch",   self.controller.on_get_architecture,
                   color=T.ACCENT2).pack(side="left", padx=(0, 3))
        FlatButton(di_frame, "⚙ Full Info",  self.controller.on_full_device_info,
                   color=T.PURPLE).pack(side="left", padx=(0, 3))
        FlatButton(di_frame, "⚙ Network",    self.controller.on_network_info,
                   color=T.BG4).pack(side="left")

        tk.Frame(f, bg=T.BG2, height=6).pack()
        pkg_row = LabeledEntry(f, "Package", self.controller.package_var, label_width=10)
        pkg_row.pack(fill="x", **pad)
        ToolTip(pkg_row.entry, "e.g. com.example.app")

        pkg_btn = tk.Frame(f, bg=T.BG2)
        pkg_btn.pack(fill="x", **pad)
        FlatButton(pkg_btn, "⬡ Enum Providers",  self.controller.on_enumerate_providers,
                   color=T.ACCENT2).pack(side="left", padx=(0, 3))
        FlatButton(pkg_btn, "⬡ List Pkgs",       self.controller.on_list_packages,
                   color=T.ACCENT).pack(side="left")

        pkg_btn2 = tk.Frame(f, bg=T.BG2)
        pkg_btn2.pack(fill="x", **pad)
        FlatButton(pkg_btn2, "🔍 Perm Audit",     self.controller.on_permission_audit,
                   color=T.WARN).pack(side="left", padx=(0, 3))
        FlatButton(pkg_btn2, "🔍 Component Scan", self.controller.on_component_scan,
                   color=T.DANGER).pack(side="left", padx=(0, 3))
        FlatButton(pkg_btn2, "📁 App Data",       self.controller.on_app_data_paths,
                   color=T.PURPLE).pack(side="left")

        tk.Frame(f, bg=T.BG2, height=6).pack()
        uri_row = LabeledEntry(f, "URI", self.controller.uri_var, label_width=10)
        uri_row.pack(fill="x", **pad)
        ToolTip(uri_row.entry, "content://authority/path")

        hist_lbl = tk.Frame(f, bg=T.BG2)
        hist_lbl.pack(fill="x", **pad)
        tk.Label(hist_lbl, text="URI History", font=T.FONT_UI_SM,
                 fg=T.TEXT_DIM, bg=T.BG2).pack(side="left")
        FlatButton(hist_lbl, "✕ Clear", self.controller.on_clear_uri_history,
                   color=T.BG4, padx=6, pady=2).pack(side="right")

        hist_wrap = tk.Frame(f, bg=T.BG2, highlightthickness=1,
                             highlightbackground=T.BORDER)
        hist_wrap.pack(fill="x", padx=T.PAD, pady=(2, 0))
        self.uri_list = tk.Listbox(
            hist_wrap, bg=T.BG3, fg=T.ACCENT,
            selectbackground=T.BG4, selectforeground=T.TEXT_BRIGHT,
            relief="flat", height=4, font=T.FONT_MONO_SM,
            bd=0, activestyle="none", highlightthickness=0,
        )
        self.uri_list.pack(fill="x")
        self.uri_list.bind("<<ListboxSelect>>", self.controller.on_uri_select)

        Separator(f).pack(fill="x", padx=T.PAD, pady=10)

        # ── ② Query ───────────────────────────────────────────────────────────
        SectionHeader(f, "② QUERY").pack(fill="x", **pad)
        tk.Frame(f, bg=T.BG2, height=6).pack()
        for lbl, var, hint in [
            ("Projection", self.controller.projection_var,  "col1,col2  or  *"),
            ("Selection",  self.controller.selection_var,   "col=?  AND  col2>0"),
            ("Sel Args",   self.controller.sel_args_var,    "val1 val2"),
            ("Sort Order", self.controller.sort_order_var,  "col ASC / DESC"),
        ]:
            row = LabeledEntry(f, lbl, var, label_width=10)
            row.pack(fill="x", **pad)
            ToolTip(row.entry, hint)
        tk.Frame(f, bg=T.BG2, height=6).pack()
        q_btn = tk.Frame(f, bg=T.BG2)
        q_btn.pack(fill="x", **pad)
        FlatButton(q_btn, "▶  QUERY",      self.controller.on_query,
                   color=T.ACCENT).pack(side="left", padx=(0, 3))
        FlatButton(q_btn, "⚡ READ",        self.controller.on_read,
                   color=T.ACCENT2).pack(side="left", padx=(0, 3))
        FlatButton(q_btn, "⬇ JSON",        self.controller.on_export_json,
                   color=T.BG4).pack(side="left", padx=(0, 3))
        FlatButton(q_btn, "⬇ CSV",         self.controller.on_export_csv,
                   color=T.BG4).pack(side="left")

        Separator(f).pack(fill="x", padx=T.PAD, pady=10)

        # ── ③ Write Ops ───────────────────────────────────────────────────────
        SectionHeader(f, "③ WRITE OPS").pack(fill="x", **pad)
        tk.Frame(f, bg=T.BG2, height=6).pack()
        for lbl, var, hint in [
            ("Column",   self.controller.col_var,      "column_name"),
            ("Value",    self.controller.val_var,       "new_value"),
            ("Val Type", self.controller.val_type_var,  "s=str  i=int  b=bool  f=float"),
            ("WHERE",    self.controller.where_var,     "_id=1"),
        ]:
            row = LabeledEntry(f, lbl, var, label_width=10)
            row.pack(fill="x", **pad)
            ToolTip(row.entry, hint)
        tk.Frame(f, bg=T.BG2, height=6).pack()
        w_btn = tk.Frame(f, bg=T.BG2)
        w_btn.pack(fill="x", **pad)
        FlatButton(w_btn, "+ INSERT", self.controller.on_insert,
                   color=T.ACCENT2).pack(side="left", padx=(0, 3))
        FlatButton(w_btn, "✎ UPDATE", self.controller.on_update,
                   color=T.WARN).pack(side="left", padx=(0, 3))
        FlatButton(w_btn, "✕ DELETE", self.controller.on_delete,
                   color=T.DANGER).pack(side="left")

        Separator(f).pack(fill="x", padx=T.PAD, pady=10)

        # ── ④ Call Method ─────────────────────────────────────────────────────
        SectionHeader(f, "④ CALL METHOD").pack(fill="x", **pad)
        tk.Frame(f, bg=T.BG2, height=6).pack()
        LabeledEntry(f, "Method", self.controller.method_var,
                     label_width=10).pack(fill="x", **pad)
        LabeledEntry(f, "Extras", self.controller.extra_var,
                     label_width=10).pack(fill="x", **pad)
        tk.Frame(f, bg=T.BG2, height=6).pack()
        FlatButton(f, "⚙  CALL METHOD", self.controller.on_call_method,
                   color=T.ACCENT).pack(anchor="w", padx=T.PAD)

        Separator(f).pack(fill="x", padx=T.PAD, pady=10)

        # ── ⑤ Intent Broadcaster ──────────────────────────────────────────────
        SectionHeader(f, "⑤ INTENT BROADCASTER").pack(fill="x", **pad)
        tk.Frame(f, bg=T.BG2, height=6).pack()
        for lbl, var, hint in [
            ("Action",    self.controller.intent_action_var, "android.intent.action.VIEW"),
            ("Component", self.controller.intent_comp_var,   "pkg/.ActivityName"),
            ("Data URI",  self.controller.intent_uri_var,    "https://example.com"),
            ("Extras",    self.controller.intent_extras_var, "--es key value"),
        ]:
            row = LabeledEntry(f, lbl, var, label_width=10)
            row.pack(fill="x", **pad)
            ToolTip(row.entry, hint)
        tk.Frame(f, bg=T.BG2, height=6).pack()
        i_btn = tk.Frame(f, bg=T.BG2)
        i_btn.pack(fill="x", **pad)
        FlatButton(i_btn, "📡 Broadcast",   self.controller.on_send_broadcast,
                   color=T.ACCENT).pack(side="left", padx=(0, 3))
        FlatButton(i_btn, "▶ Start Activity", self.controller.on_start_activity,
                   color=T.ACCENT2).pack(side="left")

        Separator(f).pack(fill="x", padx=T.PAD, pady=10)

        # ── ⑥ Logcat ──────────────────────────────────────────────────────────
        SectionHeader(f, "⑥ LOGCAT").pack(fill="x", **pad)
        tk.Frame(f, bg=T.BG2, height=6).pack()
        LabeledEntry(f, "Tag Filter", self.controller.logcat_filter_var,
                     label_width=10).pack(fill="x", **pad)
        ToolTip(f.winfo_children()[-1], "e.g. ActivityManager — leave blank for all")
        tk.Frame(f, bg=T.BG2, height=6).pack()
        l_btn = tk.Frame(f, bg=T.BG2)
        l_btn.pack(fill="x", **pad)
        FlatButton(l_btn, "📋 Dump Logcat", self.controller.on_logcat_dump,
                   color=T.ACCENT).pack(side="left", padx=(0, 3))
        FlatButton(l_btn, "✕ Clear",        self.controller.on_logcat_clear,
                   color=T.DANGER).pack(side="left")

        Separator(f).pack(fill="x", padx=T.PAD, pady=10)

        # ── ⑦ File Browser ────────────────────────────────────────────────────
        SectionHeader(f, "⑦ FILE BROWSER").pack(fill="x", **pad)
        tk.Frame(f, bg=T.BG2, height=6).pack()
        LabeledEntry(f, "Path", self.controller.fb_path_var,
                     label_width=10).pack(fill="x", **pad)
        ToolTip(f.winfo_children()[-1], "Remote device path e.g. /data/data/com.app/")
        tk.Frame(f, bg=T.BG2, height=6).pack()
        fb_btn = tk.Frame(f, bg=T.BG2)
        fb_btn.pack(fill="x", **pad)
        FlatButton(fb_btn, "📁 LS",    self.controller.on_fb_ls,
                   color=T.ACCENT).pack(side="left", padx=(0, 3))
        FlatButton(fb_btn, "📄 CAT",   self.controller.on_fb_cat,
                   color=T.ACCENT2).pack(side="left", padx=(0, 3))
        FlatButton(fb_btn, "⬇ PULL",  self.controller.on_fb_pull,
                   color=T.WARN).pack(side="left")

        Separator(f).pack(fill="x", padx=T.PAD, pady=10)

        # ── ⑧ SQLite Inspector ────────────────────────────────────────────────
        SectionHeader(f, "⑧ SQLITE INSPECTOR").pack(fill="x", **pad)
        tk.Frame(f, bg=T.BG2, height=6).pack()
        LabeledEntry(f, "DB Path", self.controller.sqlite_db_var,
                     label_width=10).pack(fill="x", **pad)
        ToolTip(f.winfo_children()[-1],
                "/data/data/com.app/databases/main.db")
        LabeledEntry(f, "Query",   self.controller.sqlite_query_var,
                     label_width=10).pack(fill="x", **pad)
        tk.Frame(f, bg=T.BG2, height=6).pack()
        sq_btn = tk.Frame(f, bg=T.BG2)
        sq_btn.pack(fill="x", **pad)
        FlatButton(sq_btn, "📋 Tables",  self.controller.on_sqlite_tables,
                   color=T.ACCENT).pack(side="left", padx=(0, 3))
        FlatButton(sq_btn, "▶ Query",    self.controller.on_sqlite_query,
                   color=T.ACCENT2).pack(side="left", padx=(0, 3))
        FlatButton(sq_btn, "🗂 Schema",  self.controller.on_sqlite_schema,
                   color=T.PURPLE).pack(side="left")

        Separator(f).pack(fill="x", padx=T.PAD, pady=10)

        # ── ⑨ Raw ADB ────────────────────────────────────────────────────────
        SectionHeader(f, "⑨ RAW ADB COMMAND").pack(fill="x", **pad)
        tk.Frame(f, bg=T.BG2, height=6).pack()
        raw_wrap = tk.Frame(f, bg=T.BG2, highlightthickness=1,
                            highlightbackground=T.BORDER)
        raw_wrap.pack(fill="x", padx=T.PAD, pady=(0, 4))
        tk.Entry(
            raw_wrap, textvariable=self.controller.raw_cmd_var,
            bg=T.BG3, fg=T.TEXT_DIM, insertbackground=T.ACCENT,
            relief="flat", font=T.FONT_MONO, bd=0,
        ).pack(fill="x", ipady=5, padx=4, pady=4)

        misc_btn = tk.Frame(f, bg=T.BG2)
        misc_btn.pack(fill="x", **pad)
        FlatButton(misc_btn, "⚡ Execute Raw",  self.controller.on_exec_raw,
                   color=T.WARN).pack(side="left", padx=(0, 3))
        FlatButton(misc_btn, "📸 Screenshot",   self.controller.on_screenshot,
                   color=T.ACCENT2).pack(side="left")

        tk.Frame(f, bg=T.BG2, height=20).pack()
        