"""Test utilities and fixtures."""
import pytest
from pathlib import Path
import tempfile
import shutil
from unittest.mock import Mock, MagicMock
from typing import Dict, Any


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path)


@pytest.fixture
def mock_config():
    """Create mock configuration for testing."""
    from config.config_schema import ApplicationConfig, GoogleDriveConfig, GeminiConfig, NotionConfig
    
    config = Mock(spec=ApplicationConfig)
    config.google_drive = Mock(spec=GoogleDriveConfig)
    config.google_drive.folder_id = "test_folder_id"
    config.google_drive.credentials_path = Path("test_credentials.json")
    
    config.gemini = Mock(spec=GeminiConfig)
    config.gemini.api_key = "test_gemini_key"
    config.gemini.model_name = "gemini-1.5-flash"
    
    config.notion = Mock(spec=NotionConfig)
    config.notion.api_key = "test_notion_key"
    config.notion.database_id = "test_database_id"
    
    config.processing.batch_size = 5
    config.processing.max_workers = 3
    config.processing.cache_ttl_seconds = 3600
    
    return config


@pytest.fixture
def mock_google_drive_service():
    """Create mock Google Drive service."""
    service = MagicMock()
    
    # Mock files().list()
    service.files().list().execute.return_value = {
        'files': [
            {
                'id': 'file1',
                'name': 'Paper1.pdf',
                'createdTime': '2024-01-01T00:00:00Z',
                'modifiedTime': '2024-01-01T00:00:00Z',
                'size': '1000000'
            },
            {
                'id': 'file2',
                'name': 'Paper2.pdf',
                'createdTime': '2024-01-02T00:00:00Z',
                'modifiedTime': '2024-01-02T00:00:00Z',
                'size': '2000000'
            }
        ]
    }
    
    # Mock files().get_media()
    service.files().get_media().execute.return_value = b"PDF content"
    
    return service


@pytest.fixture
def sample_paper_metadata() -> Dict[str, Any]:
    """Sample paper metadata for testing."""
    return {
        'title': 'Test Paper: A Comprehensive Study',
        'authors': ['John Doe', 'Jane Smith'],
        'journal': 'Journal of Testing',
        'year': 2024,
        'abstract': 'This is a test abstract in Japanese. テスト要約です。',
        'keywords': ['testing', 'research', 'テスト'],
        'summary': 'This is a detailed summary of the paper in Japanese. この論文の詳細な要約です。',
        'methodology': 'Test methodology description',
        'key_findings': ['Finding 1', 'Finding 2'],
        'research_field': 'Computer Science',
        'limitations': 'Test limitations',
        'practical_implications': 'Test implications'
    }


@pytest.fixture
def mock_gemini_response(sample_paper_metadata):
    """Mock Gemini API response."""
    import json
    
    response = Mock()
    response.text = json.dumps(sample_paper_metadata)
    return response


class MockPDFProcessor:
    """Mock PDF processor for testing."""
    
    @staticmethod
    def extract_text_from_pdf(pdf_path: str, max_pages: int = 10) -> str:
        """Return mock PDF text."""
        return """
        Test Paper: A Comprehensive Study
        
        Authors: John Doe, Jane Smith
        Journal: Journal of Testing
        
        Abstract:
        This is a test abstract for unit testing purposes.
        It contains multiple lines and some technical content.
        
        Introduction:
        This paper presents a comprehensive study on testing...
        
        Methods:
        We used various testing methodologies...
        
        Results:
        Our findings show that...
        
        Conclusion:
        In conclusion, this test was successful.
        """