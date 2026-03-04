"""
typist.py

Types text at a screen position using pyautogui.
"""

import pyautogui


class Typist:
    @staticmethod
    def type_at(x, y, text):
        """Click (x, y) to focus, then type *text*."""
        pyautogui.click(x, y)
        pyautogui.write(text, interval=0.05)
