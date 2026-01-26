"""Error handling module for ChatVLMLLM.

Handles GPU errors, CUDA errors, model errors, and provides
user-friendly error messages.
"""

import streamlit as st
from typing import Tuple, Optional


class ErrorHandler:
    """Centralized error handler for common errors."""
    
    @staticmethod
    def is_cuda_error(error: Exception) -> bool:
        """Check if error is a CUDA-related error.
        
        Args:
            error: Exception to check
            
        Returns:
            True if CUDA error, False otherwise
        """
        error_msg = str(error)
        return "CUDA error" in error_msg or "device-side assert" in error_msg
    
    @staticmethod
    def is_model_loading_error(error: Exception) -> bool:
        """Check if error is a model loading error.
        
        Args:
            error: Exception to check
            
        Returns:
            True if model loading error, False otherwise
        """
        error_msg = str(error)
        return "video_processor" in error_msg or "NoneType" in error_msg
    
    @staticmethod
    def is_out_of_memory_error(error: Exception) -> bool:
        """Check if error is an OOM error.
        
        Args:
            error: Exception to check
            
        Returns:
            True if OOM error, False otherwise
        """
        error_msg = str(error).lower()
        return "out of memory" in error_msg or "oom" in error_msg
    
    @staticmethod
    def handle_error(error: Exception, context: str = "") -> Tuple[str, str]:
        """Handle error and return user-friendly message.
        
        Args:
            error: Exception that occurred
            context: Context where error occurred (e.g., "OCR processing")
            
        Returns:
            Tuple of (error_message, recommendation)
        """
        if ErrorHandler.is_cuda_error(error):
            return (
                f"❌ Критическая ошибка GPU{': ' + context if context else ''}.",
                "💡 Рекомендация: Перезагрузите страницу или используйте vLLM режим для более стабильной работы."
            )
        
        elif ErrorHandler.is_model_loading_error(error):
            return (
                f"❌ Ошибка загрузки модели{': ' + context if context else ''}.",
                "💡 Рекомендация: Попробуйте использовать Qwen3-VL вместо dots.ocr."
            )
        
        elif ErrorHandler.is_out_of_memory_error(error):
            return (
                f"❌ Недостаточно памяти GPU{': ' + context if context else ''}.",
                "💡 Рекомендация: Используйте меньшую модель или уменьшите max_tokens."
            )
        
        else:
            return (
                f"❌ Неожиданная ошибка{': ' + context if context else ''}: {str(error)}",
                "💡 Рекомендация: Попробуйте перезагрузить страницу или выбрать другую модель."
            )
    
    @staticmethod
    def display_error(error: Exception, context: str = ""):
        """Display error in Streamlit UI with recommendations.
        
        Args:
            error: Exception that occurred
            context: Context where error occurred
        """
        error_msg, recommendation = ErrorHandler.handle_error(error, context)
        st.error(error_msg)
        st.info(recommendation)
    
    @staticmethod
    def create_error_response(error: Exception, context: str = "") -> str:
        """Create error response message for chat.
        
        Args:
            error: Exception that occurred
            context: Context where error occurred
            
        Returns:
            Formatted error message for chat
        """
        error_msg, recommendation = ErrorHandler.handle_error(error, context)
        return f"{error_msg}\n\n{recommendation}"
