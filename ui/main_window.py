"""
ui/main_window.py — Top-level window; wires sidebar + output panel + status bar.

MainWindow now wraps an existing tk.Tk() root (passed in from main.py) rather
than subclassing it.  This ensures tk.StringVar objects in AppController are
always created after the root window exists.
"""

import tkinter as tk
from tkinter import ttk
from ui import theme as T, styles
from ui.sidebar import Sidebar
from ui.output_panel import OutputPanel
from ui.widgets import StatusBar, DeviceInfoCard, FlatButton, ToolTip


class MainWindow:
    """
    Wraps the root Tk window.  All widget construction happens here;
    the root itself is owned by main.py.
    """

    def __init__(self, controller, root: tk.Tk):
        self.controller = controller
        self.root = root

        root.title("Content Provider Explorer  ·  ADB PenTest Toolkit")
        root.geometry("1340x880")
        root.minsize(1050, 680)
        root.configure(bg=T.BG)
        root.resizable(True, True)

        styles.apply(root)
        self._build()

        controller.set_view(self)
        root.after(400, controller.on_refresh_devices)

    # Delegate common Tk methods so callers can treat MainWindow like a widget
    def mainloop(self):
        self.root.mainloop()

    def deiconify(self):
        self.root.deiconify()

    def after(self, ms, fn=None, *args):
        return self.root.after(ms, fn, *args)

    # ── Layout ────────────────────────────────────────────────────────────────
    def _build(self):
        self._build_titlebar()
        self._build_device_card()
        self._build_main_area()
        self._build_statusbar()

    def _build_titlebar(self):
        bar = tk.Frame(self.root, bg=T.BG, pady=8)
        bar.pack(fill="x", padx=T.PAD_LG)

        logo = tk.Frame(bar, bg=T.BG)
        logo.pack(side="left")
        tk.Label(logo, text="⬡", font=("Segoe UI", 20), fg=T.ACCENT,
                 bg=T.BG).pack(side="left", padx=(0, 6))
        title_col = tk.Frame(logo, bg=T.BG)
        title_col.pack(side="left")
        tk.Label(title_col, text="Content Provider Explorer",
                 font=T.FONT_TITLE, fg=T.TEXT_BRIGHT, bg=T.BG).pack(anchor="w")
        tk.Label(title_col, text="Android ADB Recon  ·  PenTest Edition",
                 font=T.FONT_UI_SM, fg=T.TEXT_DIM, bg=T.BG).pack(anchor="w")

        right = tk.Frame(bar, bg=T.BG)
        right.pack(side="right")
        FlatButton(right, "⟳ Refresh Devices",
                   self.controller.on_refresh_devices,
                   color=T.BG4, pady=4).pack(side="left", padx=4)
        FlatButton(right, "⬡ Android Ver",
                   self.controller.on_get_android_version,
                   color=T.ACCENT, pady=4).pack(side="left", padx=4)
        ToolTip(right.winfo_children()[-1], "adb shell getprop ro.build.version.sdk")
        FlatButton(right, "⬡ CPU Arch",
                   self.controller.on_get_architecture,
                   color=T.ACCENT2, pady=4).pack(side="left", padx=4)
        ToolTip(right.winfo_children()[-1], "adb shell getprop ro.product.cpu.abi")
        FlatButton(right, "⬡ Full Info",
                   self.controller.on_full_device_info,
                   color=T.PURPLE, pady=4).pack(side="left", padx=4)

        tk.Frame(self.root, bg=T.BORDER, height=1).pack(fill="x")

    def _build_device_card(self):
        card_bar = tk.Frame(self.root, bg=T.BG3, pady=2)
        card_bar.pack(fill="x")
        tk.Label(card_bar, text="  ACTIVE DEVICE:",
                 font=T.FONT_UI_SM, fg=T.TEXT_DIM, bg=T.BG3).pack(side="left")
        self.device_card = DeviceInfoCard(card_bar)
        self.device_card.pack(side="left")
        tk.Frame(self.root, bg=T.BORDER, height=1).pack(fill="x")

    def _build_main_area(self):
        paned = tk.PanedWindow(
            self.root, orient="horizontal", bg=T.BG,
            sashwidth=6, sashrelief="flat", relief="flat", bd=0,
        )
        paned.pack(fill="both", expand=True)

        self.sidebar = Sidebar(paned, self.controller)
        paned.add(self.sidebar, minsize=300, width=360)

        self.output_panel = OutputPanel(paned, self.controller)
        paned.add(self.output_panel, minsize=600)

    def _build_statusbar(self):
        tk.Frame(self.root, bg=T.BORDER, height=1).pack(fill="x")
        self.status_bar = StatusBar(self.root)
        self.status_bar.pack(fill="x", side="bottom")
        