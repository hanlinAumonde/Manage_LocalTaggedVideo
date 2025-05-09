import tkinter as tk
from tkinter import ttk
import os
from GUI.dialogs.base_dialog import BaseDialog
from utils.TagManage_utils import add_tag_to_entry, replace_current_tag

class TagDialog(BaseDialog):
    """Dialog for tag management"""
    def __init__(self, parent, lang_manager, db_manager, file_paths, save_callback):
        # Calculate appropriate size based on number of files
        size = "500x500"  # Initial size estimate
        
        super().__init__(parent, 
                        lang_manager.get_text("add_tags_to").format(len(file_paths)), 
                        size)
        
        self.lang_manager = lang_manager
        self.db_manager = db_manager
        self.file_paths = file_paths
        self.save_callback = save_callback
        self.suggestion_buttons = []
        self.suggestion_max_width = 10
        
        self._setup_ui()
        self._resize_dialog()
        
    def _setup_ui(self):
        # File info
        if len(self.file_paths) == 1:
            file_name = os.path.basename(self.file_paths[0])
            ttk.Label(self.dialog, text=f"{self.lang_manager.get_text('file')}{file_name}", 
                     font=('Segoe UI', 10, 'bold')).pack(pady=(10, 5), padx=10, anchor=tk.W)
        else:
            ttk.Label(self.dialog, text=self.lang_manager.get_text("selected").format(len(self.file_paths)), 
                     font=('Segoe UI', 10, 'bold')).pack(pady=(10, 5), padx=10, anchor=tk.W)

        # Current tags (if single file)
        self.current_tags = []
        if len(self.file_paths) == 1:
            self.current_tags = self.db_manager.get_tags_for_file(self.file_paths[0])
            if self.current_tags:
                ttk.Label(self.dialog, text=self.lang_manager.get_text("current_tags")).pack(pady=(5, 0), padx=10, anchor=tk.W)
                tag_text = ", ".join(self.current_tags)
                ttk.Label(self.dialog, text=tag_text).pack(pady=(0, 10), padx=10, anchor=tk.W)

        # Append tags checkbox
        self.append_var = tk.BooleanVar(value=True)  # Default to append mode
        append_check = ttk.Checkbutton(self.dialog, text=self.lang_manager.get_text("keep_existing_tags"),
                                     variable=self.append_var)
        append_check.pack(pady=5, padx=10, anchor=tk.W)

        # Tag input
        ttk.Label(self.dialog, text=self.lang_manager.get_text("enter_tags")).pack(pady=(5, 0), padx=10, anchor=tk.W)

        self.tag_var = tk.StringVar()
        tag_entry = ttk.Entry(self.dialog, textvariable=self.tag_var, width=50)
        tag_entry.pack(pady=(0, 10), padx=10, fill=tk.X)
        tag_entry.focus_set()

        # Top tags for suggestions
        ttk.Label(self.dialog, text=self.lang_manager.get_text("top_tags_click")).pack(pady=(5, 0), padx=10, anchor=tk.W)

        # Frame for tag buttons
        tags_frame = ttk.Frame(self.dialog)
        tags_frame.pack(pady=(0, 10), padx=10, fill=tk.X)

        # Get top tags
        top_tags = self.db_manager.get_top_tags(10)
        
        # Calculate maximum width for buttons
        max_width = 10  # Default minimum width
        for tag_info in top_tags:
            tag_name = tag_info["name"]
            tag_width = len(tag_name) + 2  # Add padding
            max_width = max(max_width, tag_width)
        
        self.suggestion_max_width = max_width
        
        # Create buttons with consistent width
        row, col = 0, 0
        for tag_info in top_tags:
            tag_name = tag_info["name"]

            # Create tag button with calculated width
            tag_btn = ttk.Button(tags_frame, text=tag_name, width=max_width,
                               command=lambda t=tag_name: add_tag_to_entry(self.tag_var, t))
            tag_btn.grid(row=row, column=col, padx=2, pady=2, sticky=tk.W)

            # Update grid position
            col += 1
            if col > 4:  # 5 buttons per row
                col = 0
                row += 1

        # Tag suggestion based on typing
        ttk.Label(self.dialog, text=self.lang_manager.get_text("tag_suggestions")).pack(pady=(5, 0), padx=10, anchor=tk.W)

        # Frame for suggestion buttons
        suggestion_frame = ttk.Frame(self.dialog)
        suggestion_frame.pack(pady=(0, 10), padx=10, fill=tk.X)

        # Create initial empty suggestion buttons
        for i in range(10):
            row = i // 5
            col = i % 5
            btn = ttk.Button(suggestion_frame, text="", width=max_width, state=tk.DISABLED)
            btn.grid(row=row, column=col, padx=2, pady=2)
            self.suggestion_buttons.append(btn)

        # Update suggestions as user types
        self.tag_var.trace_add("w", lambda n, i, m, v=self.tag_var: self._update_tag_suggestions(v))

        # Buttons
        btn_frame = ttk.Frame(self.dialog)
        btn_frame.pack(pady=10, fill=tk.X, side=tk.BOTTOM)

        ttk.Button(btn_frame, text=self.lang_manager.get_text("cancel"), 
                  command=self.destroy).pack(side=tk.RIGHT, padx=(5, 10))
                  
        ttk.Button(btn_frame, text=self.lang_manager.get_text("save_tags"), 
                  style="Accent.TButton",
                  command=self._on_save).pack(side=tk.RIGHT)

        # Bind Enter key
        self.dialog.bind("<Return>", lambda e: self._on_save())
        
    def _resize_dialog(self):
        """Calculate and set optimal dialog size"""
        buttons_per_row = 5
        button_padding = 4
        min_dialog_width = 500
        
        # Calculate width required by buttons
        button_width_pixels = (self.suggestion_max_width * 8) + button_padding
        total_button_width = (button_width_pixels * buttons_per_row) + (button_padding * (buttons_per_row - 1))
        
        # Add padding for dialog borders
        optimal_width = max(min_dialog_width, total_button_width + 40)
        
        # Update dialog size, keeping the height
        self.dialog.update()
        current_height = self.dialog.winfo_height()
        self.dialog.geometry(f"{optimal_width}x{current_height}")
        
        # Re-center dialog
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (optimal_width // 2)
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (current_height // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
    def _update_tag_suggestions(self, tag_var):
        """Update tag suggestions based on current input"""
        text = tag_var.get()
        if not text:
            for btn in self.suggestion_buttons:
                btn.config(text="", state=tk.DISABLED)
            return

        # Get the last tag being typed
        tags = [t.strip() for t in text.replace("，", ",").split(",")]
        current_tag = tags[-1].strip() if tags else ""

        if not current_tag:
            for btn in self.suggestion_buttons:
                btn.config(text="", state=tk.DISABLED)
            return

        # Get suggestions
        suggestions = self.db_manager.search_similar_tags(current_tag)
        
        # Calculate maximum width required
        max_width = self.suggestion_max_width
        for suggestion in suggestions:
            suggestion_width = len(suggestion) + 2  # Add padding
            max_width = max(max_width, suggestion_width)
        
        # Update buttons width for consistency
        for btn in self.suggestion_buttons:
            btn.config(width=max_width)
        
        # Update buttons
        for i, btn in enumerate(self.suggestion_buttons):
            if i < len(suggestions):
                btn.config(text=suggestions[i], state=tk.NORMAL,
                           command=lambda t=suggestions[i], ct=current_tag: replace_current_tag(self.tag_var, t))
            else:
                btn.config(text="", state=tk.DISABLED)
                
    def _on_save(self):
        """Save tags and close dialog"""
        tag_text = self.tag_var.get()
        append = self.append_var.get()
        self.save_callback(self.file_paths, tag_text, append)
        self.destroy()