"""Application settings and configuration."""
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings."""
    
    # Google Drive
    GOOGLE_DRIVE_FOLDER_ID = os.getenv('GOOGLE_DRIVE_FOLDER_ID')
    GOOGLE_CREDENTIALS_PATH = os.getenv('GOOGLE_CREDENTIALS_PATH', 'credentials.json')
    
    # Gemini API
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    
    # Notion API
    NOTION_API_KEY = os.getenv('NOTION_API_KEY')
    NOTION_DATABASE_ID = os.getenv('NOTION_DATABASE_ID')
    
    # Application
    CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', '300'))  # 5 minutes default
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # Paths
    DOWNLOADS_DIR = 'downloads'
    LOGS_DIR = 'logs'
    
    @classmethod
    def validate(cls):
        """Validate required settings."""
        required = [
            ('GOOGLE_DRIVE_FOLDER_ID', cls.GOOGLE_DRIVE_FOLDER_ID),
            ('GEMINI_API_KEY', cls.GEMINI_API_KEY),
            ('NOTION_API_KEY', cls.NOTION_API_KEY),
            ('NOTION_DATABASE_ID', cls.NOTION_DATABASE_ID)
        ]
        
        missing = [name for name, value in required if not value]
        
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
        
        # Create directories
        os.makedirs(cls.DOWNLOADS_DIR, exist_ok=True)
        os.makedirs(cls.LOGS_DIR, exist_ok=True)


settings = Settings()