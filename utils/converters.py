"""Data converters for ChatVLMLLM.

This module provides converters for different data formats,
including OCR JSON to text tables and HTML to plain text.
"""
import json
import re
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from html.parser import HTMLParser


@dataclass
class ParsedElement:
    """Represents a parsed OCR element."""
    index: int
    bbox: List[int]
    category: str
    text: str
    emoji: str
    
    @property
    def bbox_str(self) -> str:
        """Get bbox as formatted string."""
        if self.bbox:
            return f"[{', '.join(map(str, self.bbox))}]"
        return "N/A"
    
    @property
    def has_text(self) -> bool:
        """Check if element has text content."""
        return bool(self.text and self.text.strip())


@dataclass
class OCRStatistics:
    """Statistics about parsed OCR data."""
    total_elements: int
    elements_with_text: int
    categories: Dict[str, int]
    total_characters: int
    
    @property
    def text_coverage(self) -> float:
        """Percentage of elements with text."""
        if self.total_elements == 0:
            return 0.0
        return (self.elements_with_text / self.total_elements) * 100


class DotsOCRConverter:
    """Converter for DOTS OCR JSON format."""
    
    # Category to emoji mapping
    CATEGORY_EMOJIS = {
        'Picture': '🖼️',
        'Section-header': '📋',
        'Text': '📝',
        'Table': '📊',
        'Title': '📑',
        'List-item': '📌',
        'Caption': '💬',
        'Page-header': '📄',
        'Page-footer': '📄',
        'Footnote': '📎',
        'Formula': '🔢',
        'Figure': '📈',
        'Code': '💻',
    }
    
    DEFAULT_EMOJI = '📄'
    
    @classmethod
    def is_dots_ocr_json(cls, content: str) -> bool:
        """Check if content is DOTS OCR JSON format.
        
        Args:
            content: String to check
            
        Returns:
            True if content is valid DOTS OCR JSON
        """
        if not content or not isinstance(content, str):
            return False
        
        content = content.strip()
        if not content.startswith('['):
            return False
        
        try:
            data = json.loads(content)
            if not isinstance(data, list) or len(data) == 0:
                return False
            
            # Check first element has expected keys
            first = data[0]
            return isinstance(first, dict) and 'bbox' in first
        except (json.JSONDecodeError, KeyError, IndexError):
            return False
    
    @classmethod
    def parse_json(cls, content: str) -> List[ParsedElement]:
        """Parse DOTS OCR JSON into list of ParsedElement.
        
        Args:
            content: JSON string to parse
            
        Returns:
            List of ParsedElement objects
        """
        try:
            data = json.loads(content.strip())
        except json.JSONDecodeError:
            return []
        
        if not isinstance(data, list):
            return []
        
        elements = []
        for i, item in enumerate(data, 1):
            if not isinstance(item, dict):
                continue
            
            category = item.get('category', 'Unknown')
            emoji = cls.CATEGORY_EMOJIS.get(category, cls.DEFAULT_EMOJI)
            
            elements.append(ParsedElement(
                index=i,
                bbox=item.get('bbox', []),
                category=category,
                text=item.get('text', ''),
                emoji=emoji
            ))
        
        return elements
    
    @classmethod
    def get_statistics(cls, elements: List[ParsedElement]) -> OCRStatistics:
        """Calculate statistics for parsed elements.
        
        Args:
            elements: List of ParsedElement
            
        Returns:
            OCRStatistics object
        """
        categories: Dict[str, int] = {}
        total_chars = 0
        with_text = 0
        
        for el in elements:
            # Count categories
            categories[el.category] = categories.get(el.category, 0) + 1
            
            # Count text
            if el.has_text:
                with_text += 1
                total_chars += len(el.text)
        
        return OCRStatistics(
            total_elements=len(elements),
            elements_with_text=with_text,
            categories=categories,
            total_characters=total_chars
        )
    
    @classmethod
    def to_text_table(cls, content: str, max_text_length: int = 50) -> str:
        """Convert DOTS OCR JSON to formatted text table.
        
        Args:
            content: JSON string to convert
            max_text_length: Maximum text length per cell
            
        Returns:
            Formatted text table string
        """
        elements = cls.parse_json(content)
        if not elements:
            return content
        
        stats = cls.get_statistics(elements)
        
        # Build output
        lines = [
            "═" * 80,
            "📊 РЕЗУЛЬТАТЫ РАСПОЗНАВАНИЯ (DOTS OCR)",
            "═" * 80,
            f"Всего элементов: {stats.total_elements}",
            f"С текстом: {stats.elements_with_text} ({stats.text_coverage:.1f}%)",
            f"Символов: {stats.total_characters}",
            "",
            "Категории:",
        ]
        
        for cat, count in sorted(stats.categories.items(), key=lambda x: -x[1]):
            emoji = cls.CATEGORY_EMOJIS.get(cat, cls.DEFAULT_EMOJI)
            lines.append(f"  {emoji} {cat}: {count}")
        
        lines.extend(["", "─" * 80, ""])
        
        # Add elements
        for el in elements:
            text_preview = el.text[:max_text_length] + "..." if len(el.text) > max_text_length else el.text
            text_preview = text_preview.replace('\n', ' ') if text_preview else "—"
            
            lines.append(
                f"{el.index:3d}. {el.emoji} [{el.category:15s}] "
                f"bbox={el.bbox_str:25s} │ {text_preview}"
            )
        
        lines.extend(["", "═" * 80])
        
        return "\n".join(lines)
    
    @classmethod
    def extract_text_only(cls, content: str) -> str:
        """Extract only text content from DOTS OCR JSON.
        
        Args:
            content: JSON string
            
        Returns:
            Concatenated text from all elements
        """
        elements = cls.parse_json(content)
        texts = [el.text for el in elements if el.has_text]
        return "\n".join(texts)


