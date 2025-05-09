import os
import time
from pymongo import MongoClient
from typing import List, Dict, Any, Optional, Tuple

# Define video file extensions
VIDEO_EXTENSIONS = ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.3gp', '.mpeg', '.mpg']


class FileInfoItem:
    def __init__(self, name: str, fullPath: str, size: float, lastModifyTime: float,
                 isDir: bool = False, tags: List[str] = None):
        self.name = name
        self.path = fullPath
        self.size = size
        self.lastModifyTime = lastModifyTime
        self.isDir = isDir
        self.tags = tags if tags else []

    def getDateFormatted(self) -> str:
        time_obj = time.localtime(self.lastModifyTime)
        return time.strftime("%Y/%m/%d %H:%M", time_obj)

    def getSizeConverted(self):
        # Define unit conversion
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        size = float(self.size)
        unit_index = 0

        # When file is larger than 1024 bytes, convert to next unit
        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1

        # Keep two decimal places
        return f"{size:.2f} {units[unit_index]}"

    def to_dict(self) -> Dict:
        """Convert object to dictionary for MongoDB storage"""
        return {
            "name": self.name,
            "path": self.path,
            "size": self.size,
            "lastModifyTime": self.lastModifyTime,
            "isDir": self.isDir,
            "tags": self.tags
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'FileInfoItem':
        """Create object from dictionary"""
        return cls(
            name=data["name"],
            fullPath=data["path"],
            size=data["size"],
            lastModifyTime=data["lastModifyTime"],
            isDir=data["isDir"],
            tags=data.get("tags", [])
        )


class DBManager:
    def __init__(self, db_url: str = "mongodb://localhost:27017/"):
        self.client = MongoClient(db_url)
        self.db = self.client["video_tag_db"]
        # Collection for tags
        self.tags_collection = self.db["tags"]
        # Collection for video files
        self.videos_collection = self.db["videos"]

        # Ensure indexes for faster queries
        self.videos_collection.create_index("path", unique=True)
        self.tags_collection.create_index("name", unique=True)

    def is_video_file(self, filepath: str) -> bool:
        """Check if file is a video file based on extension"""
        _, ext = os.path.splitext(filepath.lower())
        return ext in VIDEO_EXTENSIONS

    def get_top_tags(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Return the top N most used tags"""
        return list(self.tags_collection.find().sort("count", -1).limit(limit))

    def search_similar_tags(self, query: str, limit: int = 10) -> List[str]:
        """Find tags that match or are similar to the query
        
        Args:
            query: Text to search for in tags
            limit: Maximum number of suggestions to return (default: 10)
        
        Returns:
            List of tag names that match the query
        """
        if not query:
            # If query is empty, just return top tags
            top_tags = self.get_top_tags(limit)
            return [tag["name"] for tag in top_tags]
        
        # First, look for tags that start with the query (higher priority)
        prefix_pattern = f"^{query}"
        prefix_matches = list(self.tags_collection.find(
            {"name": {"$regex": prefix_pattern, "$options": "i"}},
            {"name": 1, "_id": 0}
        ).sort("count", -1).limit(limit))

        prefix_match_names = [tag["name"] for tag in prefix_matches]
        
        # If we haven't reached the limit, look for tags that contain the query anywhere
        remaining_slots = limit - len(prefix_match_names)
        if remaining_slots > 0:
            contains_pattern = f".*{query}.*"
            contains_matches = list(self.tags_collection.find(
                {"name": {"$regex": contains_pattern, "$options": "si", "$nin": prefix_match_names}},  # Exclude tags we already found
                {"name": 1, "_id": 0}
            ).sort("count", -1).limit(remaining_slots))
            
            # Combine both lists - prefix matches first, then contains matches
            prefix_match_names.extend([tag["name"] for tag in contains_matches])
        
        return prefix_match_names

    def add_or_update_tags(self, file_path: str, tags: List[str], append: bool = True) -> None:
        """Add tags to a video file, update tag counts, and store file info

        Args:
            file_path: Path to the video file
            tags: List of tags to add
            append: If True, append new tags to existing ones; if False, replace existing tags
        """
        # Normalize file path for consistency
        file_path = os.path.normpath(file_path).replace("\\", "/")

        # Check if file exists in the filesystem
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Get file information
        file_stat = os.stat(file_path)
        file_name = os.path.basename(file_path)

        # Get existing document if it exists
        existing_doc = self.videos_collection.find_one({"path": file_path})
        existing_tags = existing_doc.get("tags", []) if existing_doc else []

        # Determine final tags list (either append or replace)
        if append and existing_tags:
            # Combine existing and new tags, removing duplicates
            final_tags = list(set(existing_tags + tags))
        else:
            # Use only new tags
            final_tags = tags

        # Create or update the file document
        file_doc = {
            "name": file_name,
            "path": file_path,
            "size": file_stat.st_size,
            "lastModifyTime": file_stat.st_mtime,
            "isDir": False,
            "tags": final_tags
        }

        # Update the videos collection (upsert means insert if not exists, update if exists)
        self.videos_collection.update_one(
            {"path": file_path},
            {"$set": file_doc},
            upsert=True
        )

        # Update tag counts in the tags collection for newly added tags
        new_tags = [tag for tag in tags if tag not in existing_tags]
        for tag in new_tags:
            self.tags_collection.update_one(
                {"name": tag},
                {"$inc": {"count": 1}, "$setOnInsert": {"name": tag}},
                upsert=True
            )

        # If we're replacing tags, find and decrease count for tags that were removed
        if not append and existing_tags:
            removed_tags = [tag for tag in existing_tags if tag not in tags]
            for tag in removed_tags:
                self.tags_collection.update_one(
                    {"name": tag},
                    {"$inc": {"count": -1}}
                )
                # Remove tags with count <= 0
                self.tags_collection.delete_many({"count": {"$lte": 0}})

    def get_path_standard_format(self, path: str) -> str:
        """Standardize path format"""
        return os.path.normpath(path).replace("\\", "/")

    def get_total_size_and_latest_mod_time(self, folder_path: str) -> Tuple[float, float]:
        """Calculate total size and latest modified time for video files in a directory"""
        total_size = 0.0
        latest_mod_time = 0.0

        try:
            with os.scandir(folder_path) as entries:
                for entry in entries:
                    if entry.is_dir():
                        # Recursively check subdirectories
                        sub_size, sub_time = self.get_total_size_and_latest_mod_time(
                            self.get_path_standard_format(entry.path)
                        )
                        total_size += sub_size
                        latest_mod_time = max(latest_mod_time, sub_time)
                    elif self.is_video_file(entry.name):
                        # Process only video files
                        try:
                            file_info = entry.stat()
                            total_size += file_info.st_size
                            latest_mod_time = max(latest_mod_time, file_info.st_mtime)
                        except OSError as e:
                            print(f"Error getting file info: {e}, filename: {entry.name}, path: {entry.path}")
        except OSError as e:
            print(f"Error scanning directory: {e}, path: {folder_path}")

        # If no videos found, use the folder's modification time
        if latest_mod_time == 0.0:
            try:
                latest_mod_time = os.stat(folder_path).st_mtime
            except OSError:
                pass

        return total_size, latest_mod_time

    def get_calculated_list(self, current_path: str) -> List[FileInfoItem]:
        """Get list of directories and video files with their information"""
        result_list = []
        current_path = self.get_path_standard_format(current_path)

        try:
            with os.scandir(current_path) as entries:
                for entry in entries:
                    if entry.is_dir():
                        # Check if directory contains any videos (directly or in subdirectories)
                        size, mod_time = self.get_total_size_and_latest_mod_time(
                            self.get_path_standard_format(entry.path)
                        )

                        # Only include directories that contain videos
                        if size > 0:
                            result_list.append(FileInfoItem(
                                entry.name,
                                entry.path,
                                size,
                                mod_time,
                                True
                            ))
                    elif self.is_video_file(entry.name):
                        try:
                            file_info = entry.stat()
                            file_path = self.get_path_standard_format(entry.path)

                            # Check if this video exists in database and has tags
                            video_doc = self.videos_collection.find_one({"path": file_path})
                            tags = video_doc.get("tags", []) if video_doc else []

                            result_list.append(FileInfoItem(
                                entry.name,
                                file_path,
                                file_info.st_size,
                                file_info.st_mtime,
                                False,
                                tags
                            ))
                        except OSError as e:
                            print(f"Error getting file info: {e}, filename: {entry.name}, path: {entry.path}")
        except OSError as e:
            print(f"Error scanning directory: {e}, path: {current_path}")

        return result_list

    def find_videos_by_tag(self, tag: str) -> List[FileInfoItem]:
        """Find all videos that have the specified tag"""
        videos = []

        # Find all videos with this tag
        video_docs = self.videos_collection.find({"tags": tag})

        for doc in video_docs:
            # Verify the file still exists
            if os.path.exists(doc["path"]):
                videos.append(FileInfoItem.from_dict(doc))

        return videos

    def find_videos_by_tags(self, tags: List[str]) -> List[FileInfoItem]:
        """Find all videos that have all the specified tags (AND operation)

        Args:
            tags: List of tags that videos must all have

        Returns:
            List of FileInfoItem objects for videos with all specified tags
        """
        if not tags:
            return []

        # Create a query that finds documents containing all the specified tags
        query = {"tags": {"$all": tags}}
        
        # Find all videos matching the query
        video_docs = self.videos_collection.find(query)
        
        videos = []
        for doc in video_docs:
            # Verify the file still exists
            if os.path.exists(doc["path"]):
                videos.append(FileInfoItem.from_dict(doc))
                
        return videos

    def get_tags_for_file(self, file_path: str) -> List[str]:
        """Get all tags for a specific file"""
        file_path = self.get_path_standard_format(file_path)
        video_doc = self.videos_collection.find_one({"path": file_path})
        return video_doc.get("tags", []) if video_doc else []

    def remove_tags_from_file(self, file_path: str) -> None:
        """Remove a tag from a file and update tag counts"""
        file_path = self.get_path_standard_format(file_path)

        # Decrease the tag count
        for tag in self.get_tags_for_file(file_path):
            self.tags_collection.update_one(
                {"name": tag},
                {"$inc": {"count": -1}}
            )

        # Remove the video from the database
        self.videos_collection.delete_one({"path": file_path})

        # Remove tag if count reaches zero
        self.tags_collection.delete_many({"count": {"$lte": 0}})