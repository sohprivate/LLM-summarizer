"""Paper analysis using Gemini API."""
import json
from typing import Dict, Optional
import google.generativeai as genai
from loguru import logger
from config.settings import settings
from .pdf_processor import extract_text_from_pdf

# Configure Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)


class PaperAnalyzer:
    """Analyze academic papers using Gemini."""
    
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
    def analyze_paper(self, pdf_path: str) -> Optional[Dict]:
        """Analyze a paper and extract metadata.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary with paper metadata or None if error
        """
        # Extract text from PDF
        text = extract_text_from_pdf(pdf_path)
        if not text:
            logger.error(f"Failed to extract text from {pdf_path}")
            return None
        
        # Create prompt for Gemini
        prompt = self._create_analysis_prompt(text)
        
        try:
            # Generate response
            response = self.model.generate_content(prompt)
            
            # Parse JSON response
            result_text = response.text.strip()
            # Remove markdown code blocks if present
            if result_text.startswith("```json"):
                result_text = result_text[7:]
            if result_text.endswith("```"):
                result_text = result_text[:-3]
            
            metadata = json.loads(result_text.strip())
            
            # Validate required fields
            required_fields = ['title', 'authors', 'journal', 'year', 'abstract']
            for field in required_fields:
                if field not in metadata:
                    metadata[field] = 'Not found'
            
            logger.info(f"Successfully analyzed paper: {metadata.get('title', 'Unknown')}")
            return metadata
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini response as JSON: {e}")
            logger.debug(f"Response was: {response.text}")
            return None
        except Exception as e:
            logger.error(f"Error analyzing paper with Gemini: {e}")
            return None
    
    def _create_analysis_prompt(self, text: str) -> str:
        """Create prompt for paper analysis."""
        return f"""
You are an expert at analyzing academic papers. Please analyze the following paper text and extract key metadata.

Return ONLY a JSON object with the following structure (no additional text or explanation):
{{
    "title": "Full title of the paper",
    "authors": ["Author 1", "Author 2", ...],
    "journal": "Journal or conference name",
    "year": 2024,
    "abstract": "The paper's abstract",
    "keywords": ["keyword1", "keyword2", ...],
    "summary": "A 2-3 sentence summary of the paper's main contribution",
    "methodology": "Brief description of the methodology used",
    "key_findings": ["Finding 1", "Finding 2", ...],
    "research_field": "Primary research field/discipline"
}}

If any field cannot be found, use "Not found" for strings, [] for arrays, and 0 for numbers.

Paper text:
{text[:10000]}  # Limit to avoid token limits
"""
    
    def get_quick_summary(self, pdf_path: str) -> Optional[str]:
        """Get a quick summary of the paper."""
        text = extract_text_from_pdf(pdf_path, max_pages=3)
        if not text:
            return None
        
        prompt = f"""
Provide a concise 3-4 sentence summary of this academic paper, focusing on:
1. What problem it addresses
2. The main approach/method
3. Key findings or contributions

Paper text:
{text[:5000]}
"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Error generating quick summary: {e}")
            return None


if __name__ == "__main__":
    # Test the analyzer
    analyzer = PaperAnalyzer()
    # You can test with a sample PDF if you have one
    print("Paper analyzer initialized successfully")