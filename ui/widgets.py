"""
ui/widgets.py — Reusable custom Tkinter widgets
"""

import tkinter as tk
from tkinter import ttk
from ui import theme as T


class FlatButton(tk.Button):
    """Pill-style flat button with hover effect."""

    def __init__(self, parent, text, command, color=None, width=None, **kw):
        color = color or T.ACCENT
        cfg = dict(
            text=text,
            command=command,
            font=T.FONT_BTN,
            fg=T.BG,
            bg=color,
            activebackground=color,
            activeforeground=T.BG,
            relief="flat",
            bd=0,
            padx=T.BTN_PADX,
            pady=T.BTN_PADY,
            cursor="hand2",
        )
        if width:
            cfg["width"] = width
        cfg.update(kw)
        super().__init__(parent, **cfg)
        self._color = color
        self._darken = self._make_darker(color)
        self.bind("<Enter>", lambda e: self.configure(bg=self._darken))
        self.bind("<Leave>", lambda e: self.configure(bg=self._color))

    @staticmethod
    def _make_darker(hex_color: str) -> str:
        hex_color = hex_color.lstrip("#")
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        r, g, b = max(0, r - 25), max(0, g - 25), max(0, b - 25)
        return f"#{r:02x}{g:02x}{b:02x}"


class IconButton(FlatButton):
    """Compact icon-only button."""
    def __init__(self, parent, icon, command, color=None, tooltip_text="", **kw):
        super().__init__(parent, icon, command, color=color or T.BG4,
                         padx=7, pady=4, **kw)
        if tooltip_text:
            ToolTip(self, tooltip_text)


class LabeledEntry(tk.Frame):
    """Label + Entry in a single row frame."""

    def __init__(self, parent, label, variable, hint="", label_width=10, **kw):
        super().__init__(parent, bg=T.BG2, **kw)
        tk.Label(self, text=label, font=T.FONT_LABEL, fg=T.TEXT_DIM,
                 bg=T.BG2, width=label_width, anchor="w").pack(side="left")
        self.entry = tk.Entry(
            self, textvariable=variable,
            bg=T.BG3, fg=T.TEXT, insertbackground=T.ACCENT,
            relief="flat", font=T.FONT_MONO, bd=0,
            highlightthickness=1, highlightbackground=T.BORDER,
            highlightcolor=T.ACCENT,
        )
        self.entry.pack(side="left", fill="x", expand=True, ipady=4, padx=(0, 2))

    def focus(self):
        self.entry.focus_set()


class SectionHeader(tk.Frame):
    """Stylised section divider with label and optional badge."""

    def __init__(self, parent, title, badge=None, **kw):
        super().__init__(parent, bg=T.BG2, **kw)
        # Left accent bar
        tk.Frame(self, bg=T.ACCENT, width=3).pack(side="left", fill="y", padx=(0, 8))
        tk.Label(self, text=title, font=T.FONT_SECTION, fg=T.ACCENT,
                 bg=T.BG2).pack(side="left")
        if badge:
            tk.Label(self, text=f" {badge} ", font=T.FONT_UI_SM,
                     fg=T.BG, bg=T.ACCENT, padx=4).pack(side="left", padx=6)


class Separator(tk.Frame):
    """Custom separator line."""
    def __init__(self, parent, color=None, pady=6, **kw):
        super().__init__(parent, bg=color or T.BORDER, height=1, **kw)


class TerminalOutput(tk.Frame):
    """Scrollable terminal-style output with colour tags."""

    def __init__(self, parent, **kw):
        super().__init__(parent, bg=T.BG2, **kw)
        self._build()

    def _build(self):
        from tkinter import scrolledtext
        self.text = scrolledtext.ScrolledText(
            self,
            bg=T.BG2, fg=T.TEXT,
            insertbackground=T.ACCENT,
            font=T.FONT_MONO_LG,
            relief="flat", bd=0,
            wrap="none",
            selectbackground=T.BG4,
            selectforeground=T.TEXT_BRIGHT,
            spacing1=1, spacing3=1,
        )
        self.text.pack(fill="both", expand=True)
        self.text.configure(state="disabled")

        # Colour tags
        tags = {
            "header":   {"foreground": T.TAG_HEADER,  "font": (*T.FONT_MONO_LG[:1], T.FONT_MONO_LG[1], "bold")},
            "success":  {"foreground": T.TAG_SUCCESS},
            "warn":     {"foreground": T.TAG_WARN},
            "error":    {"foreground": T.TAG_ERROR},
            "cmd":      {"foreground": T.TAG_CMD,     "font": T.FONT_MONO_SM},
            "ts":       {"foreground": T.TAG_TS,      "font": T.FONT_MONO_SM},
            "key":      {"foreground": T.TAG_KEY},
            "val":      {"foreground": T.TAG_VAL},
            "row_num":  {"foreground": T.TAG_ROW_NUM},
            "dim":      {"foreground": T.TEXT_DIM},
            "bright":   {"foreground": T.TEXT_BRIGHT},
        }
        for name, opts in tags.items():
            self.text.tag_config(name, **opts)

    def write(self, text: str, tag: str = ""):
        self.text.configure(state="normal")
        self.text.insert("end", text, tag)
        self.text.see("end")
        self.text.configure(state="disabled")

    def writeln(self, text: str = "", tag: str = ""):
        self.write(text + "\n", tag)

    def clear(self):
        self.text.configure(state="normal")
        self.text.delete("1.0", "end")
        self.text.configure(state="disabled")

    def get_all(self) -> str:
        return self.text.get("1.0", "end")


