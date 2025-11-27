"""
Document Processing Tools

Document operations using Gemini for analysis.
Implements operations from Master SRS Section 3.5.
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
import PyPDF2

from ..llm_router import get_router

logger = logging.getLogger(__name__)


class DocTools:
    """Document processing tools using Gemini"""
    
    def __init__(self):
        self.router = get_router()
        logger.info("DocTools initialized")
    
    async def summarize_file(
        self,
        file_path: str,
        summary_type: str = "brief"
    ) -> Dict[str, Any]:
        """
        Summarize a document using Gemini
        
        Args:
            file_path: Path to document
            summary_type: "brief", "detailed", or "multi-level"
            
        Returns:
            dict: Summary result
        """
        try:
            path = Path(file_path).expanduser()
            
            if not path.exists():
                return {
                    "error": True,
                    "message": f"File not found: {file_path}"
                }
            
            # Extract text based on file type
            text = await self._extract_text(path)
            
            if not text:
                return {
                    "error": True,
                    "message": "Could not extract text from file"
                }
            
            # Summarize using Gemini
            summary = await self.router.summarize_with_gemini(text, summary_type)
            
            logger.info(f"Summarized file: {file_path}")
            
            return {
                "file": str(path),
                "summary_type": summary_type,
                "summary": summary,
                "word_count": len(text.split())
            }
            
        except Exception as e:
            logger.error(f"Failed to summarize file: {e}")
            return {
                "error": True,
                "message": str(e)
            }
    
    async def translate_file(
        self,
        file_path: str,
        target_language: str
    ) -> Dict[str, Any]:
        """
        Translate document using Gemini
        
        Args:
            file_path: Path to document
            target_language: Target language code (ar, en, etc.)
            
        Returns:
            dict: Translation result
        """
        try:
            path = Path(file_path).expanduser()
            
            if not path.exists():
                return {
                    "error": True,
                    "message": f"File not found: {file_path}"
                }
            
            # Extract text
            text = await self._extract_text(path)
            
            if not text:
                return {
                    "error": True,
                    "message": "Could not extract text from file"
                }
            
            # Translate using Gemini
            translated = await self.router.translate_with_gemini(text, target_language)
            
            logger.info(f"Translated file: {file_path} to {target_language}")
            
            return {
                "file": str(path),
                "target_language": target_language,
                "original_text": text[:200] + "..." if len(text) > 200 else text,
                "translated_text": translated
            }
            
        except Exception as e:
            logger.error(f"Failed to translate file: {e}")
            return {
                "error": True,
                "message": str(e)
            }
    
    async def compare_files(
        self,
        file1: str,
        file2: str
    ) -> Dict[str, Any]:
        """
        Compare two documents using Gemini
        
        Args:
            file1: First file path
            file2: Second file path
            
        Returns:
            dict: Comparison result
        """
        try:
            path1 = Path(file1).expanduser()
            path2 = Path(file2).expanduser()
            
            if not path1.exists() or not path2.exists():
                return {
                    "error": True,
                    "message": "One or both files not found"
                }
            
            # Extract text from both files
            text1 = await self._extract_text(path1)
            text2 = await self._extract_text(path2)
            
            # Compare using Gemini
            prompt = f"""
Compare the following two documents and provide:
1. Main similarities
2. Key differences
3. Overall assessment

Document 1:
{text1[:2000]}

Document 2:
{text2[:2000]}
"""
            
            comparison = await self.router.generate_with_gemini(prompt, temperature=0.5)
            
            logger.info(f"Compared files: {file1} vs {file2}")
            
            return {
                "file1": str(path1),
                "file2": str(path2),
                "comparison": comparison
            }
            
        except Exception as e:
            logger.error(f"Failed to compare files: {e}")
            return {
                "error": True,
                "message": str(e)
            }
    
    async def extract_tasks(self, file_path: str) -> Dict[str, Any]:
        """
        Extract tasks/action items from document using Gemini
        
        Args:
            file_path: Path to document
            
        Returns:
            dict: Extracted tasks
        """
        try:
            path = Path(file_path).expanduser()
            
            if not path.exists():
                return {
                    "error": True,
                    "message": f"File not found: {file_path}"
                }
            
            # Extract text
            text = await self._extract_text(path)
            
            # Extract tasks using Gemini
            prompt = f"""
