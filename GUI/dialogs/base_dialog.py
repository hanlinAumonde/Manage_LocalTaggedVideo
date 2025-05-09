import tkinter as tk

class BaseDialog:
    """Base class for dialogs with common functionality"""
    def __init__(self, parent, title, size="300x120"):
        self.parent = parent
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry(size)
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Center dialog on parent window
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (int(size.split("x")[0]) // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (int(size.split("x")[1]) // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
    def show(self):
        self.dialog.focus_set()
        
    def destroy(self):
        self.dialog.destroy()