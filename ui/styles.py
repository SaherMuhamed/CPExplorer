"""
ui/styles.py — Apply ttk theme overrides for a consistent dark UI
"""

from tkinter import ttk
from ui import theme as T


def apply(root):
    style = ttk.Style(root)
    style.theme_use("clam")

    style.configure(".",
        background=T.BG,
        foreground=T.TEXT,
        fieldbackground=T.BG3,
        bordercolor=T.BORDER,
        relief="flat",
        troughcolor=T.BG2,
        selectbackground=T.BG4,
        selectforeground=T.TEXT_BRIGHT,
    )

    # Notebook
    style.configure("TNotebook",
        background=T.BG, tabmargins=[0, 0, 0, 0])
    style.configure("TNotebook.Tab",
        background=T.BG3, foreground=T.TEXT_DIM,
        padding=[14, 6], font=T.FONT_UI)
    style.map("TNotebook.Tab",
        background=[("selected", T.BG2), ("active", T.BG4)],
        foreground=[("selected", T.ACCENT), ("active", T.TEXT)])

    # Combobox
    style.configure("TCombobox",
        fieldbackground=T.BG3, background=T.BG3,
        foreground=T.TEXT, arrowcolor=T.ACCENT,
        selectbackground=T.BG4, selectforeground=T.TEXT,
        bordercolor=T.BORDER, lightcolor=T.BG3, darkcolor=T.BG3)
    style.map("TCombobox",
        fieldbackground=[("readonly", T.BG3)],
        foreground=[("readonly", T.TEXT)])

    # Treeview
    style.configure("Treeview",
        background=T.BG2, foreground=T.TEXT,
        fieldbackground=T.BG2, rowheight=26,
        font=T.FONT_MONO, bordercolor=T.BORDER,
        relief="flat")
    style.configure("Treeview.Heading",
        background=T.BG3, foreground=T.ACCENT,
        font=T.FONT_BTN, relief="flat",
        bordercolor=T.BORDER)
    style.map("Treeview",
        background=[("selected", T.BG4)],
        foreground=[("selected", T.TEXT_BRIGHT)])
    style.map("Treeview.Heading",
        background=[("active", T.BG4)])

    # Scrollbars — slim
    for orient in ("Vertical", "Horizontal"):
        style.configure(f"{orient}.TScrollbar",
            background=T.BG3, troughcolor=T.BG,
            arrowcolor=T.TEXT_DIM, relief="flat",
            bordercolor=T.BG2)
        style.map(f"{orient}.TScrollbar",
            background=[("active", T.BG4)])
    style.configure("Vertical.TScrollbar",   width=8)
    style.configure("Horizontal.TScrollbar", height=8)

    # Separator
    style.configure("TSeparator", background=T.BORDER)

    # PanedWindow sash
    style.configure("Sash", sashthickness=5, sashpad=2)

    # Progressbar
    style.configure("TProgressbar",
        troughcolor=T.BG3, background=T.ACCENT,
        thickness=4)
