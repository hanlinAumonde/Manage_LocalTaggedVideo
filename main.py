import os
import subprocess
import sys
import tkinter as tk
from tkinter import messagebox

# Check for required libraries
try:
    from tkinterdnd2 import TkinterDnD
except ImportError:
    print("Error: tkinterdnd2 library is required. Install it using 'pip install tkinterdnd2'.")
    sys.exit(1)

try:
    import pymongo
except ImportError:
    print("Error: pymongo library is required. Install it using 'pip install pymongo'.")
    sys.exit(1)

# Import our custom modules
from GUI import VideoTagApp
from utils.language_manager import LanguageManager
from DB.setup_db import setup_mongodb
from DB.setup_db import on_close

def main():
    """Main entry point for the application"""
    connected, started_by_app = setup_mongodb()
    # Check MongoDB connection
    if not connected:
        tk.messagebox.showerror("Database Error",
                                "Could not connect to MongoDB.\n"
                                "Please ensure MongoDB is installed and running on localhost:27017.")
        return

    # Create main window
    root = TkinterDnD.Tk()
    
    # Initialize language manager for default app title
    lang_manager = LanguageManager()
    root.title(lang_manager.get_text("app_title"))

    # Set icon (if available)
    try:
        if os.path.exists("icon.ico"):
            root.iconbitmap("icon.ico")
    except:
        pass

    # Set window size and position
    window_width = 1200
    window_height = 700

    # Get screen dimensions
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Calculate position
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)

    # Position window
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    # Initialize application
    VideoTagApp(root)
    root.protocol("WM_DELETE_WINDOW", lambda: on_close(root, started_by_app))

    # Start main loop
    root.mainloop()


if __name__ == "__main__":
    main()