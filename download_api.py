"""
Download API for Venus File Manager
Handles file downloads from URLs with progress tracking
"""

import urllib.request
import urllib.error
import requests
import threading
import os
import time
from typing import Callable, Optional
import logging

logger = logging.getLogger(__name__)

class DownloadAPI:
    """API for downloading files from URLs"""

    def __init__(self):
        self.active_downloads = {}
        self.download_history = []

    def download_file(self, url: str, destination: str, filename: Optional[str] = None,
                     progress_callback: Optional[Callable] = None,
                     completion_callback: Optional[Callable] = None) -> str:
        """Download a file from URL to destination directory"""

        try:
            # Get filename from URL if not provided
            if not filename:
                filename = self._get_filename_from_url(url)

            # Ensure unique filename
            filepath = os.path.join(destination, filename)
            filepath = self._get_unique_filepath(filepath)

            # Start download in background thread
            download_id = f"{url}_{int(time.time())}"
            self.active_downloads[download_id] = {
                'url': url,
                'filepath': filepath,
                'progress': 0,
                'status': 'starting',
                'thread': None
            }

            def download_worker():
                try:
                    self.active_downloads[download_id]['status'] = 'downloading'

                    # Use requests for better progress tracking
                    response = requests.get(url, stream=True)
                    response.raise_for_status()

                    total_size = int(response.headers.get('content-length', 0))
                    downloaded = 0

                    with open(filepath, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                                downloaded += len(chunk)

                                if total_size > 0:
                                    progress = int((downloaded / total_size) * 100)
                                    self.active_downloads[download_id]['progress'] = progress

                                    if progress_callback:
                                        progress_callback(download_id, progress)

                    self.active_downloads[download_id]['status'] = 'completed'
                    self.download_history.append({
                        'url': url,
                        'filepath': filepath,
                        'size': downloaded,
                        'timestamp': time.time()
                    })

                    if completion_callback:
                        completion_callback(download_id, True, filepath)

                    logger.info(f"Download completed: {url} -> {filepath}")

                except Exception as e:
                    self.active_downloads[download_id]['status'] = 'failed'
                    if completion_callback:
                        completion_callback(download_id, False, str(e))
                    logger.error(f"Download failed: {url} - {e}")

            thread = threading.Thread(target=download_worker, daemon=True)
            self.active_downloads[download_id]['thread'] = thread
            thread.start()

            return download_id

        except Exception as e:
            logger.error(f"Error starting download: {url} - {e}")
            return None

    def _get_filename_from_url(self, url: str) -> str:
        """Extract filename from URL"""
        from urllib.parse import urlparse, unquote
        parsed = urlparse(url)
        filename = os.path.basename(unquote(parsed.path))
        if not filename:
            filename = f"download_{int(time.time())}"
        return filename

    def _get_unique_filepath(self, filepath: str) -> str:
        """Get a unique filepath if file already exists"""
        if not os.path.exists(filepath):
            return filepath

        base, ext = os.path.splitext(filepath)
        counter = 1
        while os.path.exists(f"{base}_{counter}{ext}"):
            counter += 1
        return f"{base}_{counter}{ext}"

    def cancel_download(self, download_id: str) -> bool:
        """Cancel an active download"""
        if download_id in self.active_downloads:
            # Note: requests doesn't have built-in cancellation, this is simplified
            self.active_downloads[download_id]['status'] = 'cancelled'
            logger.info(f"Download cancelled: {download_id}")
            return True
        return False

    def get_download_status(self, download_id: str) -> Optional[dict]:
        """Get status of a download"""
        return self.active_downloads.get(download_id)

    def get_active_downloads(self) -> dict:
        """Get all active downloads"""
        return self.active_downloads

    def get_download_history(self) -> list:
        """Get download history"""
        return self.download_history

    def clear_history(self):
        """Clear download history"""
        self.download_history.clear()

    def validate_url(self, url: str) -> bool:
        """Validate if URL is accessible"""
        try:
            response = requests.head(url, timeout=10)
            return response.status_code == 200
        except:
            return False

# Global instance
download_api = DownloadAPI()
# <parameter name="filePath">c:\Users\Tahir General\Downloads\File-Manager\JSIIT-22-NDCS-0024 - JSIIT-22-NDCS-0025\download_api.py