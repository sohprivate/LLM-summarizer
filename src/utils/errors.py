"""Custom error classes and error handling utilities."""


class PaperpileNotionError(Exception):
    """Base exception for the application."""
    pass


class GoogleDriveError(PaperpileNotionError):
    """Error related to Google Drive operations."""
    pass


class GeminiAPIError(PaperpileNotionError):
    """Error related to Gemini API operations."""
    pass


class NotionAPIError(PaperpileNotionError):
    """Error related to Notion API operations."""
    pass


class ConfigurationError(PaperpileNotionError):
    """Error related to application configuration."""
    pass