"""Centralized error handling for ChatVLMLLM.

This module provides unified error handling across the application,
eliminating code duplication and ensuring consistent error messages.
"""
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import List, Optional, Callable
import logging
import traceback

try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False

logger = logging.getLogger(__name__)


class ErrorType(Enum):
    """Types of errors that can occur in the application."""
    CUDA_ERROR = auto()
    MODEL_LOAD_ERROR = auto()
    API_ERROR = auto()
    TIMEOUT_ERROR = auto()
    VALIDATION_ERROR = auto()
    CONTAINER_ERROR = auto()
    NETWORK_ERROR = auto()
    UNKNOWN_ERROR = auto()


@dataclass
class ErrorResult:
    """Result of error analysis."""
    type: ErrorType
    message: str
    user_message: str
    suggestions: List[str] = field(default_factory=list)
    recoverable: bool = True
    original_error: Optional[Exception] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for logging."""
        return {
            "type": self.type.name,
            "message": self.message,
            "user_message": self.user_message,
            "suggestions": self.suggestions,
            "recoverable": self.recoverable
        }


class ErrorHandler:
    """Centralized error handler for the application."""
    
    # Error pattern matching
    ERROR_PATTERNS = {
        # CUDA errors
        "CUDA error": ErrorType.CUDA_ERROR,
        "device-side assert": ErrorType.CUDA_ERROR,
        "out of memory": ErrorType.CUDA_ERROR,
        "CUDA out of memory": ErrorType.CUDA_ERROR,
        "RuntimeError: CUDA": ErrorType.CUDA_ERROR,
        
        # Model loading errors
        "video_processor": ErrorType.MODEL_LOAD_ERROR,
        "NoneType": ErrorType.MODEL_LOAD_ERROR,
        "model not found": ErrorType.MODEL_LOAD_ERROR,
        "Failed to load": ErrorType.MODEL_LOAD_ERROR,
        "could not load": ErrorType.MODEL_LOAD_ERROR,
        
        # API errors
        "Connection refused": ErrorType.API_ERROR,
        "API error": ErrorType.API_ERROR,
        "HTTPError": ErrorType.API_ERROR,
        "status code": ErrorType.API_ERROR,
        
        # Timeout errors
        "timeout": ErrorType.TIMEOUT_ERROR,
        "Timeout": ErrorType.TIMEOUT_ERROR,
        "timed out": ErrorType.TIMEOUT_ERROR,
        
        # Container errors
        "container": ErrorType.CONTAINER_ERROR,
        "docker": ErrorType.CONTAINER_ERROR,
        
        # Network errors
        "ConnectionError": ErrorType.NETWORK_ERROR,
        "Network": ErrorType.NETWORK_ERROR,
    }
    
    # Error responses
    ERROR_RESPONSES = {
        ErrorType.CUDA_ERROR: ErrorResult(
            type=ErrorType.CUDA_ERROR,
            message="CUDA/GPU error detected",
            user_message="❌ Критическая ошибка GPU",
            suggestions=[
                "💡 Перезагрузите страницу (F5)",
                "💡 Используйте vLLM режим для стабильности",
                "💡 Выберите модель меньшего размера",
                "💡 Очистите GPU память командой: nvidia-smi --gpu-reset"
            ],
            recoverable=False
        ),
        ErrorType.MODEL_LOAD_ERROR: ErrorResult(
            type=ErrorType.MODEL_LOAD_ERROR,
            message="Model loading failed",
            user_message="❌ Ошибка загрузки модели",
            suggestions=[
                "💡 Проверьте наличие модели в директории",
                "💡 Убедитесь в достаточности GPU памяти",
                "💡 Попробуйте vLLM режим",
                "💡 Выберите другую модель"
            ],
            recoverable=True
        ),
        ErrorType.API_ERROR: ErrorResult(
            type=ErrorType.API_ERROR,
            message="API communication error",
            user_message="❌ Ошибка связи с API",
            suggestions=[
                "💡 Проверьте статус контейнера vLLM",
                "💡 Подождите завершения загрузки модели",
                "💡 Проверьте сетевое подключение"
            ],
            recoverable=True
        ),
        ErrorType.TIMEOUT_ERROR: ErrorResult(
            type=ErrorType.TIMEOUT_ERROR,
            message="Operation timed out",
            user_message="❌ Превышено время ожидания",
            suggestions=[
                "💡 Попробуйте снова",
                "💡 Уменьшите размер изображения",
                "💡 Уменьшите количество токенов"
            ],
            recoverable=True
        ),
        ErrorType.CONTAINER_ERROR: ErrorResult(
            type=ErrorType.CONTAINER_ERROR,
            message="Container operation failed",
            user_message="❌ Ошибка контейнера",
            suggestions=[
                "💡 Перезапустите контейнер",
                "💡 Проверьте Docker статус",
                "💡 Освободите GPU память"
            ],
            recoverable=True
        ),
        ErrorType.NETWORK_ERROR: ErrorResult(
            type=ErrorType.NETWORK_ERROR,
            message="Network connection error",
            user_message="❌ Ошибка сети",
            suggestions=[
                "💡 Проверьте сетевое подключение",
                "💡 Убедитесь, что сервер запущен"
            ],
            recoverable=True
        ),
        ErrorType.VALIDATION_ERROR: ErrorResult(
            type=ErrorType.VALIDATION_ERROR,
            message="Input validation failed",
            user_message="❌ Ошибка входных данных",
            suggestions=[
                "💡 Проверьте формат входных данных",
                "💡 Убедитесь в корректности изображения"
            ],
            recoverable=True
        ),
        ErrorType.UNKNOWN_ERROR: ErrorResult(
            type=ErrorType.UNKNOWN_ERROR,
            message="Unknown error occurred",
            user_message="❌ Неизвестная ошибка",
            suggestions=[
                "💡 Попробуйте перезагрузить страницу",
                "💡 Обратитесь к администратору"
            ],
            recoverable=True
        ),
    }
    
    @classmethod
    def analyze(cls, error: Exception) -> ErrorResult:
        """Analyze an exception and return appropriate ErrorResult.
        
        Args:
            error: The exception to analyze
            
        Returns:
            ErrorResult with type, messages, and suggestions
        """
        error_str = str(error)
        error_type_name = type(error).__name__
        
        # Check against known patterns
        for pattern, error_type in cls.ERROR_PATTERNS.items():
            if pattern.lower() in error_str.lower() or pattern in error_type_name:
                result = cls.ERROR_RESPONSES[error_type]
                # Create new instance with original error
                return ErrorResult(
                    type=result.type,
                    message=f"{result.message}: {error_str[:200]}",
                    user_message=result.user_message,
                    suggestions=result.suggestions.copy(),
                    recoverable=result.recoverable,
                    original_error=error
                )
        
        # Unknown error
        return ErrorResult(
            type=ErrorType.UNKNOWN_ERROR,
            message=f"Unknown error: {error_str[:200]}",
            user_message="❌ Произошла непредвиденная ошибка",
            suggestions=[
                "💡 Попробуйте перезагрузить страницу",
                "💡 Обратитесь к администратору с описанием проблемы"
            ],
            recoverable=True,
            original_error=error
        )
    
    @classmethod
    def handle(cls, error: Exception, show_ui: bool = True) -> ErrorResult:
        """Handle an error: analyze, log, and optionally display in UI.
        
        Args:
            error: The exception to handle
            show_ui: Whether to display error in Streamlit UI
            
        Returns:
            ErrorResult for further processing
        """
        result = cls.analyze(error)
        
        # Log the error
        logger.error(
            f"Error handled: {result.type.name} - {result.message}",
            exc_info=True
        )
        
        # Display in UI if requested and Streamlit is available
        if show_ui and HAS_STREAMLIT:
            cls.display(result)
        
        return result
    
    @classmethod
    def display(cls, result: ErrorResult):
        """Display error in Streamlit UI.
        
        Args:
            result: ErrorResult to display
        """
        if not HAS_STREAMLIT:
            return
        
        st.error(result.user_message)
        
        # Show suggestions in expander
        if result.suggestions:
            with st.expander("Рекомендации", expanded=True):
                for suggestion in result.suggestions:
                    st.info(suggestion)
        
        # Show technical details in debug mode
        if st.session_state.get('debug_mode', False):
            with st.expander("Технические детали"):
                st.code(result.message)
                if result.original_error:
                    st.code(traceback.format_exc())
    
    @classmethod
    def safe_execute(
        cls, 
        func: Callable, 
        *args, 
        default_return=None,
        show_ui: bool = True,
        **kwargs
    ):
        """Safely execute a function with error handling.
        
        Args:
            func: Function to execute
            *args: Positional arguments for the function
            default_return: Value to return on error
            show_ui: Whether to show error in UI
            **kwargs: Keyword arguments for the function
            
        Returns:
            Function result or default_return on error
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            cls.handle(e, show_ui=show_ui)
            return default_return
    
    @classmethod
    def get_fallback_response(cls, error_type: ErrorType) -> str:
        """Get a fallback response string for an error type.
        
        Args:
            error_type: Type of error
            
        Returns:
            User-friendly error message string
        """
        result = cls.ERROR_RESPONSES.get(error_type, cls.ERROR_RESPONSES[ErrorType.UNKNOWN_ERROR])
        return f"{result.user_message}. Попробуйте: {result.suggestions[0] if result.suggestions else 'перезагрузить страницу'}"