class StatusBar(tk.Frame):
    """Bottom status bar with message + command preview."""

    def __init__(self, parent, **kw):
        super().__init__(parent, bg=T.BG3, pady=4, **kw)
        self._dot_color = T.TEXT_DIM
        self.dot = tk.Label(self, text="●", font=T.FONT_UI_SM,
                            fg=self._dot_color, bg=T.BG3)
        self.dot.pack(side="left", padx=(10, 4))
        self.msg_var = tk.StringVar(value="Ready")
        tk.Label(self, textvariable=self.msg_var, font=T.FONT_UI_SM,
                 fg=T.TEXT_DIM, bg=T.BG3, anchor="w").pack(side="left")
        self.cmd_var = tk.StringVar(value="")
        tk.Label(self, textvariable=self.cmd_var, font=T.FONT_MONO_SM,
                 fg=T.ACCENT_DIM, bg=T.BG3, anchor="e").pack(side="right", padx=10)

    def set(self, msg: str, state: str = "idle"):
        self.msg_var.set(msg)
        colors = {"idle": T.TEXT_DIM, "busy": T.WARN,
                  "ok": T.ACCENT2, "error": T.DANGER}
        self.dot.configure(fg=colors.get(state, T.TEXT_DIM))

    def set_cmd(self, cmd: str):
        short = cmd[-90:] if len(cmd) > 90 else cmd
        self.cmd_var.set(short)


class DeviceInfoCard(tk.Frame):
    """Inline device badge showing SDK + ABI."""

    def __init__(self, parent, **kw):
        super().__init__(parent, bg=T.BG3, padx=10, pady=4, **kw)
        self.sdk_var = tk.StringVar(value="SDK: —")
        self.abi_var = tk.StringVar(value="ABI: —")
        self.ver_var = tk.StringVar(value="Android: —")

        lkw = dict(font=T.FONT_UI_SM, bg=T.BG3, padx=6)
        tk.Label(self, textvariable=self.sdk_var, fg=T.ACCENT,  **lkw).pack(side="left")
        tk.Label(self, text="│",                  fg=T.BORDER2, bg=T.BG3).pack(side="left")
        tk.Label(self, textvariable=self.abi_var, fg=T.ACCENT2, **lkw).pack(side="left")
        tk.Label(self, text="│",                  fg=T.BORDER2, bg=T.BG3).pack(side="left")
        tk.Label(self, textvariable=self.ver_var, fg=T.WARN,    **lkw).pack(side="left")

    def update(self, sdk: str = "", abi: str = "", android_ver: str = ""):
        if sdk:         self.sdk_var.set(f"SDK {sdk}")
        if abi:         self.abi_var.set(abi)
        if android_ver: self.ver_var.set(f"Android {android_ver}")


class ToolTip:
    """Simple tooltip on hover."""

    def __init__(self, widget, text: str):
        self._widget = widget
        self._text = text
        self._tip = None
        widget.bind("<Enter>", self._show)
        widget.bind("<Leave>", self._hide)

    def _show(self, event=None):
        x = self._widget.winfo_rootx() + 20
        y = self._widget.winfo_rooty() + self._widget.winfo_height() + 4
        self._tip = tk.Toplevel(self._widget)
        self._tip.wm_overrideredirect(True)
        self._tip.wm_geometry(f"+{x}+{y}")
        tk.Label(self._tip, text=self._text, font=T.FONT_UI_SM,
                 fg=T.TEXT, bg=T.BG4, relief="flat",
                 padx=8, pady=4).pack()

    def _hide(self, event=None):
        if self._tip:
            self._tip.destroy()
            self._tip = None
