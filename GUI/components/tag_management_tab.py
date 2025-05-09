import tkinter as tk
from tkinter import ttk, messagebox
from utils.TagManage_utils import replace_current_tag

class TagManagementTab:
    """Tab for managing and searching tags"""
    def __init__(self, parent, lang_manager, db_manager, on_search_by_tag):
        self.parent = parent
        self.tab = ttk.Frame(parent)
        self.lang_manager = lang_manager
        self.db_manager = db_manager
        self.on_search_by_tag = on_search_by_tag
        
        # Search suggestions
        self.search_suggestion_buttons = []
        self.search_suggestion_max_width = 10
        
        self._setup_ui()
        
    def get_tab(self):
        return self.tab
        
    def _setup_ui(self):
        # create main frame for tag management without canvas scrolling
        main_frame = ttk.Frame(self.tab)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Top Tags section
        top_tags_frame = ttk.Frame(main_frame)
        top_tags_frame.pack(fill=tk.X, pady=10)

        ttk.Label(top_tags_frame, text=self.lang_manager.get_text("top_tags"), 
                 font=('Segoe UI', 12, 'bold')).pack(anchor=tk.W)

        # Create horizontal scrollbar for top tags
        top_tags_tree_frame = ttk.Frame(top_tags_frame)
        top_tags_tree_frame.pack(fill=tk.X, expand=False, pady=5)
        
        vsb = ttk.Scrollbar(top_tags_tree_frame, orient="vertical")
        hsb = ttk.Scrollbar(top_tags_tree_frame, orient="horizontal")
        
        # Increase height to show more tags at once
        self.top_tags_tree = ttk.Treeview(top_tags_tree_frame, columns=("name", "count"),
                                        show="headings", height=8,
                                        yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        vsb.config(command=self.top_tags_tree.yview)
        hsb.config(command=self.top_tags_tree.xview)
        
        self.top_tags_tree.heading("name", text=self.lang_manager.get_text("tag_name"))
        self.top_tags_tree.heading("count", text=self.lang_manager.get_text("usage_count"))

        self.top_tags_tree.column("name", width=200)
        self.top_tags_tree.column("count", width=100)

        # Grid layout for treeview and scrollbars
        self.top_tags_tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        top_tags_tree_frame.grid_columnconfigure(0, weight=1)
        top_tags_tree_frame.grid_rowconfigure(0, weight=1)
        
        self.top_tags_tree.bind("<Double-1>", self._on_tag_double_click)

        refresh_btn = ttk.Button(top_tags_frame, text=self.lang_manager.get_text("refresh"), 
                               command=self.refresh_top_tags)
        refresh_btn.pack(anchor=tk.E, pady=5)

        # Search by tag section
        search_tag_frame = ttk.Frame(main_frame)
        search_tag_frame.pack(fill=tk.X, pady=10)

        ttk.Label(search_tag_frame, text=self.lang_manager.get_text("search_by_tag"), 
                 font=('Segoe UI', 12, 'bold')).pack(anchor=tk.W)

        self.tag_search_var = tk.StringVar()
        tag_search_entry = ttk.Entry(search_tag_frame, textvariable=self.tag_search_var)
        tag_search_entry.pack(fill=tk.X, pady=5)
        
        # Add help text for multiple tag search
        ttk.Label(search_tag_frame, text=self.lang_manager.get_text("multi_tag_search_hint"),
                 font=('Segoe UI', 8)).pack(anchor=tk.W, pady=(0, 5))
        
        # Add tag suggestions frame
        suggestion_frame = ttk.Frame(search_tag_frame)
        suggestion_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Create suggestion buttons with the same layout as in tag dialog
        self.search_suggestion_buttons = []
        max_width = 10  # Default minimum width
        
        # Get top tags to calculate button width
        top_tags = self.db_manager.get_top_tags()
        for tag_info in top_tags:
            tag_name = tag_info["name"]
            tag_width = len(tag_name) + 2  # Add a little padding
            max_width = max(max_width, tag_width)
        
        # Store for later use in update_search_suggestions
        self.search_suggestion_max_width = max_width
        
        # Create suggestion buttons - still using 2 rows of 5 buttons for simplicity
        for i in range(10):
            row = i // 5
            col = i % 5
            btn = ttk.Button(suggestion_frame, text="", width=max_width, state=tk.DISABLED)
            btn.grid(row=row, column=col, padx=2, pady=2, sticky=tk.W)
            self.search_suggestion_buttons.append(btn)
        
        # Connect the tag_search_var to the update function
        self.tag_search_var.trace("w", lambda n, i, m, v=self.tag_search_var: self._update_search_suggestions(v))

        # Search button
        search_tag_btn = ttk.Button(search_tag_frame, text=self.lang_manager.get_text("search_btn"), 
                                  style="Accent.TButton",
                                  command=lambda: self._search_videos_by_tag(self.tag_search_var.get()))
        search_tag_btn.pack(fill=tk.X, pady=5)

        # initialize the tag management tab
        self.refresh_top_tags()
        
    def update_language(self, lang_manager):
        """Update UI language"""
        self.lang_manager = lang_manager
        
        # Rebuild UI with new language
        for widget in self.tab.winfo_children():
            widget.destroy()
            
        self._setup_ui()
        
    def refresh_top_tags(self):
        """Refresh the top tags display"""
        # Clear current tags
        for item in self.top_tags_tree.get_children():
            self.top_tags_tree.delete(item)

        # Get top tags
        top_tags = self.db_manager.get_top_tags()

        # Add to tree
        for tag_info in top_tags:
            self.top_tags_tree.insert("", "end", values=(tag_info["name"], tag_info["count"]))
            
    def _on_tag_double_click(self, event):
        """Handle double-click on a tag in top tags tree"""
        selection = self.top_tags_tree.selection()
        if not selection:
            return

        item = selection[0]
        tag_name = self.top_tags_tree.item(item, "values")[0]

        # Set the tag search field and search
        self.tag_search_var.set(tag_name)
        self._search_videos_by_tag(tag_name)
        
    def _search_videos_by_tag(self, tag):
        """Search for videos with one or more tags"""
        if not tag.strip():
            messagebox.showinfo(self.lang_manager.get_text("missing_tag"), 
                              self.lang_manager.get_text("enter_search_tag"))
            return

        # Split by comma to support multiple tag search
        tags = [t.strip() for t in tag.replace("，",",").split(",") if t.strip()]
        
        # Let parent handle the actual search
        self.on_search_by_tag(tags)
        
    def _update_search_suggestions(self, tag_var):
        """Update search tag suggestions based on current input"""
        text = tag_var.get()
        if not text:
            for btn in self.search_suggestion_buttons:
                btn.config(text="", state=tk.DISABLED)
            return

        # Get the last tag being typed
        tags = [t.strip() for t in text.replace("，",",").split(",")]
        current_tag = tags[-1].strip() if tags else ""

        if not current_tag:
            for btn in self.search_suggestion_buttons:
                btn.config(text="", state=tk.DISABLED)
            return

        # Get suggestions
        suggestions = self.db_manager.search_similar_tags(current_tag)
        
        # Calculate the maximum width required for suggestions
        max_width = self.search_suggestion_max_width  # Start with previously calculated width
        for suggestion in suggestions:
            suggestion_width = len(suggestion) + 2  # Add padding
            max_width = max(max_width, suggestion_width)
        
        # Update all buttons to the new width for consistency
        for btn in self.search_suggestion_buttons:
            btn.config(width=max_width)
        
        # Update buttons
        for i, btn in enumerate(self.search_suggestion_buttons):
            if i < len(suggestions):
                btn.config(text=suggestions[i], state=tk.NORMAL,
                          command=lambda t=suggestions[i], ct=current_tag: replace_current_tag(tag_var, t))
            else:
                btn.config(text="", state=tk.DISABLED)
