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
            # Log the prompt for debugging
            logger.debug(f"Sending prompt to Gemini: {prompt[:500]}...")
            
            # Generate response
            response = self.model.generate_content(prompt)
            
            # Parse JSON response
            result_text = response.text.strip()
            logger.debug(f"Gemini response: {result_text[:500]}...")
            # Remove markdown code blocks if present
            if result_text.startswith("```json"):
                result_text = result_text[7:]
            if result_text.endswith("```"):
                result_text = result_text[:-3]
            
            metadata = json.loads(result_text.strip())
            
            # Validate required fields
            required_fields = ['title', 'authors', 'journal', 'year', 'impact_factor', 'background', 
                             'target_population', 'study_design', 'methods', 'statistical_methods', 
                             'results', 'discussion', 'limitations', 'conclusion', 'strengths', 
                             'abstract', 'keywords', 'research_field']
            for field in required_fields:
                if field not in metadata:
                    if field in ['authors', 'keywords']:
                        metadata[field] = []
                    elif field in ['year', 'impact_factor']:
                        metadata[field] = 0
                    else:
                        metadata[field] = '不明'
            
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
あなたは学術論文の分析に精通した専門家です。以下の論文テキストを分析し、重要なメタデータを抽出してください。

以下の構造のJSONオブジェクトのみを返してください（追加のテキストや説明は不要です）：
{{
    "title": "論文の完全なタイトル",
    "authors": ["著者1", "著者2", ...],
    "journal": "ジャーナルまたは会議名",
    "year": 2024,
    "impact_factor": 0.0,
    "background": "研究の背景と動機を日本語で詳細に記述（なぜこの研究が必要か、既存研究の問題点など）",
    "target_population": "研究の対象集団を日本語で記述（サンプルサイズ、選択基準、人口統計学的特徴など）",
    "study_design": "研究デザインを日本語で記述（前向き/後ろ向き、観察研究/介入研究、ランダム化比較試験など）",
    "methods": "研究方法を日本語で詳細に記述（データ収集方法、測定手法、実験手順など）",
    "statistical_methods": "使用した統計手法を日本語で記述（検定方法、有意水準、多重比較補正など）",
    "results": "主要な結果を日本語で詳細に記述（具体的な数値、統計的有意性、効果量など）",
    "discussion": "考察を日本語で記述（結果の解釈、既存研究との比較、臨床的意義など）",
    "limitations": "研究の限界を日本語で記述（サンプルサイズ、バイアス、一般化可能性など）",
    "conclusion": "結論を日本語で簡潔に記述（主要な発見と今後の展望）",
    "strengths": "研究の強みを日本語で記述（新規性、方法論的優位性、実用性など）",
    "abstract": "論文のアブストラクト全文を日本語で",
    "keywords": ["日本語のキーワード1", "日本語のキーワード2", ...],
    "research_field": "主要な研究分野/学問領域を日本語で"
}}

フィールドが見つからない場合は、文字列には「不明」、配列には[]、数値には0を使用してください。
impact_factorが論文中に記載されていない場合は0としてください。
すべてのフィールドの値は日本語で記述してください。

論文テキスト:
{text[:10000]}  # Limit to avoid token limits
"""
    
    def get_quick_summary(self, pdf_path: str) -> Optional[str]:
        """Get a quick summary of the paper."""
        text = extract_text_from_pdf(pdf_path, max_pages=3)
        if not text:
            return None
        
        prompt = f"""
この学術論文について、以下の点を含めて詳細な要約を日本語で提供してください（8-10文程度）：

1. 研究の背景と問題意識
2. 研究目的と研究課題
3. 使用された主要な手法・アプローチ
4. 重要な発見や結果（具体的な数値があれば含める）
5. 研究の意義と貢献
6. 実践的な応用可能性

論文テキスト:
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