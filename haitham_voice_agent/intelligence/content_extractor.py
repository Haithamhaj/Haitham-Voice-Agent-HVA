import logging
from pathlib import Path
import PyPDF2
from typing import Optional

logger = logging.getLogger(__name__)

class ContentExtractor:
    """
    Extracts raw text from various file formats.
    Supported: .txt, .md, .py, .js, .json, .html, .css, .pdf
    """
    
    def __init__(self):
        pass
        
    def extract_text(self, path: str, max_length: int = 100000) -> Optional[str]:
        """
        Extract text content from file.
        max_length: Max characters to return. If exceeded, returns Head + Tail.
        """
        file_path = Path(path)
        if not file_path.exists():
            logger.warning(f"File not found: {path}")
            return None
            
        ext = file_path.suffix.lower()
        
        try:
            content = None
            if ext == '.pdf':
                content = self._extract_pdf(file_path)
            elif ext in ['.txt', '.md', '.py', '.js', '.json', '.html', '.css', '.csv', '.log']:
                content = self._extract_text(file_path)
            else:
                # For unsupported files (images, videos, audio), return filename as context
                # This allows LLM to organize based on filename alone
                logger.info(f"Unsupported file type {ext}, using filename as content.")
                return f"File Name: {file_path.name}\nFile Type: {ext}\n(Content extraction not supported for this file type, organize based on filename only)"
                
            if content:
                return self._truncate_text(content, max_length)
            return None
            
        except Exception as e:
            logger.error(f"Failed to extract content from {path}: {e}")
            return None
            
    def _truncate_text(self, text: str, max_length: int) -> str:
        """Smart Truncation: Keep Head and Tail if too long"""
        if len(text) <= max_length:
            return text
            
        # Keep 70% Head, 30% Tail (approx)
        head_len = int(max_length * 0.7)
        tail_len = int(max_length * 0.3)
        
        return (
            text[:head_len] 
            + f"\n\n... [TRUNCATED {len(text) - max_length} CHARS] ...\n\n" 
            + text[-tail_len:]
        )

    def _extract_text(self, path: Path) -> str:
        """Read plain text files"""
        return path.read_text(encoding='utf-8', errors='ignore')
        
    def _extract_pdf(self, path: Path) -> str:
        """Extract text from PDF"""
        text = []
        with open(path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            # Limit pages for massive PDFs
            MAX_PAGES = 50
            for i, page in enumerate(reader.pages):
                if i >= MAX_PAGES:
                    text.append(f"\n... [PDF TRUNCATED AFTER {MAX_PAGES} PAGES] ...")
                    break
                text.append(page.extract_text() or "")
        return "\n".join(text)

# Singleton
content_extractor = ContentExtractor()
