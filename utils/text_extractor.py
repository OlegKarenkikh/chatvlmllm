"""Text extraction and processing utilities."""

import re
from typing import List, Dict, Any, Optional
from collections import Counter


class TextExtractor:
    """Utility class for text extraction and processing."""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean extracted text."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        # Fix common OCR errors
        text = TextExtractor.fix_common_errors(text)
        
        return text
    
    @staticmethod
    def fix_common_errors(text: str) -> str:
        """Fix common OCR errors."""
        # Common character substitutions
        replacements = {
            '0': 'O',  # Zero to O in text context
            'l': 'I',  # lowercase L to I in certain contexts
        }
        
        # Apply context-aware fixes
        # This is a simplified version - can be expanded
        
        return text
    
    @staticmethod
    def extract_dates(text: str) -> List[str]:
        """Extract dates from text."""
        # Various date patterns
        patterns = [
            r'\d{2}/\d{2}/\d{4}',  # DD/MM/YYYY
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{2}\.\d{2}\.\d{4}',  # DD.MM.YYYY
            r'\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}',
        ]
        
        dates = []
        for pattern in patterns:
            dates.extend(re.findall(pattern, text, re.IGNORECASE))
        
        return dates
    
    @staticmethod
    def extract_numbers(text: str) -> List[str]:
        """Extract numbers from text."""
        return re.findall(r'\b\d+(?:\.\d+)?\b', text)
    
    @staticmethod
    def extract_emails(text: str) -> List[str]:
        """Extract email addresses from text."""
        pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return re.findall(pattern, text)
    
    @staticmethod
    def extract_phones(text: str) -> List[str]:
        """Extract phone numbers from text."""
        patterns = [
            r'\+?\d{1,3}[-\s]?\(?\d{3}\)?[-\s]?\d{3}[-\s]?\d{4}',
            r'\d{3}-\d{3}-\d{4}',
            r'\(\d{3}\)\s*\d{3}-\d{4}',
        ]
        
        phones = []
        for pattern in patterns:
            phones.extend(re.findall(pattern, text))
        
        return phones
    
    @staticmethod
    def split_into_lines(text: str) -> List[str]:
        """Split text into lines."""
        return [line.strip() for line in text.split('\n') if line.strip()]
    
    @staticmethod
    def get_text_stats(text: str) -> Dict[str, Any]:
        """Get statistics about extracted text."""
        lines = TextExtractor.split_into_lines(text)
        words = text.split()
        
        return {
            'total_characters': len(text),
            'total_lines': len(lines),
            'total_words': len(words),
            'avg_word_length': sum(len(word) for word in words) / len(words) if words else 0,
            'avg_line_length': sum(len(line) for line in lines) / len(lines) if lines else 0,
            'has_dates': len(TextExtractor.extract_dates(text)) > 0,
            'has_emails': len(TextExtractor.extract_emails(text)) > 0,
            'has_phones': len(TextExtractor.extract_phones(text)) > 0,
        }