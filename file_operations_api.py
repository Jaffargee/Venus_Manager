"""
File Operations API for Venus File Manager
Handles all file and directory operations with proper error handling
"""

import os
import shutil
import sys
import getpass
from pathlib import Path
from typing import List, Optional, Dict, Any
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FileOperationsAPI:
    """API for file and directory operations"""

    def __init__(self):
        self.platform = sys.platform
        self.user_home = self._get_user_home()

    def _get_user_home(self) -> str:
        """Get the user's home directory cross-platform"""
        if self.platform == "win32":
            return f"C:/Users/{getpass.getuser()}"
        else:
            return f"/home/{getpass.getuser()}"

    def get_default_paths(self) -> Dict[str, str]:
        """Get default directory paths for sidebar"""
        base = self.user_home
        paths = {
            "Home": base,
            "Desktop": os.path.join(base, "Desktop"),
            "Documents": os.path.join(base, "Documents"),
            "Downloads": os.path.join(base, "Downloads"),
            "Music": os.path.join(base, "Music"),
            "Pictures": os.path.join(base, "Pictures"),
            "Videos": os.path.join(base, "Videos"),
        }

        if self.platform != "win32":
            paths["Trash"] = os.path.join(base, ".local/share/Trash/files")
        else:
            paths["Trash"] = os.path.join(base, ".Trash")

        return paths

    def list_directory(self, path: str) -> List[Dict[str, Any]]:
        """List contents of a directory"""
        try:
            items = []
            for item in os.listdir(path):
                full_path = os.path.join(path, item)
                stat_info = os.stat(full_path)
                items.append({
                    'name': item,
                    'path': full_path,
                    'is_dir': os.path.isdir(full_path),
                    'size': stat_info.st_size,
                    'modified': stat_info.st_mtime,
                    'type': 'directory' if os.path.isdir(full_path) else self._get_file_type(item)
                })
            return sorted(items, key=lambda x: (not x['is_dir'], x['name'].lower()))
        except (OSError, PermissionError) as e:
            logger.error(f"Error listing directory {path}: {e}")
            return []

    def _get_file_type(self, filename: str) -> str:
        """Get file type from extension"""
        ext = os.path.splitext(filename)[1].lower()
        types = {
            '.txt': 'text',
            '.py': 'python',
            '.js': 'javascript',
            '.html': 'html',
            '.css': 'css',
            '.jpg': 'image',
            '.png': 'image',
            '.pdf': 'pdf',
            '.zip': 'archive',
            '.mp3': 'audio',
            '.mp4': 'video'
        }
        return types.get(ext, 'file')

    def create_directory(self, path: str, name: str) -> bool:
        """Create a new directory"""
        try:
            full_path = os.path.join(path, name)
            os.makedirs(full_path, exist_ok=True)
            logger.info(f"Created directory: {full_path}")
            return True
        except (OSError, PermissionError) as e:
            logger.error(f"Error creating directory {full_path}: {e}")
            return False

    def create_file(self, path: str, name: str, content: str = "") -> bool:
        """Create a new file"""
        try:
            full_path = os.path.join(path, name)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"Created file: {full_path}")
            return True
        except (OSError, PermissionError, IOError) as e:
            logger.error(f"Error creating file {full_path}: {e}")
            return False

    def delete_items(self, paths: List[str], permanent: bool = False) -> Dict[str, bool]:
        """Delete files/directories"""
        results = {}
        for path in paths:
            try:
                if permanent:
                    if os.path.isdir(path):
                        shutil.rmtree(path)
                    else:
                        os.remove(path)
                    logger.info(f"Permanently deleted: {path}")
                else:
                    # Move to trash (simplified - in real implementation, use platform-specific trash)
                    trash_path = self.get_default_paths().get("Trash", "/tmp/trash")
                    os.makedirs(trash_path, exist_ok=True)
                    basename = os.path.basename(path)
                    dest = os.path.join(trash_path, basename)
                    if os.path.exists(dest):
                        dest = self._get_unique_name(dest)
                    shutil.move(path, dest)
                    logger.info(f"Moved to trash: {path} -> {dest}")
                results[path] = True
            except (OSError, PermissionError, shutil.Error) as e:
                logger.error(f"Error deleting {path}: {e}")
                results[path] = False
        return results

    def _get_unique_name(self, path: str) -> str:
        """Get a unique name if file exists"""
        base, ext = os.path.splitext(path)
        counter = 1
        while os.path.exists(f"{base}_{counter}{ext}"):
            counter += 1
        return f"{base}_{counter}{ext}"

    def copy_items(self, sources: List[str], destination: str) -> Dict[str, bool]:
        """Copy files/directories"""
        results = {}
        for src in sources:
            try:
                basename = os.path.basename(src)
                dest = os.path.join(destination, basename)
                if os.path.exists(dest):
                    dest = self._get_unique_name(dest)

                if os.path.isdir(src):
                    shutil.copytree(src, dest)
                else:
                    shutil.copy2(src, dest)
                logger.info(f"Copied: {src} -> {dest}")
                results[src] = True
            except (OSError, PermissionError, shutil.Error) as e:
                logger.error(f"Error copying {src}: {e}")
                results[src] = False
        return results

    def move_items(self, sources: List[str], destination: str) -> Dict[str, bool]:
        """Move files/directories"""
        results = {}
        for src in sources:
            try:
                basename = os.path.basename(src)
                dest = os.path.join(destination, basename)
                if os.path.exists(dest):
                    dest = self._get_unique_name(dest)

                shutil.move(src, dest)
                logger.info(f"Moved: {src} -> {dest}")
                results[src] = True
            except (OSError, PermissionError, shutil.Error) as e:
                logger.error(f"Error moving {src}: {e}")
                results[src] = False
        return results

    def rename_item(self, path: str, new_name: str) -> bool:
        """Rename a file/directory"""
        try:
            directory = os.path.dirname(path)
            new_path = os.path.join(directory, new_name)
            if os.path.exists(new_path):
                return False
            os.rename(path, new_path)
            logger.info(f"Renamed: {path} -> {new_path}")
            return True
        except (OSError, PermissionError) as e:
            logger.error(f"Error renaming {path}: {e}")
            return False

    def compress_items(self, sources: List[str], destination: str, archive_name: str) -> bool:
        """Compress files/directories into a zip archive"""
        try:
            archive_path = os.path.join(destination, f"{archive_name}.zip")
            with shutil.ZipFile(archive_path, 'w', shutil.ZIP_DEFLATED) as zipf:
                for src in sources:
                    if os.path.isdir(src):
                        for root, dirs, files in os.walk(src):
                            for file in files:
                                file_path = os.path.join(root, file)
                                arcname = os.path.relpath(file_path, os.path.dirname(src))
                                zipf.write(file_path, arcname)
                    else:
                        zipf.write(src, os.path.basename(src))
            logger.info(f"Created archive: {archive_path}")
            return True
        except (OSError, PermissionError, shutil.Error) as e:
            logger.error(f"Error creating archive: {e}")
            return False

    def get_item_info(self, path: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a file/directory"""
        try:
            stat_info = os.stat(path)
            return {
                'name': os.path.basename(path),
                'path': path,
                'size': stat_info.st_size,
                'modified': stat_info.st_mtime,
                'created': stat_info.st_ctime,
                'is_dir': os.path.isdir(path),
                'permissions': oct(stat_info.st_mode)[-3:],
                'type': 'directory' if os.path.isdir(path) else self._get_file_type(os.path.basename(path))
            }
        except (OSError, PermissionError) as e:
            logger.error(f"Error getting info for {path}: {e}")
            return None

    def search_files(self, directory: str, pattern: str, recursive: bool = True) -> List[str]:
        """Search for files matching a pattern"""
        matches = []
        try:
            if recursive:
                for root, dirs, files in os.walk(directory):
                    for file in files:
                        if pattern.lower() in file.lower():
                            matches.append(os.path.join(root, file))
            else:
                for item in os.listdir(directory):
                    if pattern.lower() in item.lower():
                        matches.append(os.path.join(directory, item))
        except (OSError, PermissionError) as e:
            logger.error(f"Error searching in {directory}: {e}")
        return matches

# Global instance
file_api = FileOperationsAPI()
# <parameter name="filePath">c:\Users\Tahir General\Downloads\File-Manager\JSIIT-22-NDCS-0024 - JSIIT-22-NDCS-0025\file_operations_api.py