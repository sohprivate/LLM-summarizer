"""Configuration schema and validation using Pydantic."""
from typing import Optional, Dict, Any
from pathlib import Path
from pydantic import BaseSettings, Field, validator, SecretStr
import os


class GoogleDriveConfig(BaseSettings):
    """Google Drive configuration."""
    folder_id: str = Field(..., description="Google Drive folder ID to monitor")
    credentials_path: Path = Field(
        default=Path("credentials.json"),
        description="Path to Google credentials JSON file"
    )
    
    @validator('credentials_path')
    def validate_credentials_path(cls, v: Path) -> Path:
        if not v.exists():
            raise ValueError(f"Credentials file not found: {v}")
        return v


class GeminiConfig(BaseSettings):
    """Gemini API configuration."""
    api_key: SecretStr = Field(..., description="Gemini API key")
    model_name: str = Field(
        default="gemini-1.5-flash",
        description="Gemini model to use"
    )
    max_tokens: int = Field(
        default=10000,
        description="Maximum tokens to send to Gemini",
        ge=1000,
        le=30000
    )
    temperature: float = Field(
        default=0.7,
        description="Temperature for text generation",
        ge=0.0,
        le=1.0
    )


class NotionConfig(BaseSettings):
    """Notion API configuration."""
    api_key: SecretStr = Field(..., description="Notion API key")
    database_id: str = Field(..., description="Notion database ID")
    max_title_length: int = Field(
        default=2000,
        description="Maximum length for title field"
    )
    max_text_length: int = Field(
        default=2000,
        description="Maximum length for text fields"
    )


class ProcessingConfig(BaseSettings):
    """Processing configuration."""
    check_interval: int = Field(
        default=300,
        description="Check interval in seconds",
        ge=60,
        le=3600
    )
    batch_size: int = Field(
        default=5,
        description="Number of papers to process in parallel",
        ge=1,
        le=10
    )
    max_workers: int = Field(
        default=3,
        description="Maximum number of worker threads",
        ge=1,
        le=10
    )
    rate_limit_per_minute: int = Field(
        default=60,
        description="API calls per minute",
        ge=10,
        le=120
    )
    retry_max_attempts: int = Field(
        default=3,
        description="Maximum retry attempts for failed operations",
        ge=1,
        le=5
    )
    cache_ttl_seconds: int = Field(
        default=3600,
        description="Cache TTL in seconds",
        ge=300,
        le=86400
    )


class LoggingConfig(BaseSettings):
    """Logging configuration."""
    level: str = Field(
        default="INFO",
        description="Logging level"
    )
    log_dir: Path = Field(
        default=Path("logs"),
        description="Directory for log files"
    )
    max_file_size: str = Field(
        default="10MB",
        description="Maximum log file size"
    )
    retention_days: int = Field(
        default=7,
        description="Log retention in days",
        ge=1,
        le=30
    )
    
    @validator('level')
    def validate_log_level(cls, v: str) -> str:
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f"Invalid log level: {v}. Must be one of {valid_levels}")
        return v.upper()


class ApplicationConfig(BaseSettings):
    """Main application configuration."""
    google_drive: GoogleDriveConfig
    gemini: GeminiConfig
    notion: NotionConfig
    processing: ProcessingConfig = ProcessingConfig()
    logging: LoggingConfig = LoggingConfig()
    
    # Application metadata
    app_name: str = Field(default="Paperpile to Notion", description="Application name")
    version: str = Field(default="1.0.0", description="Application version")
    environment: str = Field(default="production", description="Environment")
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
    @classmethod
    def from_env(cls) -> 'ApplicationConfig':
        """Create configuration from environment variables."""
        return cls(
            google_drive=GoogleDriveConfig(
                folder_id=os.getenv('GOOGLE_DRIVE_FOLDER_ID'),
                credentials_path=Path(os.getenv('GOOGLE_CREDENTIALS_PATH', 'credentials.json'))
            ),
            gemini=GeminiConfig(
                api_key=os.getenv('GEMINI_API_KEY')
            ),
            notion=NotionConfig(
                api_key=os.getenv('NOTION_API_KEY'),
                database_id=os.getenv('NOTION_DATABASE_ID')
            ),
            processing=ProcessingConfig(
                check_interval=int(os.getenv('CHECK_INTERVAL', '300'))
            ),
            logging=LoggingConfig(
                level=os.getenv('LOG_LEVEL', 'INFO')
            )
        )
    
    def to_dict(self, include_secrets: bool = False) -> Dict[str, Any]:
        """Convert to dictionary, optionally excluding secrets."""
        data = self.dict()
        
        if not include_secrets:
            # Mask sensitive fields
            data['gemini']['api_key'] = '***'
            data['notion']['api_key'] = '***'
        
        return data
    
    def validate_all(self) -> None:
        """Validate all configuration sections."""
        # This will raise ValidationError if any field is invalid
        _ = self.dict()
        
        # Additional custom validations
        if self.processing.max_workers > self.processing.batch_size:
            raise ValueError(
                f"max_workers ({self.processing.max_workers}) cannot be greater than "
                f"batch_size ({self.processing.batch_size})"
            )