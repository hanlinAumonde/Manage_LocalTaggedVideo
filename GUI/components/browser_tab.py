import os
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinterdnd2 import DND_FILES
from GUI.dialogs.tag_dialog import TagDialog
from GUI.dialogs.folder_dialog import NewFolderDialog
from utils.TagManage_utils import get_list_sorted

class BrowseTab:
    """Tab for browsing and managing files"""
    def __init__(self, parent, lang_manager, db_manager, on_refresh_tags):
        self.parent = parent
        self.tab = ttk.Frame(parent)
        self.lang_manager = lang_manager
        self.db_manager = db_manager
        self.on_refresh_tags = on_refresh_tags
        
        # File state
        self.current_path = tk.StringVar()
        self.current_path.set("")
        self.first_path = self.current_path.get()
        self.file_list = []
        self.path_before_search = ""

        # Sort flags
        self.sort_by_name_desc = True
        self.sort_by_size_desc = True
        self.sort_by_time_desc = True

        self._setup_ui()
        
    def get_tab(self):
        return self.tab
        
    def _setup_ui(self):
        # Top frame for directory selection and navigation
        dir_frame = ttk.Frame(self.tab)
        dir_frame.pack(fill=tk.X, padx=10, pady=10)

        # Current path display
        ttk.Label(dir_frame, text=self.lang_manager.get_text("directory")).pack(side=tk.LEFT, padx=(0, 5))
        path_entry = ttk.Entry(dir_frame, textvariable=self.current_path, width=50, state="readonly")
        path_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        # Browse button
        browse_btn = ttk.Button(dir_frame, text=self.lang_manager.get_text("browse"), 
                              style="Accent.TButton", command=self._select_directory)
        browse_btn.pack(side=tk.LEFT, padx=5)

        # Back button
        self.back_btn = ttk.Button(dir_frame, text=self.lang_manager.get_text("back"), 
                                 command=self._go_back, state=tk.DISABLED)
        self.back_btn.pack(side=tk.LEFT, padx=5)

        # Create new folder button
        self.new_folder_btn = ttk.Button(dir_frame, text=self.lang_manager.get_text("new_folder"), 
                                       command=self._create_folder_dialog, state=tk.DISABLED)
        self.new_folder_btn.pack(side=tk.LEFT, padx=5)

        # Search frame
        search_frame = ttk.Frame(self.tab)
        search_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(search_frame, text=self.lang_manager.get_text("search")).pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar(value=self.lang_manager.get_text("search_in_currentDir"))
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        search_btn = ttk.Button(search_frame, text=self.lang_manager.get_text("search_btn"), 
                              command=lambda: self._search_files(self.search_var.get()))
        search_btn.pack(side=tk.LEFT, padx=5)

        end_search_btn = ttk.Button(search_frame, text=self.lang_manager.get_text("clear_search"), 
                                  command=lambda: self._go_back(True))
        end_search_btn.pack(side=tk.LEFT, padx=5)

        # Main file tree frame
        tree_frame = ttk.Frame(self.tab)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Create vertical scrollbar
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        # Create horizontal scrollbar
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")
        hsb.pack(side=tk.BOTTOM, fill=tk.X)

        # Create Treeview for files
        self.tree = ttk.Treeview(tree_frame, columns=("type", "name", "size", "time", "tags"),
                                show="headings", yscrollcommand=vsb.set, xscrollcommand=hsb.set,
                                selectmode="extended")

        # Configure scrollbars
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)

        # Configure tree columns
        self.tree.heading("type", text=self.lang_manager.get_text("type"))
        self.tree.heading("name", text=self.lang_manager.get_text("name"), 
                        command=lambda: self._sort_by("name"))
        self.tree.heading("size", text=self.lang_manager.get_text("size"), 
                        command=lambda: self._sort_by("size"))
        self.tree.heading("time", text=self.lang_manager.get_text("time"), 
                        command=lambda: self._sort_by("time"))
        self.tree.heading("tags", text=self.lang_manager.get_text("tags"))

        # Set column widths
        self.tree.column("type", width=70, anchor=tk.CENTER)
        self.tree.column("name", width=300, anchor=tk.W)
        self.tree.column("size", width=100, anchor=tk.E)
        self.tree.column("time", width=150, anchor=tk.CENTER)
        self.tree.column("tags", width=250, anchor=tk.W)

        # Display the tree
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Bind events
        self.tree.bind("<Double-1>", self._on_double_click)
        self.tree.bind("<Button-3>", self._show_context_menu)
        self.tree.bind("<Delete>", lambda e: self._delete_file())

        # Register drag and drop
        self.tree.drop_target_register(DND_FILES)
        self.tree.dnd_bind('<<Drop>>', self._handle_drop)
        self._set_drop_state(False)  # Initially disabled

        # Button frame for tagging
        tag_buttons_frame = ttk.Frame(self.tab)
        tag_buttons_frame.pack(fill=tk.X, padx=10, pady=10)

        tag_btn = ttk.Button(tag_buttons_frame, text=self.lang_manager.get_text("add_tags"), 
                           style="Accent.TButton", command=self._tag_selected_files)
        tag_btn.pack(side=tk.LEFT, padx=5)

        remove_tag_btn = ttk.Button(tag_buttons_frame, text=self.lang_manager.get_text("remove_tags"),
                                  command=self._remove_tags_from_selected)
        remove_tag_btn.pack(side=tk.LEFT, padx=5)
        
    def update_language(self, lang_manager):
        """Update UI language"""
        self.lang_manager = lang_manager
        
        # Rebuild UI with new language
        for widget in self.tab.winfo_children():
            widget.destroy()
            
        self._setup_ui()
        
        # Reload treeview if we have files
        if self.file_list:
            self._update_treeview()
            
    def _select_directory(self):
        """Open directory selection dialog"""
        path = filedialog.askdirectory()
        if path:
            self.current_path.set(path)
            self.first_path = path
            self.file_list = self.db_manager.get_calculated_list(path)
            self.back_btn.config(state=tk.NORMAL)
            self.new_folder_btn.config(state=tk.NORMAL)
            self._set_drop_state(True)
            self._update_treeview()
            
    def _go_back(self, after_search=False):
        """Navigate back to parent directory or clear search"""
        path = self.current_path.get()
        if path == "Please select a directory":
            return

        if not after_search:
            # Go to parent directory
            parent_path = os.path.dirname(path)
            if os.path.normpath(parent_path) == os.path.normpath(self.first_path):
                self.back_btn.config(state=tk.DISABLED)
            self.current_path.set(parent_path)
        else:
            # Clear search and return to previous path
            if self.path_before_search and path != self.path_before_search:
                self.current_path.set(self.path_before_search)

        self.path_before_search = ""
        self.file_list = self.db_manager.get_calculated_list(self.current_path.get())
        self._update_treeview()
        
    def _create_folder_dialog(self):
        """Show dialog to create a new folder"""
        NewFolderDialog(self.parent, self.lang_manager, self._create_folder)
        
    def _create_folder(self, folder_name):
        """Create a new folder with the given name"""
        try:
            path = os.path.join(self.current_path.get(), folder_name)
            os.mkdir(path)
            self.file_list = self.db_manager.get_calculated_list(self.current_path.get())
            self._update_treeview()
        except OSError as e:
            messagebox.showerror(self.lang_manager.get_text("error"), 
                              f"{self.lang_manager.get_text('create_folder_failed')}{str(e)}")
                              
    def _on_double_click(self, event):
        """Handle double-click on file/folder in tree"""
        region = self.tree.identify_region(event.x, event.y)
        if region == "heading":
            return

        selection = self.tree.selection()
        if not selection:
            return

        item = selection[0]
        item_data = self.tree.item(item, "tags")

        if not item_data:
            return

        # Check if it's a directory or file
        is_dir = item_data[0] == "True"
        path = item_data[1]

        if is_dir:
            # Navigate to directory
            self.current_path.set(path)
            if self.path_before_search:
                self.path_before_search = ""
            self.file_list = self.db_manager.get_calculated_list(path)
            self.back_btn.config(state=tk.NORMAL)
            self._update_treeview()
        else:
            # Open file
            try:
                os.startfile(path)
            except:
                messagebox.showerror("Error", "Could not open the file.")
                
    def _show_context_menu(self, event):
        """Show context menu on right-click"""
        selection = self.tree.selection()
        if not selection:
            return

        item = selection[0]
        item_data = self.tree.item(item, "tags")

        if not item_data:
            return

        # Check if it's a file
        is_dir = item_data[0] == "True"
        path = item_data[1]

        menu = tk.Menu(self.parent, tearoff=0)

        if is_dir:
            menu.add_command(label="打开文件夹", command=lambda: self._on_double_click(event))
        else:
            menu.add_command(label="打开文件", command=lambda: os.startfile(path))
            menu.add_separator()
            menu.add_command(label="添加标签", command=lambda: self._tag_selected_files([item]))
            menu.add_command(label="移除标签", command=lambda: self._remove_tags_from_selected([item]))

        menu.add_separator()
        menu.add_command(label="删除", command=self._delete_file)

        # Display menu at cursor position
        menu.post(event.x_root, event.y_root)
        
    def _delete_file(self):
        """Delete selected file or directory"""
        selection = self.tree.selection()
        if not selection:
            return

        item = selection[0]
        item_data = self.tree.item(item, "tags")

        if not item_data:
            return

        is_dir = item_data[0] == "True"
        path = item_data[1]

        # Confirm deletion
        message = self.lang_manager.get_text("confirm_delete_msg").format(
            self.lang_manager.get_text("folder") if is_dir else self.lang_manager.get_text("video"))
        if not messagebox.askyesno(self.lang_manager.get_text("confirm_delete"), message):
            return

        try:
            if is_dir:
                shutil.rmtree(path)
            else:
                os.remove(path)

            self.file_list = self.db_manager.get_calculated_list(self.current_path.get())
            self._update_treeview()
        except OSError as e:
            messagebox.showerror(self.lang_manager.get_text("error"), 
                              f"{self.lang_manager.get_text('delete_failed')}{str(e)}")
                              
    def _handle_drop(self, event):
        """Handle files dropped onto the tree"""
        files = self.parent.splitlist(event.data)
        current_dir = self.current_path.get()

        for file_path in files:
            try:
                # Normalize path
                file_path = file_path.replace("\\", "/")
                file_name = os.path.basename(file_path)
                target_path = os.path.join(current_dir, file_name)

                # If target exists, add a number suffix
                counter = 1
                base_name, ext = os.path.splitext(file_name)
                while os.path.exists(target_path):
                    target_path = os.path.join(current_dir, f"{base_name}_{counter}{ext}")
                    counter += 1

                # Move file
                shutil.move(file_path, target_path)

                # Refresh view
                self.file_list = self.db_manager.get_calculated_list(current_dir)
                self._update_treeview()

            except Exception as e:
                messagebox.showerror("Error", f"Failed to move file: {str(e)}")
                
    def _set_drop_state(self, enabled):
        """Enable or disable drag and drop functionality"""
        if enabled:
            self.tree.configure(cursor="")
            self.tree.drop_target_register(DND_FILES)
        else:
            self.tree.configure(cursor="no")
            self.tree.drop_target_unregister()
            
    def _search_files(self, search_text):
        """Search for files in current directory"""
        if not search_text.strip():
            return

        self.path_before_search = self.current_path.get()
        filtered_list = []

        for item in self.file_list:
            if search_text.lower() in item.name.lower():
                filtered_list.append(item)

        self.file_list = filtered_list
        self._update_treeview()
        
    def _sort_by(self, column):
        """Sort file list by the given column"""
        if column == "name":
            self.file_list = get_list_sorted(self.file_list, "name", self.sort_by_name_desc)
            self.sort_by_name_desc = not self.sort_by_name_desc
        elif column == "size":
            self.file_list = get_list_sorted(self.file_list, "size", self.sort_by_size_desc)
            self.sort_by_size_desc = not self.sort_by_size_desc
        elif column == "time":
            self.file_list = get_list_sorted(self.file_list, "time", self.sort_by_time_desc)
            self.sort_by_time_desc = not self.sort_by_time_desc

        self._update_treeview()
        
    def _update_treeview(self):
        """Update the file tree view with current file list"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Update back button state
        if self.current_path.get().startswith(self.first_path) and self.current_path.get() != self.first_path:
            self.back_btn.config(state=tk.NORMAL)
        elif self.current_path.get() == self.first_path:
            self.back_btn.config(state=tk.DISABLED)

        # Add files and directories to tree
        for item in self.file_list:
            tags_text = ", ".join(item.tags) if item.tags else ""

            self.tree.insert("", "end", values=(
                self.lang_manager.get_text("folder") if item.isDir else self.lang_manager.get_text("video"),
                item.name,
                item.getSizeConverted(),
                item.getDateFormatted(),
                tags_text
            ), tags=(str(item.isDir), item.path))
            
    def _tag_selected_files(self, items=None):
        """Show dialog to add tags to selected files"""
        if items is None:
            items = self.tree.selection()

        if not items:
            messagebox.showinfo(self.lang_manager.get_text("no_selection"), 
                              self.lang_manager.get_text("select_files"))
            return

        # Get file paths
        file_paths = []
        for item in items:
            item_data = self.tree.item(item, "tags")
            if item_data and item_data[0] == "False":  # Only files, not directories
                file_paths.append(item_data[1])

        if not file_paths:
            messagebox.showinfo(self.lang_manager.get_text("no_files"), 
                              self.lang_manager.get_text("select_video_files"))
            return

        # Create tagging dialog
        TagDialog(self.parent, self.lang_manager, self.db_manager, file_paths, self._save_tags)
        
    def _save_tags(self, file_paths, tag_text, append=True):
        """Save tags to the selected files"""
        # Parse tags
        tags = [t.strip() for t in tag_text.replace("，",",").split(",") if t.strip()]

        try:
            # Update each file
            for path in file_paths:
                self.db_manager.add_or_update_tags(path, tags, append)

            # Refresh the view
            self.file_list = self.db_manager.get_calculated_list(self.current_path.get())
            self._update_treeview()

            # Refresh top tags
            self.on_refresh_tags()
        except Exception as e:
            messagebox.showerror(self.lang_manager.get_text("error"), 
                               f"{self.lang_manager.get_text('save_tags_failed')}: {str(e)}")
            
    def _remove_tags_from_selected(self, items=None):
        """Remove tags from selected files"""
        if items is None:
            items = self.tree.selection()

        if not items:
            messagebox.showinfo(self.lang_manager.get_text("no_selection"), 
                              self.lang_manager.get_text("select_files"))
            return

        # Get file paths
        file_paths = []
        for item in items:
            item_data = self.tree.item(item, "tags")
            if item_data and item_data[0] == "False":  # Only files, not directories
                file_paths.append(item_data[1])

        if not file_paths:
            messagebox.showinfo(self.lang_manager.get_text("no_files"), 
                              self.lang_manager.get_text("select_video_files"))
            return

        # Confirm remove
        message = self.lang_manager.get_text("confirm_remove_tags").format(len(file_paths))
        if not messagebox.askyesno(self.lang_manager.get_text("confirm"), message):
            return

        try:
            # Remove tags from each file
            for path in file_paths:
                self.db_manager.remove_tags_from_file(path)

            # Refresh views
            self.file_list = self.db_manager.get_calculated_list(self.current_path.get())
            self._update_treeview()
            self.on_refresh_tags()

        except Exception as e:
            messagebox.showerror(self.lang_manager.get_text("error"), 
                              f"{self.lang_manager.get_text('remove_tags_failed')}{str(e)}")
            
    def search_videos_by_tag(self, tags):
        """Search for videos with one or more tags"""
        if not tags:
            return
            
        # Switch to browse tab
        
        # Set different messages for single vs multiple tag search
        if len(tags) == 1:
            self.current_path.set(f"{self.lang_manager.get_text('tag_search_results').format(tags[0])}")
            # Find videos with a single tag
            tagged_videos = self.db_manager.find_videos_by_tag(tags[0])
            search_description = tags[0]
        else:
            self.current_path.set(f"{self.lang_manager.get_text('multi_tag_search_results').format(', '.join(tags))}")
            # Multi-tag search (AND operation)
            tagged_videos = self.db_manager.find_videos_by_tags(tags)
            
        if not tagged_videos:
            if len(tags) == 1:
                message = self.lang_manager.get_text("no_videos_with_tag").format(tags[0])
            else:
                message = self.lang_manager.get_text("no_videos_with_all_tags").format(", ".join(tags))
            messagebox.showinfo(self.lang_manager.get_text("no_results"), message)
            return False

        # Update path for context before updating the file list
        self.path_before_search = self.current_path.get()
        
        # Update file list and view
        self.file_list = tagged_videos
        self._update_treeview()
        return True