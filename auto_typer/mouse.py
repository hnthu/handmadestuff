"""
mouse.py

Mouse double-click listener.
"""

import time

from pynput import mouse


class MouseListenerManager:
    DOUBLE_CLICK_THRESHOLD = 0.25

    def __init__(self, on_double_click):
        """
        Args:
            on_double_click: callable(x, y) invoked on a left double-click.
        """
        self._callback = on_double_click
        self._last_click = time.time()
        self._listener = mouse.Listener(on_click=self._on_click)

    def _on_click(self, x, y, button, pressed):
        if button == mouse.Button.left and not pressed:
            now = time.time()
            if (now - self._last_click) < self.DOUBLE_CLICK_THRESHOLD:
                self._callback(x, y)
            self._last_click = now

    def start(self):
        self._listener.start()

    def stop(self):
        self._listener.stop()
