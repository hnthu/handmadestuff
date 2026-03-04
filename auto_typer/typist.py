"""
typist.py

Types text at a screen position using pyautogui.
"""

from __future__ import annotations

import pyautogui


class Typist:
    """Types clipboard text at a target screen position."""

    DEFAULT_INTERVAL: float = 0.05  # seconds between keystrokes

    def __init__(self, interval: float = DEFAULT_INTERVAL) -> None:
        """
        Args:
            interval: Seconds between each keystroke (lower = faster typing).
        """
        self._interval = interval

    def type_at(self, x: int, y: int, text: str) -> None:
        """Click (x, y) to focus, then type *text*."""
        pyautogui.click(x, y)
        pyautogui.write(text, interval=self._interval)