Extract all tasks, action items, and to-dos from the following document.
For each task, identify:
- Task description
- Assignee (if mentioned)
- Deadline (if mentioned)
- Priority (if mentioned)

Document:
{text}

Format as a structured list.
"""
            
            tasks_text = await self.router.generate_with_gemini(prompt, temperature=0.3)
            
            logger.info(f"Extracted tasks from: {file_path}")
            
            return {
                "file": str(path),
                "tasks": tasks_text
            }
            
        except Exception as e:
            logger.error(f"Failed to extract tasks: {e}")
            return {
                "error": True,
                "message": str(e)
            }
    
    async def read_pdf(self, file_path: str, page_range: Optional[str] = None) -> Dict[str, Any]:
        """
        Read PDF file and extract text
        
        Args:
            file_path: Path to PDF
            page_range: Optional page range (e.g., "1-5" or "all")
            
        Returns:
            dict: Extracted text
        """
        try:
            path = Path(file_path).expanduser()
            
            if not path.exists():
                return {
                    "error": True,
                    "message": f"File not found: {file_path}"
                }
            
            if path.suffix.lower() != '.pdf':
                return {
                    "error": True,
                    "message": "File is not a PDF"
                }
            
            # Extract text from PDF
            text = self._extract_pdf_text(path, page_range)
            
            logger.info(f"Read PDF: {file_path}")
            
            return {
                "file": str(path),
                "text": text,
                "word_count": len(text.split())
            }
            
        except Exception as e:
            logger.error(f"Failed to read PDF: {e}")
            return {
                "error": True,
                "message": str(e)
            }
    
    async def _extract_text(self, file_path: Path) -> str:
        """Extract text from various file types"""
        suffix = file_path.suffix.lower()
        
        if suffix == '.pdf':
            return self._extract_pdf_text(file_path)
        elif suffix == '.txt' or suffix == '.md':
            return file_path.read_text(encoding='utf-8')
        elif suffix == '.docx':
            return self._extract_docx_text(file_path)
        else:
            # Try to read as text
            try:
                return file_path.read_text(encoding='utf-8')
            except:
                return ""
    
    def _extract_pdf_text(self, file_path: Path, page_range: Optional[str] = None) -> str:
        """Extract text from PDF"""
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = []
                
                # Determine pages to extract
                if page_range and page_range != "all":
                    # Parse range (e.g., "1-5")
                    if '-' in page_range:
                        start, end = map(int, page_range.split('-'))
                        pages = range(start - 1, min(end, len(reader.pages)))
                    else:
                        page_num = int(page_range) - 1
                        pages = [page_num]
                else:
                    pages = range(len(reader.pages))
                
                # Extract text from pages
                for page_num in pages:
                    if page_num < len(reader.pages):
                        page = reader.pages[page_num]
                        text.append(page.extract_text())
                
                return '\n\n'.join(text)
                
        except Exception as e:
            logger.error(f"PDF extraction failed: {e}")
            return ""
    
    def _extract_docx_text(self, file_path: Path) -> str:
        """Extract text from DOCX"""
        try:
            import docx
            doc = docx.Document(file_path)
            return '\n\n'.join([para.text for para in doc.paragraphs])
        except Exception as e:
            logger.error(f"DOCX extraction failed: {e}")
            return ""


if __name__ == "__main__":
    # Test doc tools
    import asyncio
    
    async def test():
        tools = DocTools()
        
        print("Testing DocTools...")
        
        # Note: Requires actual PDF file for testing
        print("\nDocTools initialized successfully")
        print("To test, provide a PDF file path")
    
    asyncio.run(test())
