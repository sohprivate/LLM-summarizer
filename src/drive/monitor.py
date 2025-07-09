"""Google Drive file monitoring module."""
import os
import time
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional
from loguru import logger
from dotenv import load_dotenv
from .auth import authenticate

load_dotenv()


class DriveMonitor:
    """Monitor Google Drive folder for new PDF files."""
    
    def __init__(self):
        self.service = authenticate()
        self.folder_id = os.getenv('GOOGLE_DRIVE_FOLDER_ID')
        if not self.folder_id:
            raise ValueError("GOOGLE_DRIVE_FOLDER_ID not set in environment variables")
        
        self.last_check = datetime.now(timezone.utc) - timedelta(days=1)  # Start checking from 1 day ago
        self.processed_files = set()
        self._load_processed_files()
    
    def _load_processed_files(self):
        """Load list of already processed files."""
        processed_file_path = 'processed_files.txt'
        if os.path.exists(processed_file_path):
            with open(processed_file_path, 'r') as f:
                self.processed_files = set(line.strip() for line in f)
    
    def _save_processed_file(self, file_id: str):
        """Save processed file ID to prevent reprocessing."""
        self.processed_files.add(file_id)
        with open('processed_files.txt', 'a') as f:
            f.write(f"{file_id}\n")
    
    def get_new_pdfs(self) -> List[Dict]:
        """Get new PDF files from the monitored folder."""
        try:
            # Query for PDF files in the specific folder
            query = f"'{self.folder_id}' in parents and mimeType='application/pdf' and trashed=false"
            
            results = self.service.files().list(
                q=query,
                fields="nextPageToken, files(id, name, createdTime, modifiedTime, size)",
                orderBy="createdTime desc",
                pageSize=100
            ).execute()
            
            items = results.get('files', [])
            new_files = []
            
            for item in items:
                # Skip if already processed
                if item['id'] in self.processed_files:
                    continue
                
                # Check if file is new (created after last check)
                created_time = datetime.fromisoformat(item['createdTime'].replace('Z', '+00:00'))
                if created_time > self.last_check:
                    new_files.append(item)
                    logger.info(f"Found new PDF: {item['name']}")
            
            # Update last check time
            self.last_check = datetime.now(timezone.utc)
            
            return new_files
        
        except Exception as e:
            logger.error(f"Error getting new PDFs: {e}")
            return []
    
    def download_file(self, file_id: str, file_name: str) -> Optional[str]:
        """Download a file from Google Drive."""
        try:
            # Create downloads directory if it doesn't exist
            download_dir = 'downloads'
            os.makedirs(download_dir, exist_ok=True)
            
            # Clean filename
            safe_filename = "".join(c for c in file_name if c.isalnum() or c in (' ', '-', '_', '.')).rstrip()
            file_path = os.path.join(download_dir, safe_filename)
            
            # Download file
            request = self.service.files().get_media(fileId=file_id)
            with open(file_path, 'wb') as f:
                downloader = request.execute()
                f.write(downloader)
            
            logger.info(f"Downloaded file to: {file_path}")
            return file_path
        
        except Exception as e:
            logger.error(f"Error downloading file {file_name}: {e}")
            return None
    
    def mark_as_processed(self, file_id: str):
        """Mark a file as processed."""
        self._save_processed_file(file_id)
        logger.info(f"Marked file {file_id} as processed")


if __name__ == "__main__":
    # Test the monitor
    monitor = DriveMonitor()
    new_files = monitor.get_new_pdfs()
    
    print(f"Found {len(new_files)} new PDF files")
    for file in new_files:
        print(f"- {file['name']} (ID: {file['id']})")