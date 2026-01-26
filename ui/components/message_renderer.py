"""Message rendering component for ChatVLMLLM.

This module handles rendering of chat messages with support
for different content types including OCR results and tables.
"""
import streamlit as st
from typing import Dict, Any, Optional

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.converters import DotsOCRConverter, HTMLTableConverter
from utils.text_cleaner import TextCleaner
from config.settings import DISPLAY


class MessageRenderer:
    """Renders chat messages with appropriate formatting."""
    
    def __init__(self):
        self.ocr_converter = DotsOCRConverter()
        self.html_converter = HTMLTableConverter()
        self.text_cleaner = TextCleaner()
    
    def render(self, content: str, role: str = "assistant") -> None:
        """Render a message with appropriate formatting.
        
        Args:
            content: Message content
            role: Message role (user/assistant)
        """
        if not content:
            return
        
        # Detect content type and render appropriately
        if self.ocr_converter.is_dots_ocr_json(content):
            self._render_ocr_result(content)
        elif self.html_converter.has_html_table(content):
            self._render_with_tables(content)
        else:
            self._render_text(content)
    
    def _render_ocr_result(self, content: str) -> None:
        """Render DOTS OCR JSON result.
        
        Args:
            content: OCR JSON content
        """
        # Convert to text table
        text_table = self.ocr_converter.to_text_table(content)
        
        # Show formatted result
        st.code(text_table, language=None)
        
        # Add copy button and raw view
        col1, col2 = st.columns(2)
        
        with col1:
            # Extract text only for copying
            text_only = self.ocr_converter.extract_text_only(content)
            st.download_button(
                "📋 Скопировать текст",
                text_only,
                file_name="ocr_result.txt",
                mime="text/plain",
                key=f"copy_ocr_{hash(content)}"
            )
        
        with col2:
            with st.expander("🔍 Исходный JSON"):
                st.code(content, language="json")
    
    def _render_with_tables(self, content: str) -> None:
        """Render content with HTML tables converted to text.
        
        Args:
            content: Content with HTML tables
        """
        # Convert HTML tables to text
        text_content = self.html_converter.to_text_table(
            content,
            max_cell_length=DISPLAY.MAX_CELL_LENGTH
        )
        
        self._render_text(text_content)
    
    def _render_text(self, content: str) -> None:
        """Render plain text content.
        
        Args:
            content: Text content
        """
        # Clean the text
        cleaned = self.text_cleaner.normalize_whitespace(content)
        
        # Display with markdown support
        st.markdown(cleaned)
    
    def render_with_stats(self, content: str, role: str = "assistant") -> None:
        """Render message with statistics panel.
        
        Args:
            content: Message content
            role: Message role
        """
        # Show content
        self.render(content, role)
        
        # Show stats for OCR results
        if self.ocr_converter.is_dots_ocr_json(content):
            elements = self.ocr_converter.parse_json(content)
            stats = self.ocr_converter.get_statistics(elements)
            
            with st.expander("📊 Статистика"):
                col1, col2, col3 = st.columns(3)
                col1.metric("Элементов", stats.total_elements)
                col2.metric("С текстом", stats.elements_with_text)
                col3.metric("Символов", stats.total_characters)


def render_message(content: str, role: str = "assistant") -> None:
    """Convenience function to render a message.
    
    Args:
        content: Message content
        role: Message role
    """
    renderer = MessageRenderer()
    renderer.render(content, role)
