#!/usr/bin/env python3
"""
main.py — Entry point for Content Provider Explorer
Usage:
    python main.py
"""

import sys
import os
import tkinter as tk

# Ensure project root is on the path when run directly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.app import AppController
from ui.main_window import MainWindow


def main():
    # Tk root MUST exist before any tk.StringVar / tk.IntVar is created
    root = tk.Tk()
    root.withdraw()                         # hide until MainWindow is ready

    controller = AppController(root=root)
    window = MainWindow(controller, root=root)
    window.deiconify()
    window.mainloop()


if __name__ == "__main__":
    main()
    