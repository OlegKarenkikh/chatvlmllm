"""Field parsing utilities for structured document extraction."""

import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class Field:
    """Represents a document field."""
    name: str
    value: str
    confidence: float = 0.0
    bbox: Optional[tuple] = None


class FieldParser:
    """Parse structured fields from document text."""
    
    # Common field patterns
    FIELD_PATTERNS = {
        'date': [
            r'(\d{2}/\d{2}/\d{4})',
            r'(\d{4}-\d{2}-\d{2})',
            r'(\d{2}\.\d{2}\.\d{4})'
        ],
        'number': [
            r'№\s*(\d+)',
            r'#\s*(\d+)',
            r'Number:\s*(\d+)'
        ],
        'amount': [
            r'(\d+[,.]\d{2})\s*(?:руб|RUB|USD|EUR)',
            r'Total:\s*(\d+[,.]\d{2})'
        ],
    }
    
    @staticmethod
    def parse_fields(
        text: str,
        template: Dict[str, List[str]],
        use_ai: bool = False
    ) -> Dict[str, Field]:
        """
        Parse fields from text using template.
        
        Args:
            text: Extracted text
            template: Field template with field names
            use_ai: Whether to use AI for parsing (requires model)
            
        Returns:
            Dictionary of parsed fields
        """
        fields = {}
        lines = text.split('\n')
        
        for field_name in template.get('fields', []):
            field = FieldParser._extract_field(field_name, lines)
            fields[field_name] = field
        
        return fields
    
    @staticmethod
    def _extract_field(field_name: str, lines: List[str]) -> Field:
        """Extract a single field from text lines."""
        field_name_lower = field_name.lower()
        
        # Try to find field by name
        for line in lines:
            line_lower = line.lower()
            
            # Check if field name is in line
            if field_name_lower in line_lower:
                # Try to extract value
                parts = line.split(':', 1)
                if len(parts) == 2:
                    value = parts[1].strip()
                    return Field(name=field_name, value=value, confidence=0.8)
                
                # Try after field name
                idx = line_lower.index(field_name_lower)
                value = line[idx + len(field_name):].strip()
                if value:
                    # Remove leading colons, dashes, etc.
                    value = re.sub(r'^[:\-\s]+', '', value)
                    return Field(name=field_name, value=value, confidence=0.7)
        
        # Try pattern matching based on field type
        field_type = FieldParser._infer_field_type(field_name)
        if field_type in FieldParser.FIELD_PATTERNS:
            for pattern in FieldParser.FIELD_PATTERNS[field_type]:
                for line in lines:
                    match = re.search(pattern, line, re.IGNORECASE)
                    if match:
                        value = match.group(1)
                        return Field(name=field_name, value=value, confidence=0.6)
        
        return Field(name=field_name, value="", confidence=0.0)
    
    @staticmethod
    def _infer_field_type(field_name: str) -> str:
        """Infer field type from field name."""
        field_name_lower = field_name.lower()
        
        if any(word in field_name_lower for word in ['date', 'дата']):
            return 'date'
        elif any(word in field_name_lower for word in ['number', 'номер', '№']):
            return 'number'
        elif any(word in field_name_lower for word in ['amount', 'total', 'сумма']):
            return 'amount'
        else:
            return 'text'
    
    @staticmethod
    def format_fields_as_json(fields: Dict[str, Field]) -> Dict[str, Any]:
        """Format parsed fields as JSON."""
        return {
            name: {
                'value': field.value,
                'confidence': field.confidence
            }
            for name, field in fields.items()
        }
    
    @staticmethod
    def format_fields_as_markdown(fields: Dict[str, Field]) -> str:
        """Format parsed fields as Markdown table."""
        lines = ['| Field | Value | Confidence |', '|-------|-------|------------|']
        
        for name, field in fields.items():
            confidence = f"{field.confidence:.0%}" if field.confidence > 0 else "-"
            value = field.value if field.value else "-"
            lines.append(f"| {name} | {value} | {confidence} |")
        
        return '\n'.join(lines)