import tkinter as tk
from tkinter import ttk, messagebox
from GUI.dialogs.base_dialog import BaseDialog

class NewFolderDialog(BaseDialog):
    """Dialog for creating a new folder"""
    def __init__(self, parent, lang_manager, create_callback):
        super().__init__(parent, lang_manager.get_text("new_folder"))
        self.lang_manager = lang_manager
        self.create_callback = create_callback
        self._setup_ui()
        
    def _setup_ui(self):
        ttk.Label(self.dialog, text=self.lang_manager.get_text("folder_name")).pack(pady=(10, 5))

        self.name_var = tk.StringVar()
        name_entry = ttk.Entry(self.dialog, textvariable=self.name_var, width=40)
        name_entry.pack(padx=10, pady=5, fill=tk.X)
        name_entry.focus_set()

        btn_frame = ttk.Frame(self.dialog)
        btn_frame.pack(pady=10, fill=tk.X)

        ttk.Button(btn_frame, text=self.lang_manager.get_text("cancel"), 
                  command=self.destroy).pack(side=tk.RIGHT, padx=(5, 10))
        
        ttk.Button(btn_frame, text=self.lang_manager.get_text("create"), 
                  style="Accent.TButton",
                  command=self._on_create).pack(side=tk.RIGHT)

        # Bind Enter key
        self.dialog.bind("<Return>", lambda e: self._on_create())
        
    def _on_create(self):
        folder_name = self.name_var.get().strip()
        if not folder_name:
            messagebox.showwarning(
                self.lang_manager.get_text("invalid_name"), 
                self.lang_manager.get_text("enter_folder_name")
            )
            return
            
        self.create_callback(folder_name)
        self.destroy()