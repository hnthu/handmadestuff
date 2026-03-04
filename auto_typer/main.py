#!/usr/bin/env python3
"""
Auto Typer - Entry point.
"""

import tkinter as tk

from auto_typer.app import ApplicationGUI


def main():
    root = tk.Tk()
    ApplicationGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
