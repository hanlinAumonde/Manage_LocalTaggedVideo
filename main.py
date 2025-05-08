
import os
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

def setup_mongodb():
    """Check and setup MongoDB connection"""
    try:
        # Try to connect to MongoDB
        client = pymongo.MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
        # Force a command to check the connection
        client.admin.command('ping')
        print("MongoDB connection successful.")
        return True
    except pymongo.errors.ServerSelectionTimeoutError:
        print("Error: Could not connect to MongoDB server.")
        print("Please make sure MongoDB is installed and running on localhost:27017.")
        return False
    except Exception as e:
        print(f"MongoDB error: {str(e)}")
        return False


def main():
    """Main entry point for the application"""
    # Check MongoDB connection
    if not setup_mongodb():
        tk.messagebox.showerror("Database Error",
                                "Could not connect to MongoDB.\n"
                                "Please ensure MongoDB is installed and running on localhost:27017.")
        return

    # Create main window
    root = TkinterDnD.Tk()
    root.title("Video Tag Manager")

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

    # Start main loop
    root.mainloop()


if __name__ == "__main__":
    main()