"""
Video Tag Manager Application
Refactored for better maintainability and separation of concerns
"""
import tkinter as tk
from tkinter import ttk


from utils.TagManage_utils import setup_styles
# Import our database manager
from DB.db_manager import DBManager
# Import language manager
from utils.language_manager import LanguageManager
from GUI.components.browser_tab import BrowseTab
from GUI.components.tag_management_tab import TagManagementTab

class VideoTagApp:
    """Main application class"""
    def __init__(self, root):
        self.root = root
        
        # Initialize language manager
        self.lang_manager = LanguageManager()
        
        self.root.title(self.lang_manager.get_text("app_title"))
        self.root.geometry("1200x700")
        self.root.minsize(800, 600)

        # Initialize database manager
        self.db_manager = DBManager()

        # Setup UI
        setup_styles()
        self.create_widgets()
        
    def create_widgets(self):
        """Create the main application widgets"""
        # Language selection frame at the top of the window - now right-aligned
        self.language_frame = ttk.Frame(self.root)
        self.language_frame.pack(fill=tk.X, padx=10, pady=(0, 0), anchor='e')
        
        # Create a container inside language_frame to hold the language items
        lang_container = ttk.Frame(self.language_frame)
        lang_container.pack(side=tk.RIGHT)
        
        ttk.Label(lang_container, text=self.lang_manager.get_text("language")).pack(side=tk.LEFT, padx=(0, 5))
        self.language_var = tk.StringVar(value=self.lang_manager.get_current_language())
        
        language_combo = ttk.Combobox(lang_container, textvariable=self.language_var, 
                                     values=["chinese", "English"], width=10, state="readonly")
        language_combo.pack(side=tk.LEFT)
        language_combo.bind("<<ComboboxSelected>>", self.change_language)
        
        # Add display labels for the languages
        ttk.Label(lang_container, text=" (").pack(side=tk.LEFT)
        ttk.Label(lang_container, text=self.lang_manager.get_text("chinese")).pack(side=tk.LEFT)
        ttk.Label(lang_container, text=" / ").pack(side=tk.LEFT)
        ttk.Label(lang_container, text=self.lang_manager.get_text("English")).pack(side=tk.LEFT)
        ttk.Label(lang_container, text=")").pack(side=tk.LEFT)
        
        # Create the main notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Initialize tabs with dependencies injected
        self.browse_tab = BrowseTab(self.root, self.lang_manager, self.db_manager, self.refresh_tags)
        self.tag_management_tab = TagManagementTab(self.root, self.lang_manager, self.db_manager, self.search_by_tag)
        
        # Add tabs to notebook
        self.notebook.add(self.browse_tab.get_tab(), text=self.lang_manager.get_text("browse_tab"))
        self.notebook.add(self.tag_management_tab.get_tab(), text=self.lang_manager.get_text("tag_management_tab"))
        
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
        self.notebook.tab(self.browse_tab.get_tab(), text=self.lang_manager.get_text("browse_tab"))
        self.notebook.tab(self.tag_management_tab.get_tab(), text=self.lang_manager.get_text("tag_management_tab"))
        
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
        
        # Update tabs with new language
        self.browse_tab.update_language(self.lang_manager)
        self.tag_management_tab.update_language(self.lang_manager)
        
    def refresh_tags(self):
        """Refresh tags in the tag management tab"""
        self.tag_management_tab.refresh_top_tags()
        
    def search_by_tag(self, tags):
        """Search videos by tag(s)"""
        # Switch to browse tab first
        self.notebook.select(self.browse_tab.get_tab())
        
        # Tell browse tab to perform the search
        result = self.browse_tab.search_videos_by_tag(tags)
        return result


# Main entry point (would be in your main.py file)
if __name__ == "__main__":
    root = tk.Tk()
    app = VideoTagApp(root)
    root.mainloop()