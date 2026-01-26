"""Text cleaning utilities for ChatVLMLLM.

This module provides text cleaning and processing functions
for OCR results and model outputs.
"""
import re
from typing import Optional


class TextCleaner:
    """Utility class for cleaning and processing text."""
    
    # Common OCR artifacts to remove
    OCR_ARTIFACTS = [
        r'\\x[0-9a-fA-F]{2}',  # Hex escape sequences
        r'\x00',  # Null bytes
        r'[\x00-\x08\x0b\x0c\x0e-\x1f]',  # Control characters
    ]
    
    # Patterns for cleaning markdown
    MARKDOWN_PATTERNS = [
        (r'\*\*([^*]+)\*\*', r'\1'),  # Bold
        (r'\*([^*]+)\*', r'\1'),  # Italic
        (r'`([^`]+)`', r'\1'),  # Code
        (r'#{1,6}\s*', ''),  # Headers
    ]
    
    @classmethod
    def clean_ocr_result(cls, text: str) -> str:
        """Clean OCR result text.
        
        Removes common artifacts and normalizes whitespace.
        
        Args:
            text: Raw OCR text
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        result = text
        
        # Remove OCR artifacts
        for pattern in cls.OCR_ARTIFACTS:
            result = re.sub(pattern, '', result)
        
        # Normalize whitespace
        result = cls.normalize_whitespace(result)
        
        # Remove empty lines
        lines = [line for line in result.split('\n') if line.strip()]
        result = '\n'.join(lines)
        
        return result.strip()
    
    @classmethod
    def normalize_whitespace(cls, text: str) -> str:
        """Normalize whitespace in text.
        
        Args:
            text: Input text
            
        Returns:
            Text with normalized whitespace
        """
        if not text:
            return ""
        
        # Replace multiple spaces with single space
        result = re.sub(r' +', ' ', text)
        
        # Replace multiple newlines with double newline
        result = re.sub(r'\n{3,}', '\n\n', result)
        
        # Remove trailing whitespace from lines
        lines = [line.rstrip() for line in result.split('\n')]
        
        return '\n'.join(lines)
    
    @classmethod
    def strip_markdown(cls, text: str) -> str:
        """Remove markdown formatting from text.
        
        Args:
            text: Text with markdown
            
        Returns:
            Plain text without markdown
        """
        if not text:
            return ""
        
        result = text
        for pattern, replacement in cls.MARKDOWN_PATTERNS:
            result = re.sub(pattern, replacement, result)
        
        return result
    
    @classmethod
    def truncate(cls, text: str, max_length: int, suffix: str = "...") -> str:
        """Truncate text to maximum length.
        
        Args:
            text: Input text
            max_length: Maximum length
            suffix: Suffix to add when truncating
            
        Returns:
            Truncated text
        """
        if not text or len(text) <= max_length:
            return text or ""
        
        return text[:max_length - len(suffix)] + suffix
    
    @classmethod
    def escape_for_display(cls, text: str) -> str:
        """Escape text for safe display in UI.
        
        Args:
            text: Input text
            
        Returns:
            Escaped text safe for display
        """
        if not text:
            return ""
        
        # Escape HTML-like tags that might interfere with display
        result = text.replace('<', '&lt;').replace('>', '&gt;')
        
        return result
    
    @classmethod
    def extract_json_from_response(cls, text: str) -> Optional[str]:
        """Extract JSON from model response.
        
        Args:
            text: Response text that may contain JSON
            
        Returns:
            Extracted JSON string or None
        """
        if not text:
            return None
        
        # Try to find JSON array
        array_match = re.search(r'\[\s*\{.*?\}\s*\]', text, re.DOTALL)
        if array_match:
            return array_match.group()
        
        # Try to find JSON object
        object_match = re.search(r'\{.*?\}', text, re.DOTALL)
        if object_match:
            return object_match.group()
        
        return None
    
    @classmethod
    def format_for_copy(cls, text: str) -> str:
        """Format text for clipboard copy.
        
        Args:
            text: Input text
            
        Returns:
            Text formatted for copying
        """
        if not text:
            return ""
        
        # Clean up the text
        result = cls.normalize_whitespace(text)
        
        # Remove any display-specific formatting
        result = result.strip()
        
        return result
