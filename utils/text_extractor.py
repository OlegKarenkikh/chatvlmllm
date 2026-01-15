"""Text extraction and post-processing utilities."""

import re
from typing import List, Dict, Optional


class TextExtractor:
    """Text extraction and cleaning utilities."""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean extracted text.
        
        Args:
            text: Raw OCR text
            
        Returns:
            Cleaned text
        """
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        # Remove multiple newlines
        text = re.sub(r'\n+', '\n', text)
        
        # Trim whitespace
        text = text.strip()
        
        return text
    
    @staticmethod
    def extract_lines(text: str) -> List[str]:
        """
        Split text into lines.
        
        Args:
            text: Input text
            
        Returns:
            List of lines
        """
        return [line.strip() for line in text.split('\n') if line.strip()]
    
    @staticmethod
    def extract_numbers(text: str) -> List[str]:
        """
        Extract all numbers from text.
        
        Args:
            text: Input text
            
        Returns:
            List of numbers
        """
        return re.findall(r'\d+(?:\.\d+)?', text)
    
    @staticmethod
    def extract_dates(text: str) -> List[str]:
        """
        Extract dates from text.
        
        Args:
            text: Input text
            
        Returns:
            List of dates
        """
        # Common date patterns
        patterns = [
            r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',  # DD/MM/YYYY or MM/DD/YYYY
            r'\d{4}[/-]\d{1,2}[/-]\d{1,2}',  # YYYY-MM-DD
            r'\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}',
        ]
        
        dates = []
        for pattern in patterns:
            dates.extend(re.findall(pattern, text, re.IGNORECASE))
        
        return dates
    
    @staticmethod
    def extract_emails(text: str) -> List[str]:
        """
        Extract email addresses from text.
        
        Args:
            text: Input text
            
        Returns:
            List of emails
        """
        pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return re.findall(pattern, text)
    
    @staticmethod
    def extract_phone_numbers(text: str) -> List[str]:
        """
        Extract phone numbers from text.
        
        Args:
            text: Input text
            
        Returns:
            List of phone numbers
        """
        patterns = [
            r'\+?\d[\d\s\-\(\)]{7,}\d',  # International format
            r'\(\d{3}\)\s*\d{3}[\-\s]?\d{4}',  # (123) 456-7890
            r'\d{3}[\-\s]?\d{3}[\-\s]?\d{4}',  # 123-456-7890
        ]
        
        phones = []
        for pattern in patterns:
            phones.extend(re.findall(pattern, text))
        
        return phones
    
    @staticmethod
    def extract_amounts(text: str, currency: Optional[str] = None) -> List[str]:
        """
        Extract monetary amounts from text.
        
        Args:
            text: Input text
            currency: Optional currency symbol
            
        Returns:
            List of amounts
        """
        if currency:
            pattern = rf'{re.escape(currency)}\s*\d+(?:[.,]\d{{2}})?'
        else:
            # Generic currency patterns
            pattern = r'[$£€¥]\s*\d+(?:[.,]\d{2})?'
        
        return re.findall(pattern, text)
    
    @staticmethod
    def split_into_paragraphs(text: str) -> List[str]:
        """
        Split text into paragraphs.
        
        Args:
            text: Input text
            
        Returns:
            List of paragraphs
        """
        # Split on double newlines
        paragraphs = re.split(r'\n\s*\n', text)
        return [p.strip() for p in paragraphs if p.strip()]
    
    @staticmethod
    def extract_key_value_pairs(text: str) -> Dict[str, str]:
        """
        Extract key-value pairs from text (e.g., "Name: John").
        
        Args:
            text: Input text
            
        Returns:
            Dictionary of key-value pairs
        """
        pairs = {}
        lines = TextExtractor.extract_lines(text)
        
        for line in lines:
            # Look for colon-separated pairs
            if ':' in line:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    key = parts[0].strip()
                    value = parts[1].strip()
                    if key and value:
                        pairs[key] = value
        
        return pairs