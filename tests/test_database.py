"""Tests for database functionality."""
import pytest
from datetime import datetime, timedelta
from pathlib import Path

from src.utils.database import FileTrackingDatabase


class TestFileTrackingDatabase:
    """Test FileTrackingDatabase class."""
    
    @pytest.fixture
    def db(self, temp_dir):
        """Create test database instance."""
        db_path = temp_dir / "test.db"
        return FileTrackingDatabase(db_path)
    
    def test_init_creates_tables(self, db):
        """Test that initialization creates required tables."""
        with db._get_connection() as conn:
            # Check tables exist
            cursor = conn.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name IN ('processed_files', 'processing_history')
            """)
            tables = [row['name'] for row in cursor.fetchall()]
            
            assert 'processed_files' in tables
            assert 'processing_history' in tables
    
    def test_mark_as_processed(self, db):
        """Test marking file as processed."""
        file_id = "test_file_1"
        file_name = "test.pdf"
        notion_page_id = "notion_123"
        metadata = {"title": "Test Paper"}
        
        # Mark as processed
        db.mark_as_processed(file_id, file_name, notion_page_id, metadata)
        
        # Verify it's marked as processed
        assert db.is_processed(file_id) is True
        
        # Check database content
        with db._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM processed_files WHERE file_id = ?",
                (file_id,)
            )
            row = cursor.fetchone()
            
            assert row['file_name'] == file_name
            assert row['notion_page_id'] == notion_page_id
            assert row['status'] == 'completed'
            assert row['metadata'] is not None
    
    def test_mark_as_failed(self, db):
        """Test marking file as failed."""
        file_id = "test_file_2"
        file_name = "failed.pdf"
        error_msg = "Test error message"
        
        # Mark as failed
        db.mark_as_failed(file_id, file_name, error_msg)
        
        # Verify it's not marked as processed
        assert db.is_processed(file_id) is False
        
        # Check database content
        with db._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM processed_files WHERE file_id = ?",
                (file_id,)
            )
            row = cursor.fetchone()
            
            assert row['status'] == 'failed'
            assert row['error_message'] == error_msg
    
    def test_get_failed_files(self, db):
        """Test retrieving failed files for retry."""
        # Add some failed files
        old_file = "old_failed"
        recent_file = "recent_failed"
        
        # Mark old file as failed (25 hours ago)
        with db._get_connection() as conn:
            old_time = datetime.now() - timedelta(hours=25)
            conn.execute("""
                INSERT INTO processed_files 
                (file_id, file_name, processed_at, status, error_message)
                VALUES (?, ?, ?, ?, ?)
            """, (old_file, "old.pdf", old_time, 'failed', 'Old error'))
            conn.commit()
        
        # Mark recent file as failed (1 hour ago)
        db.mark_as_failed(recent_file, "recent.pdf", "Recent error")
        
        # Get failed files ready for retry (after 24 hours)
        failed_files = db.get_failed_files(retry_after_hours=24)
        
        # Should only get the old file
        assert len(failed_files) == 1
        assert failed_files[0]['file_id'] == old_file
    
    def test_get_processing_stats(self, db):
        """Test getting processing statistics."""
        # Add various files
        db.mark_as_processed("file1", "file1.pdf")
        db.mark_as_processed("file2", "file2.pdf")
        db.mark_as_failed("file3", "file3.pdf", "Error")
        
        # Get stats
        stats = db.get_processing_stats()
        
        assert stats['completed'] == 2
        assert stats['failed'] == 1
        assert stats['last_24h'] == 3
    
    def test_cleanup_old_records(self, db):
        """Test cleaning up old records."""
        file_id = "test_file"
        
        # Add file with history
        db.mark_as_processed(file_id, "test.pdf")
        
        # Add old history entry manually
        with db._get_connection() as conn:
            old_time = datetime.now() - timedelta(days=40)
            conn.execute("""
                INSERT INTO processing_history (file_id, action, timestamp, details)
                VALUES (?, ?, ?, ?)
            """, (file_id, "old_action", old_time, "{}"))
            conn.commit()
        
        # Cleanup old records
        deleted = db.cleanup_old_records(days_to_keep=30)
        
        assert deleted == 1
    
    def test_migrate_from_text_file(self, db, temp_dir):
        """Test migration from text file."""
        # Create text file with file IDs
        text_file = temp_dir / "processed_files.txt"
        file_ids = ["file1", "file2", "file3"]
        
        with open(text_file, 'w') as f:
            for file_id in file_ids:
                f.write(f"{file_id}\n")
        
        # Migrate
        migrated = db.migrate_from_text_file(text_file)
        
        assert migrated == 3
        
        # Verify all files are marked as processed
        for file_id in file_ids:
            assert db.is_processed(file_id) is True