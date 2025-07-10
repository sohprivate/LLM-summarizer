"""Refactored main application with improved architecture."""
import sys
import signal
from typing import Optional, List, Dict
from pathlib import Path
import argparse
from loguru import logger

# Import refactored components
from config.config_schema import ApplicationConfig
from src.utils.database import FileTrackingDatabase
from src.utils.async_processor import AsyncPaperProcessor, CacheManager
from src.utils.retry import CircuitBreaker, RateLimiter
from src.utils.security import SecureConfigManager

# Import original components (to be refactored later)
from src.drive.monitor import DriveMonitor
from src.gemini.analyzer import PaperAnalyzer
from src.notion.client import NotionPaperDatabase


class ImprovedPaperpileNotionSync:
    """Improved main application with better architecture."""
    
    def __init__(self, config: Optional[ApplicationConfig] = None):
        # Load configuration
        self.config = config or ApplicationConfig.from_env()
        self._setup_logging()
        
        # Initialize security manager
        self.security_manager = SecureConfigManager()
        
        # Initialize database
        self.db = FileTrackingDatabase()
        
        # Initialize cache
        self.cache = CacheManager(ttl_seconds=self.config.processing.cache_ttl_seconds)
        
        # Initialize rate limiters and circuit breakers
        self.rate_limiter = RateLimiter(self.config.processing.rate_limit_per_minute)
        self.drive_circuit = CircuitBreaker()
        self.gemini_circuit = CircuitBreaker()
        self.notion_circuit = CircuitBreaker()
        
        # Initialize async processor
        self.async_processor = AsyncPaperProcessor(max_workers=self.config.processing.max_workers)
        
        # Initialize service components
        self._init_services()
        
        # Setup signal handlers
        self._setup_signal_handlers()
        
        logger.info(f"Initialized {self.config.app_name} v{self.config.version}")
    
    def _setup_logging(self):
        """Configure enhanced logging."""
        logger.remove()  # Remove default handler
        
        # Console handler
        logger.add(
            sys.stdout,
            level=self.config.logging.level,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
        )
        
        # File handler with rotation
        logger.add(
            self.config.logging.log_dir / "paperpile-notion_{time}.log",
            level=self.config.logging.level,
            rotation=self.config.logging.max_file_size,
            retention=f"{self.config.logging.retention_days} days",
            compression="gz"
        )
        
        # Error file handler
        logger.add(
            self.config.logging.log_dir / "errors_{time}.log",
            level="ERROR",
            rotation="1 week",
            retention="1 month"
        )
    
    def _init_services(self):
        """Initialize service components with dependency injection."""
        # For now, use original implementations
        # TODO: Refactor these to accept config and dependencies
        self.drive_monitor = DriveMonitor()
        self.paper_analyzer = PaperAnalyzer()
        self.notion_db = NotionPaperDatabase()
    
    def _setup_signal_handlers(self):
        """Setup graceful shutdown handlers."""
        def signal_handler(sig, frame):
            logger.info(f"Received signal {sig}, shutting down gracefully...")
            self.shutdown()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def process_paper_improved(self, file_info: Dict) -> bool:
        """Improved paper processing with caching and better error handling."""
        file_id = file_info['id']
        file_name = file_info['name']
        
        # Check if already processed in database
        if self.db.is_processed(file_id):
            logger.debug(f"File {file_id} already processed, skipping")
            return True
        
        # Check cache for analysis results
        cache_key = f"analysis_{file_id}"
        cached_analysis = self.cache.get(cache_key)
        
        try:
            # Download PDF with circuit breaker
            pdf_path = self.drive_circuit.call(
                self.drive_monitor.download_file,
                file_id,
                file_name
            )
            
            if not pdf_path:
                raise ValueError(f"Failed to download {file_name}")
            
            # Analyze paper (use cache if available)
            if cached_analysis:
                paper_metadata = cached_analysis
                logger.info(f"Using cached analysis for {file_name}")
            else:
                with self.rate_limiter:
                    paper_metadata = self.gemini_circuit.call(
                        self.paper_analyzer.analyze_paper,
                        pdf_path
                    )
                
                if paper_metadata:
                    self.cache.set(cache_key, paper_metadata)
            
            if not paper_metadata:
                raise ValueError(f"Failed to analyze {file_name}")
            
            # Add Google Drive file ID
            paper_metadata['drive_file_id'] = file_id
            
            # Check for duplicates
            if self.notion_db.check_duplicate(paper_metadata.get('title', file_name)):
                logger.warning(f"Paper already exists in Notion: {paper_metadata.get('title')}")
                self.db.mark_as_processed(file_id, file_name, metadata={'duplicate': True})
                return True
            
            # Create Notion entry with circuit breaker
            with self.rate_limiter:
                page_id = self.notion_circuit.call(
                    self.notion_db.create_paper_entry,
                    paper_metadata
                )
            
            if not page_id:
                raise ValueError(f"Failed to create Notion entry for {file_name}")
            
            # Mark as processed in database
            self.db.mark_as_processed(
                file_id=file_id,
                file_name=file_name,
                notion_page_id=page_id,
                metadata=paper_metadata
            )
            
            logger.success(f"Successfully processed: {paper_metadata.get('title', file_name)}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing {file_name}: {e}")
            self.db.mark_as_failed(file_id, file_name, str(e))
            return False
    
    def run_once_improved(self):
        """Improved single run with parallel processing."""
        logger.info("Starting improved sync cycle...")
        
        # Get processing statistics
        stats = self.db.get_processing_stats()
        logger.info(f"Processing stats: {stats}")
        
        # Get new PDFs
        new_files = self.drive_monitor.get_new_pdfs()
        
        # Get failed files for retry
        failed_files = self.db.get_failed_files(retry_after_hours=24)
        
        all_files = new_files + failed_files
        
        if not all_files:
            logger.info("No files to process")
            return
        
        logger.info(f"Found {len(new_files)} new and {len(failed_files)} failed files to process")
        
        # Process files in parallel
        def progress_callback(completed: int, total: int):
            logger.info(f"Progress: {completed}/{total} files processed")
        
        results = self.async_processor.process_papers_batch(
            papers=all_files,
            process_func=self.process_paper_improved,
            progress_callback=progress_callback
        )
        
        # Summary
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful
        avg_time = sum(r.processing_time for r in results) / len(results) if results else 0
        
        logger.info(
            f"Sync cycle complete. Success: {successful}, Failed: {failed}, "
            f"Avg processing time: {avg_time:.2f}s"
        )
        
        # Cleanup
        self.cache.cleanup_expired()
        self.db.cleanup_old_records(days_to_keep=30)
    
    def run_continuous_improved(self):
        """Improved continuous monitoring with better error handling."""
        logger.info(
            f"Starting continuous monitoring (interval: {self.config.processing.check_interval}s)"
        )
        
        import time
        
        while True:
            try:
                self.run_once_improved()
                
                logger.info(
                    f"Waiting {self.config.processing.check_interval}s until next check..."
                )
                time.sleep(self.config.processing.check_interval)
                
            except KeyboardInterrupt:
                logger.info("Received interrupt, shutting down...")
                break
            except Exception as e:
                logger.error(f"Unexpected error in main loop: {e}")
                logger.info("Waiting 60s before retry...")
                time.sleep(60)
    
    def shutdown(self):
        """Graceful shutdown."""
        logger.info("Shutting down...")
        self.async_processor.shutdown()
        logger.info("Shutdown complete")


