"""Notion API client for paper database management."""
from typing import Dict, List, Optional
from datetime import datetime
from notion_client import Client
from loguru import logger
from config.settings import settings


class NotionPaperDatabase:
    """Manage paper entries in Notion database."""
    
    def __init__(self):
        self.client = Client(auth=settings.NOTION_API_KEY)
        self.database_id = settings.NOTION_DATABASE_ID
        
    def create_paper_entry(self, paper_data: Dict) -> Optional[str]:
        """Create a new paper entry in Notion database.
        
        Args:
            paper_data: Dictionary containing paper metadata
            
        Returns:
            Page ID if successful, None if error
        """
        try:
            # Prepare properties for Notion
            properties = self._prepare_properties(paper_data)
            
            # Create page
            response = self.client.pages.create(
                parent={"database_id": self.database_id},
                properties=properties,
                children=self._create_page_content(paper_data)
            )
            
            page_id = response["id"]
            logger.info(f"Created Notion page: {page_id}")
            return page_id
            
        except Exception as e:
            logger.error(f"Error creating Notion entry: {e}")
            return None
    
    def _prepare_properties(self, paper_data: Dict) -> Dict:
        """Prepare properties for Notion page."""
        properties = {
            "Title": {
                "title": [
                    {
                        "text": {
                            "content": paper_data.get("title", "Untitled Paper")[:2000]
                        }
                    }
                ]
            },
            "Authors": {
                "rich_text": [
                    {
                        "text": {
                            "content": ", ".join(paper_data.get("authors", []))[:2000]
                        }
                    }
                ]
            },
            "Journal ": {
                "rich_text": [
                    {
                        "text": {
                            "content": paper_data.get("journal", "Unknown")[:2000]
                        }
                    }
                ]
            },
            "Year": {
                "number": paper_data.get("year", 0)
            },
            "Added Date": {
                "date": {
                    "start": datetime.now().isoformat()
                }
            },
            "Research Field": {
                "select": {
                    "name": paper_data.get("research_field", "General").split(",")[0].strip()[:100]
                }
            },
            "Keywords ": {
                "multi_select": [
                    {"name": keyword[:100]} 
                    for keyword in paper_data.get("keywords", [])[:10]
                ]
            },
            "Summary ": {
                "rich_text": [
                    {
                        "text": {
                            "content": paper_data.get("summary", "")[:2000]
                        }
                    }
                ]
            },
            "Google Drive ID": {
                "rich_text": [
                    {
                        "text": {
                            "content": paper_data.get("drive_file_id", "")
                        }
                    }
                ]
            }
        }
        
        return properties
    
    def _create_page_content(self, paper_data: Dict) -> List[Dict]:
        """Create page content blocks."""
        blocks = []
        
        # Abstract section
        if paper_data.get("abstract"):
            blocks.extend([
                {
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [{"type": "text", "text": {"content": "概要"}}]
                    }
                },
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {"content": paper_data["abstract"][:2000]}
                            }
                        ]
                    }
                }
            ])
        
        # Methodology section
        if paper_data.get("methodology"):
            blocks.extend([
                {
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [{"type": "text", "text": {"content": "研究手法"}}]
                    }
                },
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {"content": paper_data["methodology"][:2000]}
                            }
                        ]
                    }
                }
            ])
        
        # Limitations section
        if paper_data.get("limitations"):
            blocks.extend([
                {
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [{"type": "text", "text": {"content": "研究の限界"}}]
                    }
                },
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {"content": paper_data["limitations"][:2000]}
                            }
                        ]
                    }
                }
            ])
        
        # Practical implications section
        if paper_data.get("practical_implications"):
            blocks.extend([
                {
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [{"type": "text", "text": {"content": "実践的意義"}}]
                    }
                },
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {"content": paper_data["practical_implications"][:2000]}
                            }
                        ]
                    }
                }
            ])
        
        # Key findings section
        if paper_data.get("key_findings"):
            blocks.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "主要な発見"}}]
                }
            })
            
            for finding in paper_data["key_findings"][:10]:
                blocks.append({
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {"content": finding[:2000]}
                            }
                        ]
                    }
                })
        
        # Google Drive link
        if paper_data.get("drive_file_id"):
            blocks.extend([
                {
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [{"type": "text", "text": {"content": "リンク"}}]
                    }
                },
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": "Google Driveで表示",
                                    "link": {
                                        "url": f"https://drive.google.com/file/d/{paper_data['drive_file_id']}/view"
                                    }
                                }
                            }
                        ]
                    }
                }
            ])
        
        return blocks
    
    def check_duplicate(self, title: str) -> bool:
        """Check if a paper with the same title already exists."""
        try:
            response = self.client.databases.query(
                database_id=self.database_id,
                filter={
                    "property": "Title",
                    "title": {
                        "equals": title
                    }
                }
            )
            
            return len(response["results"]) > 0
            
        except Exception as e:
            logger.error(f"Error checking for duplicates: {e}")
            return False
    
    def setup_database_properties(self):
        """Setup or verify database properties.
        
        This should be run once to ensure the database has the correct properties.
        Call this separately when setting up a new database.
        """
        try:
            # Get current database
            database = self.client.databases.retrieve(database_id=self.database_id)
            logger.info(f"Database '{database['title'][0]['text']['content']}' is accessible")
            
            # Log current properties
            logger.info("Current database properties:")
            for prop_name, prop_data in database["properties"].items():
                logger.info(f"  - {prop_name}: {prop_data['type']}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error accessing database: {e}")
            return False


if __name__ == "__main__":
    # Test connection
    client = NotionPaperDatabase()
    if client.setup_database_properties():
        print("Notion database connection successful!")
    else:
        print("Failed to connect to Notion database")