import tkinter as tk
from tkinter import messagebox
import pyautogui
import pyperclip
from pynput import mouse
import threading
import time

# Single Responsibility: Handles clipboard operations
class ClipboardManager:
    def fetch_clipboard_content(self):
        return pyperclip.paste()

    def update_clipboard_content_in_widget(self, widget, content):
        widget.config(state=tk.NORMAL)
        widget.delete('1.0', tk.END)
        widget.insert(tk.END, content)
        widget.config(state=tk.DISABLED)

# Single Responsibility: Handles GUI operations
class ApplicationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PyAutoGUI Typing Tool")
        self.clipboard_manager = ClipboardManager()
        self.create_widgets()

    def create_widgets(self):
        clipboard_label = tk.Label(self.root, text="Clipboard Content:")
        clipboard_label.pack(pady=5)

        self.clipboard_text_widget = tk.Text(self.root, height=4, width=50)
        self.clipboard_text_widget.pack(pady=5)
        self.clipboard_text_widget.config(state=tk.DISABLED)

        fetch_clipboard_button = tk.Button(self.root, text="Fetch Clipboard Content", command=self.fetch_clipboard_content)
        fetch_clipboard_button.pack(pady=5)

        self.start_button = tk.Button(self.root, text="Start Listener", command=self.start_listener)
        self.start_button.pack(pady=5)

        self.stop_button = tk.Button(self.root, text="Stop Listener", command=self.stop_listener)
        self.stop_button.pack(pady=5)
        self.stop_button.config(state=tk.DISABLED)

    def fetch_clipboard_content(self):
        content = self.clipboard_manager.fetch_clipboard_content()
        self.clipboard_manager.update_clipboard_content_in_widget(self.clipboard_text_widget, content)

    def start_listener(self):
        # Create a new MouseListenerManager each time we start listening
        self.mouse_listener_manager = MouseListenerManager(type_clipboard_text)
        self.mouse_listener_manager.start()
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

    def stop_listener(self):
        # Stop the currently running listener
        self.mouse_listener_manager.stop()
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

# Single Responsibility: Monitors mouse events
class MouseListenerManager:
    def __init__(self, type_text_callback):
        self.type_text_callback = type_text_callback
        self.listener = mouse.Listener(on_click=self.on_click)
        self.last_click_time = time.time()
        self.double_click_threshold = 0.25

    def on_click(self, x, y, button, pressed):
        if button == mouse.Button.left and not pressed:
            current_click_time = time.time()
            if (current_click_time - self.last_click_time) < self.double_click_threshold:
                self.type_text_callback(x, y)
            self.last_click_time = current_click_time

    def start(self):
        self.listener.start()

    def stop(self):
        self.listener.stop()

# Single Responsibility: Manages the typing of text at a position
class Typist:
    @staticmethod
    def type_text_at_position(x, y, text):
        # Click the position to focus
        pyautogui.click(x, y)
        # Use keyboard to type the text
        pyautogui.write(text, interval=0.05)


def on_close():
    try:
        mouse_listener_manager.stop()
    except AttributeError:
        pass  # Listener wasn't started yet
    root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    gui = ApplicationGUI(root)
    clipboard_manager = ClipboardManager()
    typist = Typist()
    
    def type_clipboard_text(x, y):
        text_to_type = clipboard_manager.fetch_clipboard_content()
        typist.type_text_at_position(x, y, text_to_type)
    
    mouse_listener_manager = MouseListenerManager(type_clipboard_text)
    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()
