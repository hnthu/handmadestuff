"""
mouse.py

Mouse double-click listener.
"""

from __future__ import annotations

import time
from collections.abc import Callable

from pynput import mouse


class MouseListenerManager:
    """Listens for left-button double-clicks and invokes a callback."""

    DEFAULT_THRESHOLD: float = 0.25  # seconds between clicks

    def __init__(
        self,
        on_double_click: Callable[[int, int], None],
        threshold: float = DEFAULT_THRESHOLD,
    ) -> None:
        """
        Args:
            on_double_click: Called with (x, y) on a detected double-click.
            threshold: Max seconds between two clicks to count as a double-click.
        """
        self._callback = on_double_click
        self._threshold = threshold
        self._last_click: float = time.time()
        self._listener = mouse.Listener(on_click=self._on_click)

    def _on_click(self, x: int, y: int, button: mouse.Button, pressed: bool) -> None:
        if button == mouse.Button.left and not pressed:
            now = time.time()
            if (now - self._last_click) < self._threshold:
                self._callback(x, y)
            self._last_click = now

    def start(self) -> None:
        self._listener.start()

    def stop(self) -> None:
        self._listener.stop()
