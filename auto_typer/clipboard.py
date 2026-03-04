"""
clipboard.py

Clipboard read/write helpers.
"""

import tkinter as tk

import pyperclip


class ClipboardManager:
    def fetch(self):
        """Return the current clipboard text."""
        return pyperclip.paste()

    def show_in_widget(self, widget, content):
        """Display *content* inside a read-only Text widget."""
        widget.config(state=tk.NORMAL)
        widget.delete('1.0', tk.END)
        widget.insert(tk.END, content)
        widget.config(state=tk.DISABLED)
