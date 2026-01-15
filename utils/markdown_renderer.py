"""Markdown rendering utilities."""

import re
from typing import List, Dict


class MarkdownRenderer:
    """Utilities for rendering and formatting Markdown content."""
    
    @staticmethod
    def format_ocr_result(text: str, fields: Dict[str, str] = None) -> str:
        """
        Format OCR result as Markdown.
        
        Args:
            text: Raw OCR text
            fields: Extracted fields dictionary
            
        Returns:
            Formatted Markdown string
        """
        markdown = "## OCR Result\n\n"
        
        if fields:
            markdown += "### Extracted Fields\n\n"
            for key, value in fields.items():
                markdown += f"- **{key}**: {value}\n"
            markdown += "\n"
        
        markdown += "### Full Text\n\n"
        markdown += f"```\n{text}\n```\n"
        
        return markdown
    
    @staticmethod
    def format_table(data: List[List[str]], headers: List[str] = None) -> str:
        """
        Format data as Markdown table.
        
        Args:
            data: 2D list of data
            headers: Optional column headers
            
        Returns:
            Markdown table string
        """
        if not data:
            return ""
        
        # Use headers if provided, otherwise use first row
        if headers:
            rows = [headers] + data
        else:
            rows = data
        
        # Calculate column widths
        col_widths = [max(len(str(row[i])) for row in rows) for i in range(len(rows[0]))]
        
        # Build table
        markdown = ""
        
        # Header row
        header_row = "| " + " | ".join(str(rows[0][i]).ljust(col_widths[i]) for i in range(len(rows[0]))) + " |\n"
        markdown += header_row
        
        # Separator
        separator = "| " + " | ".join("-" * col_widths[i] for i in range(len(rows[0]))) + " |\n"
        markdown += separator
        
        # Data rows
        for row in rows[1:]:
            data_row = "| " + " | ".join(str(row[i]).ljust(col_widths[i]) for i in range(len(row))) + " |\n"
            markdown += data_row
        
        return markdown
    
    @staticmethod
    def add_code_block(content: str, language: str = "") -> str:
        """
        Wrap content in Markdown code block.
        
        Args:
            content: Content to wrap
            language: Optional language identifier
            
        Returns:
            Markdown code block
        """
        return f"```{language}\n{content}\n```"
    
    @staticmethod
    def add_quote(text: str) -> str:
        """
        Format text as Markdown quote.
        
        Args:
            text: Text to quote
            
        Returns:
            Markdown quote
        """
        lines = text.split('\n')
        return '\n'.join(f"> {line}" for line in lines)
    
    @staticmethod
    def create_list(items: List[str], ordered: bool = False) -> str:
        """
        Create Markdown list.
        
        Args:
            items: List items
            ordered: Use ordered list (numbered)
            
        Returns:
            Markdown list
        """
        if ordered:
            return '\n'.join(f"{i+1}. {item}" for i, item in enumerate(items))
        else:
            return '\n'.join(f"- {item}" for item in items)
    
    @staticmethod
    def highlight_text(text: str) -> str:
        """
        Highlight text (bold).
        
        Args:
            text: Text to highlight
            
        Returns:
            Bold Markdown text
        """
        return f"**{text}**"
    
    @staticmethod
    def italicize_text(text: str) -> str:
        """
        Italicize text.
        
        Args:
            text: Text to italicize
            
        Returns:
            Italic Markdown text
        """
        return f"*{text}*"