def main():
    """Enhanced main entry point."""
    parser = argparse.ArgumentParser(
        description="Sync papers from Paperpile to Notion with improved features"
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run once and exit"
    )
    parser.add_argument(
        "--migrate",
        action="store_true",
        help="Migrate from old processed_files.txt to database"
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show processing statistics and exit"
    )
    parser.add_argument(
        "--config-check",
        action="store_true",
        help="Validate configuration and exit"
    )
    
    args = parser.parse_args()
    
    # Load and validate configuration
    try:
        config = ApplicationConfig.from_env()
        config.validate_all()
    except Exception as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    
    if args.config_check:
        logger.success("Configuration is valid!")
        logger.info(f"Configuration: {config.to_dict(include_secrets=False)}")
        return
    
    # Initialize application
    app = ImprovedPaperpileNotionSync(config)
    
    if args.migrate:
        # Migrate from old text file
        old_file = Path("processed_files.txt")
        if old_file.exists():
            count = app.db.migrate_from_text_file(old_file)
            logger.success(f"Migration complete: {count} files migrated")
        else:
            logger.warning("No processed_files.txt found")
        return
    
    if args.stats:
        # Show statistics
        stats = app.db.get_processing_stats()
        logger.info("Processing Statistics:")
        for key, value in stats.items():
            logger.info(f"  {key}: {value}")
        return
    
    # Run the sync
    if args.once:
        app.run_once_improved()
    else:
        app.run_continuous_improved()


if __name__ == "__main__":
    main()