class HTMLTableParser(HTMLParser):
    """Parser for extracting text from HTML tables."""
    
    def __init__(self):
        super().__init__()
        self.rows: List[List[str]] = []
        self.current_row: List[str] = []
        self.current_cell: str = ""
        self.in_table = False
        self.in_cell = False
    
    def handle_starttag(self, tag: str, attrs):
        if tag == 'table':
            self.in_table = True
        elif tag == 'tr' and self.in_table:
            self.current_row = []
        elif tag in ('td', 'th') and self.in_table:
            self.in_cell = True
            self.current_cell = ""
    
    def handle_endtag(self, tag: str):
        if tag == 'table':
            self.in_table = False
        elif tag == 'tr' and self.in_table:
            if self.current_row:
                self.rows.append(self.current_row)
        elif tag in ('td', 'th') and self.in_table:
            self.in_cell = False
            self.current_row.append(self.current_cell.strip())
    
    def handle_data(self, data: str):
        if self.in_cell:
            self.current_cell += data


class HTMLTableConverter:
    """Converter for HTML tables to text format."""
    
    @classmethod
    def has_html_table(cls, content: str) -> bool:
        """Check if content contains HTML table.
        
        Args:
            content: String to check
            
        Returns:
            True if content contains HTML table
        """
        if not content or not isinstance(content, str):
            return False
        return '<table' in content.lower() and '</table>' in content.lower()
    
    @classmethod
    def extract_tables(cls, content: str) -> List[List[List[str]]]:
        """Extract all tables from HTML content.
        
        Args:
            content: HTML string
            
        Returns:
            List of tables, each table is list of rows, each row is list of cells
        """
        # Find all table blocks
        table_pattern = re.compile(
            r'<table[^>]*>.*?</table>',
            re.DOTALL | re.IGNORECASE
        )
        
        tables = []
        for match in table_pattern.finditer(content):
            parser = HTMLTableParser()
            parser.feed(match.group())
            if parser.rows:
                tables.append(parser.rows)
        
        return tables
    
    @classmethod
    def to_text_table(cls, content: str, max_cell_length: int = 30) -> str:
        """Convert HTML tables in content to text format.
        
        Args:
            content: HTML content with tables
            max_cell_length: Maximum cell content length
            
        Returns:
            Content with HTML tables replaced by text tables
        """
        if not cls.has_html_table(content):
            return content
        
        tables = cls.extract_tables(content)
        if not tables:
            return content
        
        result_parts = []
        
        # Replace each table
        remaining = content
        for i, table in enumerate(tables):
            # Convert table to text
            text_table = cls._format_text_table(table, max_cell_length)
            
            # Find and replace the HTML table
            table_pattern = re.compile(
                r'<table[^>]*>.*?</table>',
                re.DOTALL | re.IGNORECASE
            )
            remaining = table_pattern.sub(text_table, remaining, count=1)
        
        return remaining
    
    @classmethod
    def _format_text_table(cls, rows: List[List[str]], max_cell_length: int) -> str:
        """Format a table as text.
        
        Args:
            rows: List of rows, each row is list of cells
            max_cell_length: Maximum cell content length
            
        Returns:
            Formatted text table
        """
        if not rows:
            return ""
        
        # Truncate cells and calculate column widths
        processed_rows = []
        col_widths = []
        
        for row in rows:
            processed_row = []
            for i, cell in enumerate(row):
                # Truncate and clean cell
                cell = cell.strip().replace('\n', ' ')
                if len(cell) > max_cell_length:
                    cell = cell[:max_cell_length-3] + "..."
                processed_row.append(cell)
                
                # Track column width
                if i >= len(col_widths):
                    col_widths.append(len(cell))
                else:
                    col_widths[i] = max(col_widths[i], len(cell))
            
            processed_rows.append(processed_row)
        
        # Build text table
        lines = []
        separator = "+" + "+".join("-" * (w + 2) for w in col_widths) + "+"
        
        lines.append(separator)
        for row_idx, row in enumerate(processed_rows):
            # Pad row to have all columns
            while len(row) < len(col_widths):
                row.append("")
            
            cells = [
                f" {cell:{col_widths[i]}} "
                for i, cell in enumerate(row)
            ]
            lines.append("|" + "|".join(cells) + "|")
            
            # Add separator after header row
            if row_idx == 0:
                lines.append(separator.replace("-", "="))
            else:
                lines.append(separator)
        
        return "\n".join(lines)
