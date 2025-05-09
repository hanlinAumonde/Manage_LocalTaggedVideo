from tkinter import ttk


def get_size(element):
    """Get size from FileInfoItem for sorting"""
    return element.size


def get_time(element):
    """Get last modified time from FileInfoItem for sorting"""
    return element.lastModifyTime


def get_name(element):
    """Get name from FileInfoItem for sorting (case insensitive)"""
    return element.name.upper()


def get_list_sorted(res_list, index, asc):
    """Sort list of FileInfoItems by given attribute

    Args:
        res_list: List of FileInfoItem objects
        index: Attribute to sort by ('size', 'time', or 'name')
        asc: If True, sort in ascending order, else descending

    Returns:
        Sorted list of FileInfoItems
    """
    if index == "size":
        res_list.sort(key=get_size, reverse=not asc)
    elif index == "time":
        res_list.sort(key=get_time, reverse=asc)
    elif index == "name":
        res_list.sort(key=get_name, reverse=not asc)
    return res_list

def setup_styles():
    """Setup custom styles for a modern UI feel"""
    style = ttk.Style()

    # Configure the main theme - use 'clam' as base and customize
    style.theme_use('clam')

    # Configure modern colors
    bg_color = "#f5f5f5"
    accent_color = "#1976d2"
    text_color = "#333333"

    # Configure Treeview
    style.configure("Treeview", background=bg_color, foreground=text_color, rowheight=25)
    style.configure("Treeview.Heading", font=('Segoe UI', 10, 'bold'), background=accent_color, foreground="white")
    style.map("Treeview", background=[('selected', accent_color)])

    # Configure Notebook
    style.configure("TNotebook", background=bg_color)
    style.configure("TNotebook.Tab", font=('Segoe UI', 10), padding=[10, 5])
    style.map("TNotebook.Tab", background=[("selected", accent_color)], foreground=[("selected", "white")])

    # Configure Buttons
    style.configure("TButton", font=('Segoe UI', 10), background=accent_color, foreground="white")
    style.map("TButton", background=[('active', '#1565c0')])

    # Configure Frames
    style.configure("TFrame", background=bg_color)

    # Configure Labels
    style.configure("TLabel", font=('Segoe UI', 10), background=bg_color, foreground=text_color)

    # Configure special accent button
    style.configure("Accent.TButton", font=('Segoe UI', 10, 'bold'), background=accent_color, foreground="white")
    style.map("Accent.TButton", background=[('active', '#1565c0')])

    # Configure Entry fields
    style.configure("TEntry", font=('Segoe UI', 10))

def add_tag_to_entry(tag_var, new_tag):
    """Add a tag to the entry field"""
    current_tags = [t.strip() for t in tag_var.get().split(",") if t.strip()]

    # Add tag if not already in list
    if new_tag not in current_tags:
        current_tags.append(new_tag)

    tag_var.set(", ".join(current_tags))


def replace_current_tag(tag_var, new_tag):
    """Replace the current tag being typed with a suggestion"""
    text = tag_var.get()
    tags = [t.strip() for t in text.split(",")]

    # Replace the last tag
    if tags:
        tags[-1] = new_tag

    tag_var.set(", ".join(tags))