"""
app.py

ApplicationGUI — main window for the Auto Typer tool.
"""

import tkinter as tk

from auto_typer.clipboard import ClipboardManager
from auto_typer.mouse import MouseListenerManager
from auto_typer.typist import Typist


class ApplicationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PyAutoGUI Typing Tool")
        self._clipboard = ClipboardManager()
        self._typist = Typist()
        self._listener = None
        self._build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self):
        tk.Label(self.root, text="Clipboard Content:").pack(pady=5)

        self._text_widget = tk.Text(self.root, height=4, width=50, state=tk.DISABLED)
        self._text_widget.pack(pady=5)

        tk.Button(self.root, text="Fetch Clipboard Content",
                  command=self._fetch_clipboard).pack(pady=5)

        self._start_btn = tk.Button(self.root, text="Start Listener",
                                    command=self._start_listener)
        self._start_btn.pack(pady=5)

        self._stop_btn = tk.Button(self.root, text="Stop Listener",
                                   command=self._stop_listener, state=tk.DISABLED)
        self._stop_btn.pack(pady=5)

    def _fetch_clipboard(self):
        content = self._clipboard.fetch()
        self._clipboard.show_in_widget(self._text_widget, content)

    def _start_listener(self):
        self._listener = MouseListenerManager(self._type_clipboard_at)
        self._listener.start()
        self._start_btn.config(state=tk.DISABLED)
        self._stop_btn.config(state=tk.NORMAL)

    def _stop_listener(self):
        if self._listener:
            self._listener.stop()
            self._listener = None
        self._start_btn.config(state=tk.NORMAL)
        self._stop_btn.config(state=tk.DISABLED)

    def _type_clipboard_at(self, x, y):
        text = self._clipboard.fetch()
        self._typist.type_at(x, y, text)

    def _on_close(self):
        self._stop_listener()
        self.root.destroy()
