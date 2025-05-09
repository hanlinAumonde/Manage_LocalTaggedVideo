import os
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from tkinterdnd2 import DND_FILES

from utils.TagManage_utils import get_list_sorted, setup_styles, replace_current_tag, add_tag_to_entry
# Import our database manager
from DB.db_manager import DBManager
# Import language manager
from utils.language_manager import LanguageManager

class VideoTagApp:
    def __init__(self, root):
        self.root = root
        
        # Initialize language manager
        self.lang_manager = LanguageManager()
        
        self.root.title(self.lang_manager.get_text("app_title"))
        self.root.geometry("1200x700")
        self.root.minsize(800, 600)

        # Initialize database manager
        self.db_manager = DBManager()

        # Current path for file browsing
        self.current_path = tk.StringVar()
        self.current_path.set("Please select a directory")
        self.first_path = self.current_path.get()

        # Files list for current directory
        self.file_list = []
        self.path_before_search = ""

        # Sort flags
        self.sort_by_name_desc = True
        self.sort_by_size_desc = True
        self.sort_by_time_desc = True

        # Track selected files for tagging
        self.selected_files = []

        # Setup UI
        setup_styles()
        self.create_widgets()
        self.setup_notebook()

    def create_widgets(self):
        """Create the main application widgets"""
        # Create the main notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Initialize tabs
        self.browse_tab = ttk.Frame(self.notebook)
        self.tag_management_tab = ttk.Frame(self.notebook)

        # Add tabs to notebook
        self.notebook.add(self.browse_tab, text=self.lang_manager.get_text("browse_tab"))
        self.notebook.add(self.tag_management_tab, text=self.lang_manager.get_text("tag_management_tab"))
        
        # Language selection frame at the top of the window
        self.language_frame = ttk.Frame(self.root)
        self.language_frame.pack(fill=tk.X, padx=10, pady=(0, 0))
        
        ttk.Label(self.language_frame, text=self.lang_manager.get_text("language")).pack(side=tk.LEFT, padx=(0, 5))
        self.language_var = tk.StringVar(value=self.lang_manager.get_current_language())
        
        language_combo = ttk.Combobox(self.language_frame, textvariable=self.language_var, 
                                      values=["chinese", "English"], width=10, state="readonly")
        language_combo.pack(side=tk.LEFT)
        language_combo.bind("<<ComboboxSelected>>", self.change_language)
        
        # Add display labels for the languages
        ttk.Label(self.language_frame, text=" (").pack(side=tk.LEFT)
        ttk.Label(self.language_frame, text=self.lang_manager.get_text("chinese")).pack(side=tk.LEFT)
        ttk.Label(self.language_frame, text=" / ").pack(side=tk.LEFT)
        ttk.Label(self.language_frame, text=self.lang_manager.get_text("English")).pack(side=tk.LEFT)
        ttk.Label(self.language_frame, text=")").pack(side=tk.LEFT)

    def change_language(self, event=None):
        """Change the application language"""
        new_language = self.language_var.get()
        if self.lang_manager.set_language(new_language):
            # Update UI text
            self.update_ui_language()
    
    def update_ui_language(self):
        """Update all UI elements with the new language"""
        # Update window title
        self.root.title(self.lang_manager.get_text("app_title"))
        
        # Update notebook tabs
        self.notebook.tab(self.browse_tab, text=self.lang_manager.get_text("browse_tab"))
        self.notebook.tab(self.tag_management_tab, text=self.lang_manager.get_text("tag_management_tab"))
        
        # Recreate both tabs with new language
        self.setup_browse_tab()
        self.setup_tag_management_tab()
        
        # Update language selection labels
        for widget in self.language_frame.winfo_children():
            if isinstance(widget, ttk.Label):
                if widget.cget("text") == " (":
                    continue
                elif widget.cget("text") == " / ":
                    continue
                elif widget.cget("text") == ")":
                    continue
                elif widget.cget("text").startswith(self.lang_manager.get_text("language").split(":")[0]):
                    widget.config(text=self.lang_manager.get_text("language"))
                elif widget.cget("text") in ["中文", "English"]:
                    # These labels don't need to be translated as they show the actual language names
                    pass

    def setup_notebook(self):
        """Set up the tabs with their content"""
        # Setup Browse Files tab
        self.setup_browse_tab()

        # Setup Tag Management tab
        self.setup_tag_management_tab()

    def setup_browse_tab(self):
        """Setup the Browse Files tab"""
        # Clear existing content if any
        for widget in self.browse_tab.winfo_children():
            widget.destroy()
            
        # Top frame for directory selection and navigation
        dir_frame = ttk.Frame(self.browse_tab)
        dir_frame.pack(fill=tk.X, padx=10, pady=10)

        # Current path display
        ttk.Label(dir_frame, text=self.lang_manager.get_text("directory")).pack(side=tk.LEFT, padx=(0, 5))
        path_entry = ttk.Entry(dir_frame, textvariable=self.current_path, width=50, state="readonly")
        path_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        # Browse button
        browse_btn = ttk.Button(dir_frame, text=self.lang_manager.get_text("browse"), style="Accent.TButton", command=self.select_directory)
        browse_btn.pack(side=tk.LEFT, padx=5)

        # Back button
        self.back_btn = ttk.Button(dir_frame, text=self.lang_manager.get_text("back"), command=self.go_back, state=tk.DISABLED)
        self.back_btn.pack(side=tk.LEFT, padx=5)

        # Create new folder button
        self.new_folder_btn = ttk.Button(dir_frame, text=self.lang_manager.get_text("new_folder"), command=self.create_folder_dialog,
                                         state=tk.DISABLED)
        self.new_folder_btn.pack(side=tk.LEFT, padx=5)

        # Search frame
        search_frame = ttk.Frame(self.browse_tab)
        search_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(search_frame, text=self.lang_manager.get_text("search")).pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        search_btn = ttk.Button(search_frame, text=self.lang_manager.get_text("search_btn"), command=lambda: self.search_files(self.search_var.get()))
        search_btn.pack(side=tk.LEFT, padx=5)

        end_search_btn = ttk.Button(search_frame, text=self.lang_manager.get_text("clear_search"), command=lambda: self.go_back(True))
        end_search_btn.pack(side=tk.LEFT, padx=5)

        # Main file tree frame
        tree_frame = ttk.Frame(self.browse_tab)
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
        self.tree.heading("name", text=self.lang_manager.get_text("name"), command=lambda: self.sort_by("name"))
        self.tree.heading("size", text=self.lang_manager.get_text("size"), command=lambda: self.sort_by("size"))
        self.tree.heading("time", text=self.lang_manager.get_text("time"), command=lambda: self.sort_by("time"))
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
        self.tree.bind("<Double-1>", self.on_double_click)
        self.tree.bind("<Button-3>", self.show_context_menu)
        self.tree.bind("<Delete>", lambda e: self.delete_file())

        # Register drag and drop (initially disabled)
        self.tree.drop_target_register(DND_FILES)
        self.tree.dnd_bind('<<Drop>>', self.handle_drop)
        self.set_drop_state(False)

        # Button frame for tagging
        tag_buttons_frame = ttk.Frame(self.browse_tab)
        tag_buttons_frame.pack(fill=tk.X, padx=10, pady=10)

        tag_btn = ttk.Button(tag_buttons_frame, text=self.lang_manager.get_text("add_tags"), style="Accent.TButton",
                            command=self.tag_selected_files)
        tag_btn.pack(side=tk.LEFT, padx=5)

        remove_tag_btn = ttk.Button(tag_buttons_frame, text=self.lang_manager.get_text("remove_tags"),
                                   command=self.remove_tags_from_selected)
        remove_tag_btn.pack(side=tk.LEFT, padx=5)
        
        # Update the treeview if we already have files loaded
        if self.file_list:
            self.update_treeview()

    def setup_tag_management_tab(self):
        """Setup the Tag Management tab"""
        # Clear existing content if any
        for widget in self.tag_management_tab.winfo_children():
            widget.destroy()
            
        # 创建一个框架作为容器，确保它填充整个标签页
        main_frame = ttk.Frame(self.tag_management_tab)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 创建Canvas和滚动条
        canvas_frame = ttk.Frame(main_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(canvas_frame)
        vsb = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        hsb = ttk.Scrollbar(canvas_frame, orient="horizontal", command=canvas.xview)

        # 配置Canvas的滚动区域
        canvas.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # 放置滚动条和Canvas，确保Canvas填充整个区域
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 内容框架
        content_frame = ttk.Frame(canvas)

        # 创建窗口并将内容框架放入canvas
        canvas_window = canvas.create_window((0, 0), window=content_frame, anchor="nw")

        # 绑定Canvas大小变化事件，确保内容框架宽度与Canvas匹配
        def configure_window(event):
            # 更新滚动区域以包含整个内容
            canvas.configure(scrollregion=canvas.bbox("all"))
            # 更新内容框架宽度以匹配Canvas宽度
            canvas.itemconfig(canvas_window, width=canvas.winfo_width())

        canvas.bind('<Configure>', configure_window)
        content_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # 添加鼠标滚轮支持
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(-1 * (e.delta // 120), "units"))
        canvas.bind_all("<Shift-MouseWheel>", lambda e: canvas.xview_scroll(-1 * (e.delta // 120), "units"))

        # -- 以下是内容部分 --

        # Top Tags section
        top_tags_frame = ttk.Frame(content_frame)
        top_tags_frame.pack(fill=tk.X, pady=10)

        ttk.Label(top_tags_frame, text=self.lang_manager.get_text("top_tags"), font=('Segoe UI', 12, 'bold')).pack(anchor=tk.W)

        # Reduce the height of the Treeview
        self.top_tags_tree = ttk.Treeview(top_tags_frame, columns=("name", "count"),
                                        show="headings", height=5)

        self.top_tags_tree.heading("name", text=self.lang_manager.get_text("tag_name"))
        self.top_tags_tree.heading("count", text=self.lang_manager.get_text("usage_count"))

        self.top_tags_tree.column("name", width=200)
        self.top_tags_tree.column("count", width=100)

        self.top_tags_tree.pack(fill=tk.X, expand=True, pady=5)
        self.top_tags_tree.bind("<Double-1>", self.on_tag_double_click)

        refresh_btn = ttk.Button(top_tags_frame, text=self.lang_manager.get_text("refresh"), command=self.refresh_top_tags)
        refresh_btn.pack(anchor=tk.E, pady=5)

        # Search by tag section
        search_tag_frame = ttk.Frame(content_frame)
        search_tag_frame.pack(fill=tk.X, pady=10)

        ttk.Label(search_tag_frame, text=self.lang_manager.get_text("search_by_tag"), font=('Segoe UI', 12, 'bold')).pack(anchor=tk.W)

        self.tag_search_var = tk.StringVar()
        tag_search_entry = ttk.Entry(search_tag_frame, textvariable=self.tag_search_var)
        tag_search_entry.pack(fill=tk.X, pady=5)

        search_tag_btn = ttk.Button(search_tag_frame, text=self.lang_manager.get_text("search_btn"), style="Accent.TButton",
                                  command=lambda: self.search_videos_by_tag(self.tag_search_var.get()))
        search_tag_btn.pack(fill=tk.X, pady=5)

        # Untagged videos section
        untagged_frame = ttk.Frame(content_frame)
        untagged_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        ttk.Label(untagged_frame, text=self.lang_manager.get_text("untagged_videos"), font=('Segoe UI', 12, 'bold')).pack(anchor=tk.W)

        folders_frame = ttk.Frame(untagged_frame)
        folders_frame.pack(fill=tk.X, pady=5)

        self.folder_paths = []
        self.folder_listbox = tk.Listbox(folders_frame, height=3)
        self.folder_listbox.pack(side=tk.LEFT, fill=tk.X, expand=True)

        folder_btn_frame = ttk.Frame(folders_frame)
        folder_btn_frame.pack(side=tk.LEFT, padx=5)

        add_folder_btn = ttk.Button(folder_btn_frame, text=self.lang_manager.get_text("add_folder"),
                                  command=self.add_folder_for_untagged)
        add_folder_btn.pack(fill=tk.X, pady=2)

        remove_folder_btn = ttk.Button(folder_btn_frame, text=self.lang_manager.get_text("remove_folder"),
                                     command=self.remove_folder_for_untagged)
        remove_folder_btn.pack(fill=tk.X, pady=2)

        find_untagged_btn = ttk.Button(untagged_frame, text=self.lang_manager.get_text("find_untagged"),
                                     command=self.find_untagged_videos)
        find_untagged_btn.pack(fill=tk.X, pady=5)

        # 确保未标记视频的树形视图占据剩余空间
        tree_frame = ttk.Frame(untagged_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.untagged_tree = ttk.Treeview(tree_frame, columns=("name", "path", "size", "time"),
                                        show="headings", height=10)

        self.untagged_tree.heading("name", text=self.lang_manager.get_text("name"))
        self.untagged_tree.heading("path", text=self.lang_manager.get_text("path"))
        self.untagged_tree.heading("size", text=self.lang_manager.get_text("size"))
        self.untagged_tree.heading("time", text=self.lang_manager.get_text("time"))

        self.untagged_tree.column("name", width=200)
        self.untagged_tree.column("path", width=300)
        self.untagged_tree.column("size", width=100)
        self.untagged_tree.column("time", width=150)

        # 添加滚动条到未标记视频的树形视图
        untagged_vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.untagged_tree.yview)
        untagged_hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.untagged_tree.xview)
        self.untagged_tree.configure(yscrollcommand=untagged_vsb.set, xscrollcommand=untagged_hsb.set)

        untagged_vsb.pack(side=tk.RIGHT, fill=tk.Y)
        untagged_hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self.untagged_tree.pack(fill=tk.BOTH, expand=True)

        tag_untagged_btn = ttk.Button(untagged_frame, text=self.lang_manager.get_text("tag_selected"), style="Accent.TButton",
                                    command=self.tag_selected_untagged)
        tag_untagged_btn.pack(fill=tk.X, pady=5)

        # 初始加载热门标签
        self.refresh_top_tags()

    def select_directory(self):
        """Open directory selection dialog"""
        path = filedialog.askdirectory()
        if path:
            self.current_path.set(path)
            self.first_path = path
            self.file_list = self.db_manager.get_calculated_list(path)
            self.back_btn.config(state=tk.NORMAL)
            self.new_folder_btn.config(state=tk.NORMAL)
            self.set_drop_state(True)
            self.update_treeview()
        else:
            self.reset_app()

    def go_back(self, after_search=False):
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
        self.update_treeview()

    def create_folder_dialog(self):
        """Show dialog to create a new folder"""
        dialog = tk.Toplevel(self.root)
        dialog.title(self.lang_manager.get_text("new_folder"))
        dialog.geometry("300x120")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        # Center dialog on main window
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (300 // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (120 // 2)
        dialog.geometry(f"+{x}+{y}")

        ttk.Label(dialog, text=self.lang_manager.get_text("folder_name")).pack(pady=(10, 5))

        name_var = tk.StringVar()
        name_entry = ttk.Entry(dialog, textvariable=name_var, width=40)
        name_entry.pack(padx=10, pady=5, fill=tk.X)
        name_entry.focus_set()

        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10, fill=tk.X)

        ttk.Button(btn_frame, text=self.lang_manager.get_text("cancel"), command=dialog.destroy).pack(side=tk.RIGHT, padx=(5, 10))
        ttk.Button(btn_frame, text=self.lang_manager.get_text("create"), style="Accent.TButton",
                command=lambda: self.create_folder(name_var.get(), dialog)).pack(side=tk.RIGHT)

        # Bind Enter key to create folder
        dialog.bind("<Return>", lambda e: self.create_folder(name_var.get(), dialog))
        
    def create_folder(self, folder_name, dialog):
        """Create a new folder with the given name"""
        if not folder_name.strip():
            messagebox.showwarning(self.lang_manager.get_text("invalid_name"), 
                                  self.lang_manager.get_text("enter_folder_name"))
            return

        try:
            path = os.path.join(self.current_path.get(), folder_name)
            os.mkdir(path)
            self.file_list = self.db_manager.get_calculated_list(self.current_path.get())
            self.update_treeview()
            dialog.destroy()
        except OSError as e:
            messagebox.showerror(self.lang_manager.get_text("error"), 
                               f"{self.lang_manager.get_text('create_folder_failed')}{str(e)}")

    def on_double_click(self, event):
        """Handle double-click on file/folder in tree"""
        region = self.tree.identify_region(event.x, event.y)
        if region == "heading":
            return

        selection = self.tree.selection()
        if not selection:
            return

        item = selection[0]
        item_values = self.tree.item(item, "values")
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
            self.update_treeview()
        else:
            # Open file
            try:
                os.startfile(path)
            except:
                messagebox.showerror("Error", "Could not open the file.")

    def show_context_menu(self, event):
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

        menu = tk.Menu(self.root, tearoff=0)

        if is_dir:
            menu.add_command(label="打开文件夹", command=lambda: self.on_double_click(event))
        else:
            menu.add_command(label="打开文件", command=lambda: os.startfile(path))
            menu.add_separator()
            menu.add_command(label="添加标签", command=lambda: self.tag_selected_files([item]))
            menu.add_command(label="移除标签", command=lambda: self.remove_tags_from_selected([item]))

        menu.add_separator()
        menu.add_command(label="删除", command=self.delete_file)

        # Display menu at cursor position
        menu.post(event.x_root, event.y_root)

    def delete_file(self):
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
            self.update_treeview()
        except OSError as e:
            messagebox.showerror(self.lang_manager.get_text("error"), 
                              f"{self.lang_manager.get_text('delete_failed')}{str(e)}")

    def handle_drop(self, event):
        """Handle files dropped onto the tree"""
        files = self.root.splitlist(event.data)
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
                self.update_treeview()

            except Exception as e:
                messagebox.showerror("错误", f"移动文件失败: {str(e)}")

    def set_drop_state(self, enabled):
        """Enable or disable drag and drop functionality"""
        if enabled:
            self.tree.configure(cursor="")
            self.tree.drop_target_register(DND_FILES)
        else:
            self.tree.configure(cursor="no")
            self.tree.drop_target_unregister()

    def search_files(self, search_text):
        """Search for files in current directory"""
        if not search_text.strip():
            return

        self.path_before_search = self.current_path.get()
        filtered_list = []

        for item in self.file_list:
            if search_text.lower() in item.name.lower():
                filtered_list.append(item)

        self.file_list = filtered_list
        self.update_treeview()

    def sort_by(self, column):
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

        self.update_treeview()

    def update_treeview(self):
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
    
    def tag_selected_files(self, items=None):
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
        self.show_tag_dialog(file_paths)

    def show_tag_dialog(self, file_paths):
        """Show dialog to add tags to files"""
        dialog = tk.Toplevel(self.root)
        dialog.title(self.lang_manager.get_text("add_tags_to").format(len(file_paths)))
        dialog.geometry("500x450")  # Made taller to accommodate the new checkbox
        dialog.transient(self.root)
        dialog.grab_set()

        # Center dialog
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (500 // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (450 // 2)
        dialog.geometry(f"+{x}+{y}")

        # File info
        if len(file_paths) == 1:
            file_name = os.path.basename(file_paths[0])
            ttk.Label(dialog, text=f"{self.lang_manager.get_text('file')}{file_name}", 
                     font=('Segoe UI', 10, 'bold')).pack(pady=(10, 5), padx=10, anchor=tk.W)
        else:
            ttk.Label(dialog, text=self.lang_manager.get_text("selected").format(len(file_paths)), 
                     font=('Segoe UI', 10, 'bold')).pack(pady=(10, 5), padx=10, anchor=tk.W)

        # Current tags (if single file)
        current_tags = []
        if len(file_paths) == 1:
            current_tags = self.db_manager.get_tags_for_file(file_paths[0])
            if current_tags:
                ttk.Label(dialog, text=self.lang_manager.get_text("current_tags")).pack(pady=(5, 0), padx=10, anchor=tk.W)
                tag_text = ", ".join(current_tags)
                ttk.Label(dialog, text=tag_text).pack(pady=(0, 10), padx=10, anchor=tk.W)

        # Append tags checkbox
        append_var = tk.BooleanVar(value=True)  # Default to append mode
        append_check = ttk.Checkbutton(dialog, text=self.lang_manager.get_text("keep_existing_tags"),
                                     variable=append_var)
        append_check.pack(pady=5, padx=10, anchor=tk.W)

        # Tag input
        ttk.Label(dialog, text=self.lang_manager.get_text("enter_tags")).pack(pady=(5, 0), padx=10, anchor=tk.W)

        tag_var = tk.StringVar()

        tag_entry = ttk.Entry(dialog, textvariable=tag_var, width=50)
        tag_entry.pack(pady=(0, 10), padx=10, fill=tk.X)
        tag_entry.focus_set()

        # Top tags for suggestions
        ttk.Label(dialog, text=self.lang_manager.get_text("top_tags_click")).pack(pady=(5, 0), padx=10, anchor=tk.W)

        # Frame for tag buttons
        tags_frame = ttk.Frame(dialog)
        tags_frame.pack(pady=(0, 10), padx=10, fill=tk.X)

        # Get top tags
        top_tags = self.db_manager.get_top_tags(10)
        row, col = 0, 0
        for tag_info in top_tags:
            tag_name = tag_info["name"]

            # Create tag button
            tag_btn = ttk.Button(tags_frame, text=tag_name,
                               command=lambda t=tag_name: add_tag_to_entry(tag_var, t))
            tag_btn.grid(row=row, column=col, padx=2, pady=2, sticky=tk.W)

            # Update grid position
            col += 1
            if col > 4:  # 5 buttons per row
                col = 0
                row += 1

        # Tag suggestion based on typing
        ttk.Label(dialog, text=self.lang_manager.get_text("tag_suggestions")).pack(pady=(5, 0), padx=10, anchor=tk.W)

        suggestion_frame = ttk.Frame(dialog)
        suggestion_frame.pack(pady=(0, 10), padx=10, fill=tk.X)

        # Track suggestion buttons for dynamic updates
        self.suggestion_buttons = []

        # Create initial empty suggestion buttons
        for i in range(5):
            btn = ttk.Button(suggestion_frame, text="", state=tk.DISABLED)
            btn.pack(side=tk.LEFT, padx=2)
            self.suggestion_buttons.append(btn)

        # Update suggestions as user types
        tag_var.trace("w", lambda n, i, m, v=tag_var: self.update_tag_suggestions(v))

        # Buttons
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10, fill=tk.X, side=tk.BOTTOM)

        ttk.Button(btn_frame, text=self.lang_manager.get_text("cancel"), command=dialog.destroy).pack(side=tk.RIGHT, padx=(5, 10))
        ttk.Button(btn_frame, text=self.lang_manager.get_text("save_tags"), style="Accent.TButton",
                 command=lambda: self.save_tags(file_paths, tag_var.get(), dialog, append_var.get())).pack(
            side=tk.RIGHT)

        # Bind Enter key (make sure it also uses the append value)
        dialog.bind("<Return>", lambda e: self.save_tags(file_paths, tag_var.get(), dialog, append_var.get()))
    
    def update_tag_suggestions(self, tag_var):
        """Update tag suggestions based on current input"""
        text = tag_var.get()
        if not text:
            for btn in self.suggestion_buttons:
                btn.config(text="", state=tk.DISABLED)
            return

        # Get the last tag being typed
        tags = [t.strip() for t in text.split(",")]
        current_tag = tags[-1].strip() if tags else ""

        if not current_tag:
            for btn in self.suggestion_buttons:
                btn.config(text="", state=tk.DISABLED)
            return

        # Get suggestions
        suggestions = self.db_manager.search_similar_tags(current_tag)

        # Update buttons
        for i, btn in enumerate(self.suggestion_buttons):
            if i < len(suggestions):
                btn.config(text=suggestions[i], state=tk.NORMAL,
                           command=lambda t=suggestions[i], ct=current_tag: replace_current_tag(tag_var, t))
            else:
                btn.config(text="", state=tk.DISABLED)

    def save_tags(self, file_paths, tag_text, dialog, append=True):
        """Save tags to the selected files

        Args:
            file_paths: List of file paths to update
            tag_text: Comma-separated tag text
            dialog: Dialog window to close after saving
            append: If True, append new tags to existing ones; if False, replace existing tags
        """
        # Parse tags
        tags = [t.strip() for t in tag_text.split(",") if t.strip()]

        try:
            # Update each file
            for path in file_paths:
                self.db_manager.add_or_update_tags(path, tags, append)

            # Refresh the view
            self.file_list = self.db_manager.get_calculated_list(self.current_path.get())
            self.update_treeview()

            # Refresh top tags
            self.refresh_top_tags()

            dialog.destroy()
        except Exception as e:
            messagebox.showerror("错误", f"保存标签失败: {str(e)}")

    def remove_tags_from_selected(self, items=None):
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
            self.update_treeview()
            self.refresh_top_tags()

        except Exception as e:
            messagebox.showerror(self.lang_manager.get_text("error"), 
                               f"{self.lang_manager.get_text('remove_tags_failed')}{str(e)}")

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

    def on_tag_double_click(self, event):
        """Handle double-click on a tag in top tags tree"""
        selection = self.top_tags_tree.selection()
        if not selection:
            return

        item = selection[0]
        tag_name = self.top_tags_tree.item(item, "values")[0]

        # Set the tag search field and search
        self.tag_search_var.set(tag_name)
        self.search_videos_by_tag(tag_name)

    def search_videos_by_tag(self, tag):
        """Search for videos with the given tag"""
        if not tag.strip():
            messagebox.showinfo(self.lang_manager.get_text("missing_tag"), 
                              self.lang_manager.get_text("enter_search_tag"))
            return

        # Switch to browse tab
        self.notebook.select(self.browse_tab)

        # Find videos with this tag
        tagged_videos = self.db_manager.find_videos_by_tag(tag)

        if not tagged_videos:
            messagebox.showinfo(self.lang_manager.get_text("no_results"), 
                              self.lang_manager.get_text("no_videos_with_tag").format(tag))
            return

        # Update current path for context
        self.path_before_search = self.current_path.get()
        self.current_path.set(f"{self.lang_manager.get_text('tag_search_results').format(tag)}")

        # Update file list and view
        self.file_list = tagged_videos
        self.update_treeview()
    
    def add_folder_for_untagged(self):
        """Add a folder to search for untagged videos"""
        folder = filedialog.askdirectory()
        if folder:
            # Add to list if not already there
            if folder not in self.folder_paths:
                self.folder_paths.append(folder)
                self.folder_listbox.insert(tk.END, folder)

    def remove_folder_for_untagged(self):
        """Remove selected folder from untagged search list"""
        selection = self.folder_listbox.curselection()
        if selection:
            index = selection[0]
            self.folder_paths.pop(index)
            self.folder_listbox.delete(index)

    def find_untagged_videos(self):
        """Find untagged videos in the selected folders"""
        if not self.folder_paths:
            messagebox.showinfo(self.lang_manager.get_text("no_folders"), 
                              self.lang_manager.get_text("add_folders_to_search"))
            return

        # Show progress
        self.root.config(cursor="wait")
        self.root.update()

        try:
            # Get untagged videos
            untagged_videos = self.db_manager.get_untagged_videos(self.folder_paths)

            # Clear current list
            for item in self.untagged_tree.get_children():
                self.untagged_tree.delete(item)

            # Add to tree
            for video in untagged_videos:
                self.untagged_tree.insert("", "end", values=(
                    video.name,
                    video.path,
                    video.getSizeConverted(),
                    video.getDateFormatted()
                ), tags=(str(video.isDir), video.path))

            # Show result
            if not untagged_videos:
                messagebox.showinfo(self.lang_manager.get_text("no_results"), 
                                  self.lang_manager.get_text("no_untagged_videos"))

        except Exception as e:
            messagebox.showerror(self.lang_manager.get_text("error"), 
                               f"{self.lang_manager.get_text('error_finding_untagged')}{str(e)}")
        finally:
            self.root.config(cursor="")

    def tag_selected_untagged(self):
        """Tag selected untagged videos"""
        selection = self.untagged_tree.selection()
        if not selection:
            messagebox.showinfo("无选择", "请选择要标记的视频。")
            return

        # Get file paths
        file_paths = []
        for item in selection:
            item_data = self.untagged_tree.item(item, "tags")
            if item_data:
                file_paths.append(item_data[1])

        if not file_paths:
            return

        # Show tag dialog
        self.show_tag_dialog(file_paths)

        # Refresh untagged list after tagging
        self.find_untagged_videos()

    def reset_app(self):
        """Reset application state"""
        self.current_path.set("Please select a directory")
        self.file_list = []
        self.sort_by_name_desc = True
        self.sort_by_size_desc = True
        self.sort_by_time_desc = True
        self.set_drop_state(False)
        self.back_btn.config(state=tk.DISABLED)
        self.new_folder_btn.config(state=tk.DISABLED)

        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)
