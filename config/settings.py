"""Settings module for managing application configuration.

Handles session state, model settings, and UI configuration.
"""

import streamlit as st
from typing import Optional, Dict, Any


class Settings:
    """Centralized settings manager for ChatVLMLLM."""
    
    @staticmethod
    def initialize_session_state():
        """Initialize all session state variables."""
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        if "current_execution_mode" not in st.session_state:
            st.session_state.current_execution_mode = "vLLM (Рекомендуется)"
        
        if "max_tokens" not in st.session_state:
            st.session_state.max_tokens = 4096
        
        if "temperature" not in st.session_state:
            st.session_state.temperature = 0.7
        
        if "uploaded_image" not in st.session_state:
            st.session_state.uploaded_image = None
        
        if "ocr_result" not in st.session_state:
            st.session_state.ocr_result = None
        
        if "loaded_model" not in st.session_state:
            st.session_state.loaded_model = None
    
    @staticmethod
    def get(key: str, default: Any = None) -> Any:
        """Safely get a value from session state.
        
        Args:
            key: Session state key
            default: Default value if key doesn't exist
            
        Returns:
            Value from session state or default
        """
        return getattr(st.session_state, key, default)
    
    @staticmethod
    def set(key: str, value: Any):
        """Set a value in session state.
        
        Args:
            key: Session state key
            value: Value to set
        """
        setattr(st.session_state, key, value)
    
    @staticmethod
    def get_model_settings() -> Dict[str, Any]:
        """Get current model-related settings.
        
        Returns:
            Dictionary with model settings
        """
        return {
            "execution_mode": Settings.get("current_execution_mode", "vLLM (Рекомендуется)"),
            "max_tokens": Settings.get("max_tokens", 4096),
            "temperature": Settings.get("temperature", 0.7),
            "loaded_model": Settings.get("loaded_model", None)
        }
    
    @staticmethod
    def get_ui_settings() -> Dict[str, Any]:
        """Get current UI-related settings.
        
        Returns:
            Dictionary with UI settings
        """
        return {
            "uploaded_image": Settings.get("uploaded_image", None),
            "ocr_result": Settings.get("ocr_result", None),
            "messages": Settings.get("messages", [])
        }
    
    @staticmethod
    def clear_chat_history():
        """Clear chat message history."""
        st.session_state.messages = []
    
    @staticmethod
    def add_message(role: str, content: str):
        """Add a message to chat history.
        
        Args:
            role: Message role ("user" or "assistant")
            content: Message content
        """
        if "messages" not in st.session_state:
            st.session_state.messages = []
        st.session_state.messages.append({"role": role, "content": content})
