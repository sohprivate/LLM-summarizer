"""Database management for efficient file tracking."""
import sqlite3
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import json
from loguru import logger
from contextlib import contextmanager


class FileTrackingDatabase:
    """SQLite-based file tracking system."""
    
    def __init__(self, db_path: Path = Path("processed_files.db")):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize database schema."""
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS processed_files (
                    file_id TEXT PRIMARY KEY,
                    file_name TEXT NOT NULL,
                    processed_at TIMESTAMP NOT NULL,
                    notion_page_id TEXT,
                    status TEXT NOT NULL,
                    error_message TEXT,
                    metadata TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS processing_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    details TEXT,
                    FOREIGN KEY (file_id) REFERENCES processed_files (file_id)
                )
            """)
            
            # Create indexes for better performance
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_processed_at 
                ON processed_files (processed_at)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_status 
                ON processed_files (status)
            """)
            
            conn.commit()
    
    @contextmanager
    def _get_connection(self):
        """Get database connection with proper error handling."""
        conn = None
        try:
            conn = sqlite3.connect(
                self.db_path,
                detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
            )
            conn.row_factory = sqlite3.Row
            yield conn
        finally:
            if conn:
                conn.close()
    
    def is_processed(self, file_id: str) -> bool:
        """Check if a file has been processed."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT 1 FROM processed_files WHERE file_id = ? AND status = 'completed'",
                (file_id,)
            )
            return cursor.fetchone() is not None
    
    def mark_as_processed(
        self,
        file_id: str,
        file_name: str,
        notion_page_id: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> None:
        """Mark a file as successfully processed."""
        with self._get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO processed_files 
                (file_id, file_name, processed_at, notion_page_id, status, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                file_id,
                file_name,
                datetime.now(),
                notion_page_id,
                'completed',
                json.dumps(metadata) if metadata else None
            ))
            
            self._add_history(conn, file_id, 'processed', {'notion_page_id': notion_page_id})
            conn.commit()
            
        logger.info(f"Marked file {file_id} as processed")
    
    def mark_as_failed(
        self,
        file_id: str,
        file_name: str,
        error_message: str
    ) -> None:
        """Mark a file as failed to process."""
        with self._get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO processed_files 
                (file_id, file_name, processed_at, status, error_message)
                VALUES (?, ?, ?, ?, ?)
            """, (
                file_id,
                file_name,
                datetime.now(),
                'failed',
                error_message
            ))
            
            self._add_history(conn, file_id, 'failed', {'error': error_message})
            conn.commit()
            
        logger.warning(f"Marked file {file_id} as failed: {error_message}")
    
    def get_failed_files(self, retry_after_hours: int = 24) -> List[Dict]:
        """Get files that failed processing and are ready for retry."""
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT file_id, file_name, error_message, processed_at
                FROM processed_files
                WHERE status = 'failed'
                AND datetime(processed_at, '+' || ? || ' hours') <= datetime('now')
                ORDER BY processed_at ASC
            """, (retry_after_hours,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_processing_stats(self) -> Dict[str, int]:
        """Get processing statistics."""
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT 
                    status,
                    COUNT(*) as count
                FROM processed_files
                GROUP BY status
            """)
            
            stats = {row['status']: row['count'] for row in cursor.fetchall()}
            
            # Add time-based stats
            cursor = conn.execute("""
                SELECT 
                    COUNT(*) as last_24h
                FROM processed_files
                WHERE processed_at >= datetime('now', '-1 day')
            """)
            
            stats['last_24h'] = cursor.fetchone()['last_24h']
            
            return stats
    
    def _add_history(self, conn: sqlite3.Connection, file_id: str, action: str, details: Optional[Dict] = None):
        """Add entry to processing history."""
        conn.execute("""
            INSERT INTO processing_history (file_id, action, timestamp, details)
            VALUES (?, ?, ?, ?)
        """, (
            file_id,
            action,
            datetime.now(),
            json.dumps(details) if details else None
        ))
    
    def cleanup_old_records(self, days_to_keep: int = 30) -> int:
        """Clean up old processing records."""
        with self._get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM processing_history
                WHERE timestamp < datetime('now', '-' || ? || ' days')
            """, (days_to_keep,))
            
            deleted_count = cursor.rowcount
            conn.commit()
            
            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} old history records")
            
            return deleted_count
    
    def migrate_from_text_file(self, text_file_path: Path) -> int:
        """Migrate from old text-based tracking to database."""
        if not text_file_path.exists():
            return 0
        
        migrated_count = 0
        with open(text_file_path, 'r') as f:
            for line in f:
                file_id = line.strip()
                if file_id:
                    self.mark_as_processed(
                        file_id=file_id,
                        file_name=f"Migrated file {file_id}",
                        metadata={'migrated': True}
                    )
                    migrated_count += 1
        
        logger.info(f"Migrated {migrated_count} file records from text file")
        return migrated_count