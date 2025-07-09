"""Logging configuration."""
import sys
from loguru import logger
from config.settings import settings

# Remove default logger
logger.remove()

# Add console handler
logger.add(
    sys.stderr,
    level=settings.LOG_LEVEL,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)

# Add file handler
logger.add(
    f"{settings.LOGS_DIR}/paperpile-to-notion.log",
    rotation="1 day",
    retention="7 days",
    level=settings.LOG_LEVEL,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
)