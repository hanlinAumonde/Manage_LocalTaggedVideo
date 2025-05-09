class LanguageManager:
    def __init__(self):
        """Initialize with Chinese and English translations"""
        self.current_language = "chinese"  # Default language
        
        # Define translations dictionary
        self.translations = {
            "chinese": {
                # Main UI
                "app_title": "视频标签管理器",
                "browse_tab": "文件浏览",
                "tag_management_tab": "标签管理",
                "directory": "目录:",
                "browse": "浏览",
                "back": "返回",
                "new_folder": "新建文件夹",
                "search": "搜索:",
                "search_in_currentDir": "在当前目录中搜索文件（夹）名",
                "search_btn": "搜索",
                "clear_search": "清除搜索",
                
                # File tree
                "type": "类型",
                "name": "名称",
                "size": "大小",
                "time": "修改时间",
                "tags": "标签",
                "folder": "文件夹",
                "video": "视频",
                
                # Tag operations
                "add_tags": "为选中文件添加标签",
                "remove_tags": "移除标签",
                
                # Top tags section
                "top_tags": "最多使用标签",
                "tag_name": "标签名称",
                "usage_count": "使用次数",
                "refresh": "刷新",
                
                # Search by tag section
                "search_by_tag": "按标签搜索:",
                
                # Dialog texts
                "folder_name": "文件夹名称:",
                "cancel": "取消",
                "create": "创建",
                "invalid_name": "无效名称",
                "enter_folder_name": "请输入文件夹名称。",
                "error": "错误",
                "create_folder_failed": "创建文件夹失败: ",
                "no_selection": "无选择",
                "select_files": "请选择要标记的文件。",
                "no_files": "无文件",
                "select_video_files": "请选择视频文件进行标记（不要选择文件夹）。",
                "add_tags_to": "添加标签到 {} 个文件",
                "file": "文件: ",
                "selected": "已选择: {} 个文件",
                "current_tags": "当前标签:",
                "keep_existing_tags": "保留现有标签 (添加新标签而不替换现有标签)",
                "enter_tags": "输入标签 (用逗号分隔):",
                "top_tags_click": "最多使用标签 (点击添加):",
                "tag_suggestions": "标签建议:",
                "save_tags": "保存标签",
                "missing_tag": "缺少标签",
                "enter_search_tag": "请输入要搜索的标签。",
                "no_results": "无结果",
                "no_videos_with_tag": "未找到带有标签 '{}' 的视频。",
                "tag_search_results": "标签搜索结果: {}",
                "multi_tag_search_hint": "输入多个标签以逗号分隔进行搜索",
                "multi_tag_search_results": "复合标签搜索结果: {}",
                "confirm_delete": "确认删除",
                "confirm_delete_msg": "您确定要删除这个{}吗?",
                "delete_failed": "删除失败: ",
                "confirm": "确认",
                "confirm_remove_tags": "确定要移除 {} 个文件的所有标签吗?",
                "remove_tags_failed": "移除标签失败: ",
                
                # Language
                "language": "语言:",
                "chinese": "中文",
                "English": "English"
            },
            "English": {
                # Main UI
                "app_title": "Video Tag Manager",
                "browse_tab": "Browse Files",
                "tag_management_tab": "Tag Management",
                "directory": "Directory:",
                "browse": "Browse",
                "back": "Back",
                "new_folder": "New Folder",
                "search": "Search:",
                "search_in_currentDir": "Search file (folder) names in current directory",
                "search_btn": "Search",
                "clear_search": "Clear Search",
                
                # File tree
                "type": "Type",
                "name": "Name",
                "size": "Size",
                "time": "Modified Time",
                "tags": "Tags",
                "folder": "Folder",
                "video": "Video",
                
                # Tag operations
                "add_tags": "Add Tags to Selected",
                "remove_tags": "Remove Tags",
                
                # Top tags section
                "top_tags": "Most Used Tags",
                "tag_name": "Tag Name",
                "usage_count": "Usage Count",
                "refresh": "Refresh",
                
                # Search by tag section
                "search_by_tag": "Search by Tag:",
                
                # Dialog texts
                "folder_name": "Folder Name:",
                "cancel": "Cancel",
                "create": "Create",
                "invalid_name": "Invalid Name",
                "enter_folder_name": "Please enter a folder name.",
                "error": "Error",
                "create_folder_failed": "Failed to create folder: ",
                "no_selection": "No Selection",
                "select_files": "Please select files to tag.",
                "no_files": "No Files",
                "select_video_files": "Please select video files to tag (not folders).",
                "add_tags_to": "Add Tags to {} Files",
                "file": "File: ",
                "selected": "Selected: {} files",
                "current_tags": "Current Tags:",
                "keep_existing_tags": "Keep existing tags (add new tags without replacing existing ones)",
                "enter_tags": "Enter tags (separated by commas):",
                "top_tags_click": "Top tags (click to add):",
                "tag_suggestions": "Tag suggestions:",
                "save_tags": "Save Tags",
                "missing_tag": "Missing Tag",
                "enter_search_tag": "Please enter a tag to search for.",
                "no_results": "No Results",
                "no_videos_with_tag": "No videos found with tag '{}'.",
                "tag_search_results": "Tag Search Results: {}",
                "multi_tag_search_hint": "Enter multiple tags separated by commas to search",
                "multi_tag_search_results": "Multi-Tag Search Results: {}",
                "confirm_delete": "Confirm Delete",
                "confirm_delete_msg": "Are you sure you want to delete this {}?",
                "delete_failed": "Delete failed: ",
                "confirm": "Confirm",
                "confirm_remove_tags": "Are you sure you want to remove all tags from {} files?",
                "remove_tags_failed": "Failed to remove tags: ",
                
                # Language
                "language": "Language:",
                "chinese": "中文",
                "English": "English"
            }
        }

    def get_text(self, key):
        """Get the translated text for a key in current language"""
        return self.translations.get(self.current_language, {}).get(key, key)
    
    def set_language(self, language):
        """Set the current language"""
        if language in self.translations:
            self.current_language = language
            return True
        return False
    
    def get_current_language(self):
        """Get current language code"""
        return self.current_language
