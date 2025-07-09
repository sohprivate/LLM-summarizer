"""Main application entry point."""
import time
import sys
from typing import Dict
from loguru import logger
from src.utils.logger import logger  # This imports configured logger
from config.settings import settings
from src.drive.monitor import DriveMonitor
from src.gemini.analyzer import PaperAnalyzer
from src.notion.client import NotionPaperDatabase


class PaperpileNotionSync:
    """Main application class for syncing papers from Paperpile to Notion."""
    
    def __init__(self):
        # Validate settings
        try:
            settings.validate()
        except ValueError as e:
            logger.error(f"Configuration error: {e}")
            sys.exit(1)
        
        # Initialize components
        self.drive_monitor = DriveMonitor()
        self.paper_analyzer = PaperAnalyzer()
        self.notion_db = NotionPaperDatabase()
        
        logger.info("Paperpile to Notion sync initialized")
    
    def process_paper(self, file_info: Dict) -> bool:
        """Process a single paper from Drive to Notion.
        
        Args:
            file_info: Dictionary with file information from Google Drive
            
        Returns:
            True if successful, False otherwise
        """
        file_id = file_info['id']
        file_name = file_info['name']
        
        logger.info(f"Processing paper: {file_name}")
        
        try:
            # Download PDF from Google Drive
            pdf_path = self.drive_monitor.download_file(file_id, file_name)
            if not pdf_path:
                logger.error(f"Failed to download {file_name}")
                return False
            
            # Analyze paper with Gemini
            logger.info(f"Analyzing paper with Gemini...")
            paper_metadata = self.paper_analyzer.analyze_paper(pdf_path)
            if not paper_metadata:
                logger.error(f"Failed to analyze {file_name}")
                return False
            
            # Add Google Drive file ID
            paper_metadata['drive_file_id'] = file_id
            
            # Check for duplicates in Notion
            if self.notion_db.check_duplicate(paper_metadata.get('title', file_name)):
                logger.warning(f"Paper already exists in Notion: {paper_metadata.get('title')}")
                # Still mark as processed to avoid re-checking
                self.drive_monitor.mark_as_processed(file_id)
                return True
            
            # Create Notion entry
            logger.info(f"Creating Notion entry...")
            page_id = self.notion_db.create_paper_entry(paper_metadata)
            if not page_id:
                logger.error(f"Failed to create Notion entry for {file_name}")
                return False
            
            # Mark as processed
            self.drive_monitor.mark_as_processed(file_id)
            
            logger.success(f"Successfully processed: {paper_metadata.get('title', file_name)}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing {file_name}: {e}")
            return False
    
    def run_once(self):
        """Run a single sync cycle."""
        logger.info("Starting sync cycle...")
        
        # Get new PDFs from Drive
        new_files = self.drive_monitor.get_new_pdfs()
        
        if not new_files:
            logger.info("No new papers found")
            return
        
        logger.info(f"Found {len(new_files)} new papers")
        
        # Process each paper
        success_count = 0
        for file_info in new_files:
            if self.process_paper(file_info):
                success_count += 1
            
            # Small delay between papers to avoid rate limits
            time.sleep(2)
        
        logger.info(f"Sync cycle complete. Processed {success_count}/{len(new_files)} papers successfully")
    
    def run_continuous(self):
        """Run continuous monitoring."""
        logger.info(f"Starting continuous monitoring (checking every {settings.CHECK_INTERVAL} seconds)")
        
        while True:
            try:
                self.run_once()
                
                # Wait for next cycle
                logger.info(f"Waiting {settings.CHECK_INTERVAL} seconds until next check...")
                time.sleep(settings.CHECK_INTERVAL)
                
            except KeyboardInterrupt:
                logger.info("Received interrupt signal, shutting down...")
                break
            except Exception as e:
                logger.error(f"Unexpected error in main loop: {e}")
                logger.info("Waiting 60 seconds before retrying...")
                time.sleep(60)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Sync papers from Paperpile to Notion")
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run once and exit (default is continuous monitoring)"
    )
    parser.add_argument(
        "--setup-notion",
        action="store_true",
        help="Check Notion database setup and exit"
    )
    
    args = parser.parse_args()
    
    if args.setup_notion:
        # Just check Notion setup
        notion_db = NotionPaperDatabase()
        if notion_db.setup_database_properties():
            logger.success("Notion database is properly configured!")
        else:
            logger.error("Failed to access Notion database. Check your configuration.")
        return
    
    # Run the sync
    sync = PaperpileNotionSync()
    
    if args.once:
        sync.run_once()
    else:
        sync.run_continuous()


if __name__ == "__main__":
    main()