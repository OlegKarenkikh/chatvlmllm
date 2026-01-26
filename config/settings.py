"""Centralized settings and constants for ChatVLMLLM.

This module contains all magic numbers, configuration constants,
and settings used throughout the application.
"""
from dataclasses import dataclass
from typing import Dict, List, Optional


# =============================================================================
# Application Settings
# =============================================================================

@dataclass(frozen=True)
class AppSettings:
    """Main application settings."""
    APP_TITLE: str = "🤖 ChatVLM - Vision Language Models"
    APP_ICON: str = "🤖"
    APP_VERSION: str = "2.0.0"
    
    PAGE_CONFIG = {
        "page_title": "ChatVLM - Vision Language Models",
        "page_icon": "🤖",
        "layout": "wide",
        "initial_sidebar_state": "expanded"
    }


# =============================================================================
# Token Settings
# =============================================================================

@dataclass(frozen=True)
class TokenSettings:
    """Token-related constants."""
    # Reserve for input tokens when calculating safe max tokens
    INPUT_TOKEN_RESERVE: int = 500
    
    # Minimum safe tokens to generate
    MIN_SAFE_TOKENS: int = 100
    
    # Fallback ratio when model max tokens unknown
    FALLBACK_RATIO: float = 0.5
    
    # Default max tokens for different modes
    DEFAULT_MAX_TOKENS_CHAT: int = 2048
    DEFAULT_MAX_TOKENS_OCR: int = 4096
    
    # Token estimation multipliers
    TOKENS_PER_WORD_MULTIPLIER: float = 1.3
    IMAGE_TOKEN_ESTIMATE: int = 200


# =============================================================================
# Display Settings
# =============================================================================

@dataclass(frozen=True)
class DisplaySettings:
    """UI display-related constants."""
    # Text length thresholds
    MAX_TEXT_PREVIEW_LENGTH: int = 50
    MAX_CELL_LENGTH: int = 30
    MAX_DETAILED_TEXT_LENGTH: int = 100
    
    # Table column widths (proportions)
    BBOX_TABLE_COLUMNS: List[float] = (0.5, 1.5, 2, 4)
    
    # Message display
    MAX_MESSAGE_PREVIEW: int = 200
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 10


# =============================================================================
# Model Settings
# =============================================================================

@dataclass(frozen=True)
class ModelSettings:
    """Model-related constants."""
    # Timeouts (seconds)
    MODEL_LOAD_TIMEOUT: int = 300
    INFERENCE_TIMEOUT: int = 120
    HEALTH_CHECK_TIMEOUT: int = 10
    
    # Retry settings
    MAX_RETRIES: int = 3
    RETRY_DELAY: float = 1.0
    
    # GPU memory thresholds (GB)
    LOW_MEMORY_THRESHOLD: float = 4.0
    HIGH_MEMORY_THRESHOLD: float = 16.0


# =============================================================================
# vLLM Settings
# =============================================================================

@dataclass(frozen=True)
class VLLMSettings:
    """vLLM-specific settings."""
    DEFAULT_PORT: int = 8000
    CONTAINER_NAME_PREFIX: str = "vllm-model-"
    
    # API endpoints
    HEALTH_ENDPOINT: str = "/health"
    COMPLETIONS_ENDPOINT: str = "/v1/chat/completions"
    
    # Container settings
    GPU_MEMORY_UTILIZATION: float = 0.9
    MAX_MODEL_LEN: int = 32768
    
    # Timeouts
    CONTAINER_START_TIMEOUT: int = 300
    CONTAINER_STOP_TIMEOUT: int = 30


# =============================================================================
# OCR Settings
# =============================================================================

@dataclass(frozen=True)
class OCRSettings:
    """OCR-specific settings."""
    # Category emojis for BBOX visualization
    CATEGORY_EMOJIS: Dict[str, str] = None
    
    def __post_init__(self):
        object.__setattr__(self, 'CATEGORY_EMOJIS', {
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
        })
    
    # Default prompts
    DEFAULT_OCR_PROMPT: str = "Extract all text from this image."
    DEFAULT_LAYOUT_PROMPT: str = "Analyze the layout and extract structured content."


# Create singleton instances
APP = AppSettings()
TOKENS = TokenSettings()
DISPLAY = DisplaySettings()
MODELS = ModelSettings()
VLLM = VLLMSettings()
OCR = OCRSettings()


# =============================================================================
# Error Messages
# =============================================================================

class ErrorMessages:
    """Centralized error messages."""
    CUDA_ERROR = "❌ Критическая ошибка GPU. Попробуйте перезагрузить страницу."
    MODEL_LOAD_ERROR = "❌ Ошибка загрузки модели. Проверьте конфигурацию."
    API_ERROR = "❌ Ошибка API. Проверьте подключение к серверу."
    TIMEOUT_ERROR = "❌ Превышено время ожидания. Попробуйте снова."
    VALIDATION_ERROR = "❌ Ошибка валидации входных данных."
    
    # Suggestions
    CUDA_SUGGESTIONS = [
        "Перезагрузите страницу (F5)",
        "Используйте vLLM режим для стабильности",
        "Выберите модель меньшего размера"
    ]
    
    LOAD_SUGGESTIONS = [
        "Проверьте наличие модели в директории",
        "Убедитесь в достаточности GPU памяти",
        "Попробуйте другую модель"
    ]
