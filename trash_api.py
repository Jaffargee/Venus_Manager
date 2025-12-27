"""
Trash API for Venus File Manager
Handles file deletion and trash management
"""

import os
import sys
import shutil
import json
import time
from pathlib import Path
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class TrashAPI:
    """API for trash/recycle bin operations"""

    def __init__(self):
        self.platform = sys.platform
        self.trash_path = self._get_trash_path()
        self.info_path = os.path.join(self.trash_path, "info")
        self.files_path = os.path.join(self.trash_path, "files")

        # Ensure trash directories exist
        os.makedirs(self.info_path, exist_ok=True)
        os.makedirs(self.files_path, exist_ok=True)

    def _get_trash_path(self) -> str:
        """Get platform-specific trash path"""
        if self.platform == "win32":
            # Use a simple trash directory for Windows
            import getpass
            return f"C:/Users/{getpass.getuser()}/.venus_trash"
        else:
            # Linux/FreeDesktop trash spec
            import getpass
            return f"/home/{getpass.getuser()}/.local/share/Trash"

    def get_trash_path(self) -> str:
        """Get the trash directory path"""
        return self.trash_path

    def move_to_trash(self, file_path: str) -> bool:
        """Move a file to trash"""
        try:
            filename = os.path.basename(file_path)
            trash_file_path = self._get_unique_trash_path(filename)

            # Move the file
            shutil.move(file_path, trash_file_path)

            # Create trash info file
            info_file = os.path.join(self.info_path, f"{os.path.basename(trash_file_path)}.trashinfo")
            self._create_trash_info(info_file, file_path, trash_file_path)

            logger.info(f"Moved to trash: {file_path} -> {trash_file_path}")
            return True

        except (OSError, shutil.Error) as e:
            logger.error(f"Error moving to trash: {file_path} - {e}")
            return False

    def _get_unique_trash_path(self, filename: str) -> str:
        """Get a unique path in trash directory"""
        base_path = os.path.join(self.files_path, filename)
        if not os.path.exists(base_path):
            return base_path

        base, ext = os.path.splitext(filename)
        counter = 1
        while os.path.exists(os.path.join(self.files_path, f"{base}_{counter}{ext}")):
            counter += 1
        return os.path.join(self.files_path, f"{base}_{counter}{ext}")

    def _create_trash_info(self, info_path: str, original_path: str, trash_path: str):
        """Create .trashinfo file with metadata"""
        info_content = f"""[Trash Info]
Path={original_path}
DeletionDate={time.strftime('%Y-%m-%dT%H:%M:%S')}

"""
        with open(info_path, 'w') as f:
            f.write(info_content)

    def restore_from_trash(self, trash_filename: str) -> bool:
        """Restore a file from trash"""
        try:
            trash_file_path = os.path.join(self.files_path, trash_filename)
            info_file = os.path.join(self.info_path, f"{trash_filename}.trashinfo")

            # Read original path from info file
            original_path = None
            if os.path.exists(info_file):
                with open(info_file, 'r') as f:
                    for line in f:
                        if line.startswith('Path='):
                            original_path = line.split('=', 1)[1].strip()
                            break

            if not original_path:
                logger.error(f"Could not find original path for {trash_filename}")
                return False

            # Ensure destination directory exists
            os.makedirs(os.path.dirname(original_path), exist_ok=True)

            # Restore file
            shutil.move(trash_file_path, original_path)

            # Remove info file
            if os.path.exists(info_file):
                os.remove(info_file)

            logger.info(f"Restored from trash: {trash_file_path} -> {original_path}")
            return True

        except (OSError, shutil.Error) as e:
            logger.error(f"Error restoring from trash: {trash_filename} - {e}")
            return False

    def permanently_delete(self, trash_filename: str) -> bool:
        """Permanently delete a file from trash"""
        try:
            trash_file_path = os.path.join(self.files_path, trash_filename)
            info_file = os.path.join(self.info_path, f"{trash_filename}.trashinfo")

            # Delete the file
            if os.path.isdir(trash_file_path):
                shutil.rmtree(trash_file_path)
            else:
                os.remove(trash_file_path)

            # Delete info file
            if os.path.exists(info_file):
                os.remove(info_file)

            logger.info(f"Permanently deleted from trash: {trash_filename}")
            return True

        except OSError as e:
            logger.error(f"Error permanently deleting: {trash_filename} - {e}")
            return False

    def list_trash_contents(self) -> List[Dict]:
        """List all items in trash"""
        items = []
        try:
            for filename in os.listdir(self.files_path):
                file_path = os.path.join(self.files_path, filename)
                info_file = os.path.join(self.info_path, f"{filename}.trashinfo")

                item_info = {
                    'filename': filename,
                    'path': file_path,
                    'size': self._get_size(file_path),
                    'deleted_date': None,
                    'original_path': None
                }

                # Read info file if exists
                if os.path.exists(info_file):
                    with open(info_file, 'r') as f:
                        for line in f:
                            if line.startswith('DeletionDate='):
                                item_info['deleted_date'] = line.split('=', 1)[1].strip()
                            elif line.startswith('Path='):
                                item_info['original_path'] = line.split('=', 1)[1].strip()

                items.append(item_info)

        except OSError as e:
            logger.error(f"Error listing trash contents: {e}")

        return items

    def _get_size(self, path: str) -> int:
        """Get size of file or directory"""
        try:
            if os.path.isfile(path):
                return os.path.getsize(path)
            elif os.path.isdir(path):
                total = 0
                for root, dirs, files in os.walk(path):
                    for file in files:
                        try:
                            total += os.path.getsize(os.path.join(root, file))
                        except OSError:
                            pass
                return total
        except OSError:
            pass
        return 0

    def empty_trash(self) -> bool:
        """Empty the entire trash"""
        try:
            # Delete all files
            for filename in os.listdir(self.files_path):
                file_path = os.path.join(self.files_path, filename)
                if os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                else:
                    os.remove(file_path)

            # Delete all info files
            for filename in os.listdir(self.info_path):
                os.remove(os.path.join(self.info_path, filename))

            logger.info("Trash emptied")
            return True

        except OSError as e:
            logger.error(f"Error emptying trash: {e}")
            return False

    def get_trash_size(self) -> int:
        """Get total size of trash contents"""
        total = 0
        for item in self.list_trash_contents():
            total += item['size']
        return total

# Global instance
trash_api = TrashAPI()
# <parameter name="filePath">c:\Users\Tahir General\Downloads\File-Manager\JSIIT-22-NDCS-0024 - JSIIT-22-NDCS-0025\trash_api.py