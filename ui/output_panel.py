"""
ui/output_panel.py — Right panel: Output, Table View, Device Info, Command Log tabs
"""

import tkinter as tk
from tkinter import ttk, filedialog
from ui import theme as T
from ui.widgets import FlatButton, TerminalOutput, ToolTip


class OutputPanel(tk.Frame):
    """
    Right-side tabbed panel:
      Tab 0 — Terminal Output
      Tab 1 — Table View (Treeview)
      Tab 2 — Device Info
      Tab 3 — Command Log
    """

    def __init__(self, parent, controller, **kw):
        super().__init__(parent, bg=T.BG, **kw)
        self.controller = controller
        self._tree_data = []
        self._build()

    def _build(self):
        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True)

        self._build_output_tab()
        self._build_table_tab()
        self._build_device_tab()
        self._build_log_tab()

    # ── Tab 0: Terminal Output ────────────────────────────────────────────────
    def _build_output_tab(self):
        frame = tk.Frame(self.nb, bg=T.BG)
        self.nb.add(frame, text="  Output  ")

        # Toolbar
        tb = tk.Frame(frame, bg=T.BG2, pady=5)
        tb.pack(fill="x")
        FlatButton(tb, "📝 Copy",  self.copy_output,  color=T.ACCENT,  pady=3, padx=9).pack(side="left", padx=(8, 3))
        FlatButton(tb, "📥 Save",  self.save_output,  color=T.ACCENT2, pady=3, padx=9).pack(side="left", padx=3)
        FlatButton(tb, "❌ Clear", self.clear_output, color=T.DANGER,  pady=3, padx=9).pack(side="left", padx=3)
        self.row_count_lbl = tk.Label(tb, text="", font=T.FONT_UI_SM,
                                      fg=T.TEXT_DIM, bg=T.BG2)
        self.row_count_lbl.pack(side="right", padx=12)

        # Terminal
        self.terminal = TerminalOutput(frame)
        self.terminal.pack(fill="both", expand=True, padx=1, pady=(0, 1))

    # ── Tab 1: Table View ─────────────────────────────────────────────────────
    def _build_table_tab(self):
        frame = tk.Frame(self.nb, bg=T.BG)
        self.nb.add(frame, text="  Table View  ")

        # Filter bar
        tb = tk.Frame(frame, bg=T.BG2, pady=5)
        tb.pack(fill="x")
        tk.Label(tb, text="Filter:", font=T.FONT_LABEL, fg=T.TEXT_DIM,
                 bg=T.BG2).pack(side="left", padx=(10, 4))
        self.filter_var = tk.StringVar()
        self.filter_var.trace_add("write", self._filter_table)
        filter_wrap = tk.Frame(tb, bg=T.BG2, highlightthickness=1,
                               highlightbackground=T.BORDER)
        filter_wrap.pack(side="left")
        tk.Entry(filter_wrap, textvariable=self.filter_var, bg=T.BG3, fg=T.TEXT,
                 insertbackground=T.ACCENT, relief="flat", font=T.FONT_MONO,
                 bd=0, width=28).pack(ipady=4, padx=4, pady=2)
        FlatButton(tb, "✕", lambda: self.filter_var.set(""),
                   color=T.BG4, padx=7, pady=3).pack(side="left", padx=4)
        self.tbl_count_lbl = tk.Label(tb, text="", font=T.FONT_UI_SM,
                                      fg=T.TEXT_DIM, bg=T.BG2)
        self.tbl_count_lbl.pack(side="right", padx=12)

        # Treeview
        tree_wrap = tk.Frame(frame, bg=T.BG)
        tree_wrap.pack(fill="both", expand=True, padx=4, pady=(0, 4))
        self.tree = ttk.Treeview(tree_wrap, show="headings", selectmode="browse")
        vsb = ttk.Scrollbar(tree_wrap, orient="vertical",   command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_wrap, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side="right",  fill="y")
        hsb.pack(side="bottom", fill="x")
        self.tree.pack(fill="both", expand=True)

        # Row highlight on hover
        self.tree.tag_configure("odd",  background=T.BG3)
        self.tree.tag_configure("even", background=T.BG2)

    # ── Tab 2: Device Info ────────────────────────────────────────────────────
    def _build_device_tab(self):
        frame = tk.Frame(self.nb, bg=T.BG)
        self.nb.add(frame, text="  Device Info  ")

        tb = tk.Frame(frame, bg=T.BG2, pady=5)
        tb.pack(fill="x")
        FlatButton(tb, "⟳ Refresh Device Info",
                   self.controller.on_full_device_info,
                   color=T.ACCENT, pady=3).pack(side="left", padx=8)
        FlatButton(tb, "⎘ Copy",
                   self.copy_device_info,
                   color=T.ACCENT2, pady=3).pack(side="left", padx=4)

        # Info grid
        self.device_grid = tk.Frame(frame, bg=T.BG)
        self.device_grid.pack(fill="both", expand=True, padx=16, pady=12)

        # Placeholder labels — populated by populate_device_info()
        self._device_rows: list[tuple[tk.Label, tk.Label]] = []

    # ── Tab 3: Command Log ────────────────────────────────────────────────────
    def _build_log_tab(self):
        from tkinter import scrolledtext
        frame = tk.Frame(self.nb, bg=T.BG)
        self.nb.add(frame, text="  Command Log  ")

        tb = tk.Frame(frame, bg=T.BG2, pady=5)
        tb.pack(fill="x")
        FlatButton(tb, "✕ Clear Log", self.clear_log,
                   color=T.DANGER, pady=3).pack(side="left", padx=8)
        FlatButton(tb, "⬇ Save Log", self.save_log,
                   color=T.ACCENT2, pady=3).pack(side="left", padx=4)

        self.cmd_log = scrolledtext.ScrolledText(
            frame, bg=T.BG2, fg=T.TEXT_DIM,
            font=T.FONT_MONO_SM, relief="flat", bd=0, wrap="word",
            selectbackground=T.BG4,
        )
        self.cmd_log.pack(fill="both", expand=True, padx=1, pady=(0, 1))
        self.cmd_log.configure(state="disabled")

    # ── Public API ────────────────────────────────────────────────────────────
    def switch_to(self, tab: int):
        self.nb.select(tab)

    # Terminal helpers
    def write(self, text: str, tag: str = ""):
        self.terminal.write(text, tag)

    def writeln(self, text: str = "", tag: str = ""):
        self.terminal.writeln(text, tag)

    def header(self, title: str, cmd: str = ""):
        from datetime import datetime
        bar = "─" * max(0, 60 - len(title))
        self.writeln(f"\n┌─ {title} {bar}", "header")
        if cmd:
            self.writeln(f"│  ▸ {cmd}", "cmd")
        self.writeln(f"│  ⏱ {datetime.now().strftime('%H:%M:%S')}", "ts")
        self.writeln("└" + "─" * 62, "header")
        self.writeln()

    def clear_output(self):
        self.terminal.clear()
        self.row_count_lbl.configure(text="")

    def copy_output(self):
        txt = self.terminal.get_all()
        self.terminal.text.clipboard_clear()
        self.terminal.text.clipboard_append(txt)

    def save_output(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text", "*.txt"), ("All", "*.*")],
            title="Save Output")
        if path:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(self.terminal.get_all())

    # Table helpers
    def populate_table(self, rows):
        """rows: list of ContentRow from parsers.py"""
        from utils.parsers import extract_columns
        self._tree_data = rows
        cols = extract_columns(rows)
        if not cols:
            return
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = cols
        for col in cols:
            self.tree.heading(col, text=col,
                              command=lambda c=col: self._sort_column(c, False))
            self.tree.column(col, width=130, minwidth=60, stretch=True)
        for i, row in enumerate(rows):
            vals = [row.data.get(c, "") for c in cols]
            tag = "odd" if i % 2 else "even"
            self.tree.insert("", "end", values=vals, tags=(tag,))
        self.tbl_count_lbl.configure(text=f"{len(rows)} rows")

    def _filter_table(self, *_):
        q = self.filter_var.get().lower()
        self.tree.delete(*self.tree.get_children())
        for i, row in enumerate(self._tree_data):
            if not q or any(q in str(v).lower() for v in row.data.values()):
                from utils.parsers import extract_columns
                cols = list(self.tree["columns"])
                vals = [row.data.get(c, "") for c in cols]
                tag = "odd" if i % 2 else "even"
                self.tree.insert("", "end", values=vals, tags=(tag,))

    def _sort_column(self, col: str, reverse: bool):
        data = [(self.tree.set(k, col), k) for k in self.tree.get_children("")]
        try:
            data.sort(key=lambda t: float(t[0]) if t[0] else 0, reverse=reverse)
        except ValueError:
            data.sort(reverse=reverse)
        for i, (_, iid) in enumerate(data):
            self.tree.move(iid, "", i)
        self.tree.heading(col, command=lambda: self._sort_column(col, not reverse))

    # Device info helpers
    def populate_device_info(self, info: dict):
        for w in self.device_grid.winfo_children():
            w.destroy()
        self._device_rows = []

        # Title
        tk.Label(self.device_grid, text="DEVICE FINGERPRINT",
                 font=(*T.FONT_UI[:1], 11, "bold"), fg=T.ACCENT,
                 bg=T.BG).grid(row=0, column=0, columnspan=2,
                               sticky="w", pady=(0, 10))

        for i, (key, val) in enumerate(info.items(), start=1):
            # Key
            kl = tk.Label(self.device_grid, text=key,
                          font=T.FONT_BTN, fg=T.TEXT_DIM, bg=T.BG,
                          width=16, anchor="w")
            kl.grid(row=i, column=0, sticky="w", pady=2, padx=(0, 12))

            # Value — colour-code based on content
            color = T.TEXT
            if "SDK" in key:
                color = T.ACCENT
            elif "ABI" in key or "CPU" in key:
                color = T.ACCENT2
            elif "Root" in key and val and val not in ["", "[error", "[]"]:
                color = T.DANGER
            elif "SELinux" in key:
                color = T.WARN if "Enforcing" in val else T.DANGER
            elif "Build Type" in key and "user" not in val:
                color = T.WARN

            vl = tk.Label(self.device_grid, text=val or "—",
                          font=T.FONT_MONO, fg=color, bg=T.BG,
                          anchor="w", justify="left")
            vl.grid(row=i, column=1, sticky="w", pady=2)
            self._device_rows.append((kl, vl))

        # Grid weight
        self.device_grid.columnconfigure(1, weight=1)
        self.switch_to(2)

    def copy_device_info(self):
        lines = []
        for kl, vl in self._device_rows:
            lines.append(f"{kl['text']:<20} {vl['text']}")
        self.device_grid.clipboard_clear()
        self.device_grid.clipboard_append("\n".join(lines))

    # Log helpers
    def log_command(self, cmd: str):
        from datetime import datetime
        self.cmd_log.configure(state="normal")
        self.cmd_log.insert("end",
            f"[{datetime.now().strftime('%H:%M:%S')}]  {cmd}\n")
        self.cmd_log.see("end")
        self.cmd_log.configure(state="disabled")

    def clear_log(self):
        self.cmd_log.configure(state="normal")
        self.cmd_log.delete("1.0", "end")
        self.cmd_log.configure(state="disabled")

    def save_log(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text", "*.txt"), ("All", "*.*")],
            title="Save Command Log")
        if path:
            with open(path, "w", encoding="utf-8") as fh:
                self.cmd_log.configure(state="normal")
                fh.write(self.cmd_log.get("1.0", "end"))
                self.cmd_log.configure(state="disabled")
