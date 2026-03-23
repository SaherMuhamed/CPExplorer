"""
ui/theme.py — Centralised design tokens for Content Provider Explorer
Dark terminal aesthetic with amber/green accent — hacker utility feel
"""

# ── Palette ─────────────────────────────────────────────────────────────────
BG          = "#080c10"      # deep void background
BG2         = "#0d1219"      # panel bg
BG3         = "#131a23"      # input / card bg
BG4         = "#1a2333"      # hover / selected
BORDER      = "#1e2d3d"      # subtle border
BORDER2     = "#2a3f55"      # active border

ACCENT      = "#00d4ff"      # cyan primary
ACCENT_DIM  = "#0099bb"      # muted cyan
ACCENT2     = "#39d353"      # green success
WARN        = "#f0a500"      # amber warning
DANGER      = "#ff4444"      # red danger
PURPLE      = "#bd93f9"      # purple for special ops

TEXT        = "#cdd9e5"      # primary text
TEXT_DIM    = "#5c7a96"      # muted text
TEXT_BRIGHT = "#e8f4ff"      # highlight text

# ── Tag colors for output terminal ──────────────────────────────────────────
TAG_HEADER  = "#00d4ff"
TAG_SUCCESS = "#39d353"
TAG_WARN    = "#f0a500"
TAG_ERROR   = "#ff4444"
TAG_CMD     = "#5c7a96"
TAG_TS      = "#2a3f55"
TAG_KEY     = "#bd93f9"
TAG_VAL     = "#cdd9e5"
TAG_ROW_NUM = "#f0a500"

# ── Fonts ────────────────────────────────────────────────────────────────────
import platform
_os = platform.system()

if _os == "Windows":
    FONT_MONO    = ("Cascadia Code",  9)
    FONT_MONO_LG = ("Cascadia Code", 10)
    FONT_MONO_SM = ("Cascadia Code",  8)
    FONT_UI      = ("Segoe UI",       9)
    FONT_UI_SM   = ("Segoe UI",       8)
    FONT_UI_LG   = ("Segoe UI",      11)
    FONT_TITLE   = ("Segoe UI",      13, "bold")
    FONT_LABEL   = ("Segoe UI",       9)
    FONT_BTN     = ("Segoe UI",       9, "bold")
    FONT_SECTION = ("Segoe UI",       9, "bold")
elif _os == "Darwin":
    FONT_MONO    = ("Menlo",          9)
    FONT_MONO_LG = ("Menlo",         10)
    FONT_MONO_SM = ("Menlo",          8)
    FONT_UI      = ("SF Pro Text",    9)
    FONT_UI_SM   = ("SF Pro Text",    8)
    FONT_UI_LG   = ("SF Pro Text",   11)
    FONT_TITLE   = ("SF Pro Display",13, "bold")
    FONT_LABEL   = ("SF Pro Text",    9)
    FONT_BTN     = ("SF Pro Text",    9, "bold")
    FONT_SECTION = ("SF Pro Text",    9, "bold")
else:
    FONT_MONO    = ("DejaVu Sans Mono", 9)
    FONT_MONO_LG = ("DejaVu Sans Mono",10)
    FONT_MONO_SM = ("DejaVu Sans Mono", 8)
    FONT_UI      = ("Ubuntu",           9)
    FONT_UI_SM   = ("Ubuntu",           8)
    FONT_UI_LG   = ("Ubuntu",          11)
    FONT_TITLE   = ("Ubuntu",          13, "bold")
    FONT_LABEL   = ("Ubuntu",           9)
    FONT_BTN     = ("Ubuntu",           9, "bold")
    FONT_SECTION = ("Ubuntu",           9, "bold")

# ── Sizing ───────────────────────────────────────────────────────────────────
PAD         = 10
PAD_SM      = 6
PAD_LG      = 16
RADIUS      = 4
BTN_PADY    = 5
BTN_PADX    = 12
