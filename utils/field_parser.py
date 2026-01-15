"""Document field parsing utilities."""

import re
from typing import Dict, List, Optional, Any
from datetime import datetime


class FieldParser:
    """Parse and extract structured fields from documents."""
    
    @staticmethod
    def parse_passport_fields(text: str) -> Dict[str, str]:
        """
        Extract fields from passport text.
        
        Args:
            text: OCR text from passport
            
        Returns:
            Dictionary of extracted fields
        """
        fields = {}
        
        # Common passport field patterns
        patterns = {
            "Passport Number": r'(?:Passport|No|Number)[:\s]*([A-Z0-9]{6,12})',
            "Surname": r'(?:Surname|Last Name)[:\s]*([A-Z\s]+)',
            "Given Names": r'(?:Given Names?|First Name)[:\s]*([A-Z\s]+)',
            "Date of Birth": r'(?:Date of Birth|DOB)[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            "Date of Issue": r'(?:Date of Issue|Issued)[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            "Date of Expiry": r'(?:Date of Expiry|Expires|Valid Until)[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            "Nationality": r'(?:Nationality|Country)[:\s]*([A-Z\s]+)',
        }
        
        for field, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                fields[field] = match.group(1).strip()
        
        return fields
    
    @staticmethod
    def parse_invoice_fields(text: str) -> Dict[str, str]:
        """
        Extract fields from invoice text.
        
        Args:
            text: OCR text from invoice
            
        Returns:
            Dictionary of extracted fields
        """
        fields = {}
        
        patterns = {
            "Invoice Number": r'(?:Invoice|Bill|Receipt)\s*(?:#|No|Number)[:\s]*([A-Z0-9\-]+)',
            "Invoice Date": r'(?:Invoice Date|Date)[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            "Due Date": r'(?:Due Date|Payment Due)[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            "Vendor Name": r'(?:From|Vendor|Company)[:\s]*([A-Z][A-Za-z\s&,\.]+?)(?:\n|$)',
            "Total Amount": r'(?:Total|Amount Due|Balance)[:\s]*([£$€¥]?\s*\d+[.,]\d{2})',
            "Tax Amount": r'(?:Tax|VAT|GST)[:\s]*([£$€¥]?\s*\d+[.,]\d{2})',
        }
        
        for field, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                fields[field] = match.group(1).strip()
        
        return fields
    
    @staticmethod
    def parse_receipt_fields(text: str) -> Dict[str, Any]:
        """
        Extract fields from receipt text.
        
        Args:
            text: OCR text from receipt
            
        Returns:
            Dictionary of extracted fields
        """
        fields = {}
        
        # Store name (usually at the top)
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        if lines:
            fields["Store Name"] = lines[0]
        
        # Date and time
        date_match = re.search(r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', text)
        if date_match:
            fields["Date"] = date_match.group(1)
        
        time_match = re.search(r'(\d{1,2}:\d{2}(?::\d{2})?\s*(?:AM|PM)?)', text, re.IGNORECASE)
        if time_match:
            fields["Time"] = time_match.group(1)
        
        # Total amount
        total_match = re.search(r'(?:Total|Amount)[:\s]*([£$€¥]?\s*\d+[.,]\d{2})', text, re.IGNORECASE)
        if total_match:
            fields["Total Amount"] = total_match.group(1)
        
        # Items (simple extraction)
        items = []
        item_pattern = r'([A-Za-z\s]+)\s+([£$€¥]?\s*\d+[.,]\d{2})'
        for match in re.finditer(item_pattern, text):
            items.append({
                "description": match.group(1).strip(),
                "price": match.group(2).strip()
            })
        
        if items:
            fields["Items"] = items
        
        return fields
    
    @staticmethod
    def parse_generic_document(text: str, field_names: List[str]) -> Dict[str, str]:
        """
        Generic field extraction based on field names.
        
        Args:
            text: OCR text
            field_names: List of field names to extract
            
        Returns:
            Dictionary of extracted fields
        """
        fields = {}
        
        for field_name in field_names:
            # Create a flexible pattern for the field
            pattern = rf'{re.escape(field_name)}[:\s]*(.*?)(?=\n|$)'
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                fields[field_name] = match.group(1).strip()
            else:
                fields[field_name] = ""
        
        return fields
    
    @staticmethod
    def validate_date(date_str: str) -> Optional[datetime]:
        """
        Validate and parse date string.
        
        Args:
            date_str: Date string
            
        Returns:
            datetime object if valid, None otherwise
        """
        date_formats = [
            "%d/%m/%Y",
            "%m/%d/%Y",
            "%Y-%m-%d",
            "%d-%m-%Y",
            "%d.%m.%Y",
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        return None
    
    @staticmethod
    def normalize_amount(amount_str: str) -> Optional[float]:
        """
        Normalize monetary amount string to float.
        
        Args:
            amount_str: Amount string (e.g., "$1,234.56")
            
        Returns:
            Float value or None if invalid
        """
        # Remove currency symbols and spaces
        cleaned = re.sub(r'[$£€¥\s]', '', amount_str)
        
        # Replace comma with dot for European format
        if cleaned.count(',') == 1 and cleaned.count('.') == 0:
            cleaned = cleaned.replace(',', '.')
        elif cleaned.count(',') > 0:
            # Remove thousand separators
            cleaned = cleaned.replace(',', '')
        
        try:
            return float(cleaned)
        except ValueError:
            return None