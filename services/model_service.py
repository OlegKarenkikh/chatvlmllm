"""Model service for ChatVLMLLM.

This module provides a unified interface for working with models,
abstracting the differences between local and vLLM modes.
"""
import logging
from typing import Dict, Any, Optional, Generator
from dataclasses import dataclass
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


@dataclass
class GenerationConfig:
    """Configuration for text generation."""
    max_tokens: int = 2048
    temperature: float = 0.7
    top_p: float = 0.9
    stream: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "stream": self.stream
        }


@dataclass
class GenerationResult:
    """Result of text generation."""
    text: str
    tokens_used: int
    finish_reason: str
    model_name: str
    
    @property
    def is_complete(self) -> bool:
        return self.finish_reason == "stop"


class BaseModelService(ABC):
    """Abstract base class for model services."""
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the service is available."""
        pass
    
    @abstractmethod
    def generate(
        self,
        prompt: str,
        image: Optional[Any] = None,
        config: Optional[GenerationConfig] = None
    ) -> GenerationResult:
        """Generate response for prompt."""
        pass
    
    @abstractmethod
    def generate_stream(
        self,
        prompt: str,
        image: Optional[Any] = None,
        config: Optional[GenerationConfig] = None
    ) -> Generator[str, None, None]:
        """Generate response as stream."""
        pass


class ModelService:
    """Unified model service that handles both local and vLLM modes."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize model service.
        
        Args:
            config: Service configuration
        """
        self.config = config or {}
        self._local_service = None
        self._vllm_service = None
        self._current_mode = "vllm"
        self._current_model = None
    
    @property
    def current_model(self) -> Optional[str]:
        """Get currently loaded model name."""
        return self._current_model
    
    @property
    def current_mode(self) -> str:
        """Get current mode (local or vllm)."""
        return self._current_mode
    
    def set_mode(self, mode: str) -> None:
        """Set the service mode.
        
        Args:
            mode: 'local' or 'vllm'
        """
        if mode not in ('local', 'vllm'):
            raise ValueError(f"Invalid mode: {mode}. Use 'local' or 'vllm'")
        self._current_mode = mode
        logger.info(f"Model service mode set to: {mode}")
    
    def load_model(self, model_name: str, **kwargs) -> bool:
        """Load a model.
        
        Args:
            model_name: Name of the model to load
            **kwargs: Additional arguments for model loading
            
        Returns:
            True if model loaded successfully
        """
        logger.info(f"Loading model: {model_name} in {self._current_mode} mode")
        
        try:
            if self._current_mode == "vllm":
                return self._load_vllm_model(model_name, **kwargs)
            else:
                return self._load_local_model(model_name, **kwargs)
        except Exception as e:
            logger.error(f"Failed to load model {model_name}: {e}")
            return False
    
    def _load_vllm_model(self, model_name: str, **kwargs) -> bool:
        """Load model via vLLM.
        
        Args:
            model_name: Model name
            **kwargs: Additional arguments
            
        Returns:
            True if successful
        """
        # This would integrate with SingleContainerManager
        # Placeholder implementation
        self._current_model = model_name
        return True
    
    def _load_local_model(self, model_name: str, **kwargs) -> bool:
        """Load model locally.
        
        Args:
            model_name: Model name
            **kwargs: Additional arguments
            
        Returns:
            True if successful
        """
        # This would integrate with model_loader
        # Placeholder implementation
        self._current_model = model_name
        return True
    
    def generate(
        self,
        prompt: str,
        image: Optional[Any] = None,
        config: Optional[GenerationConfig] = None
    ) -> GenerationResult:
        """Generate response for prompt.
        
        Args:
            prompt: Text prompt
            image: Optional image input
            config: Generation configuration
            
        Returns:
            GenerationResult with response
        """
        config = config or GenerationConfig()
        
        if not self._current_model:
            raise RuntimeError("No model loaded. Call load_model() first.")
        
        logger.info(f"Generating with {self._current_model} in {self._current_mode} mode")
        
        # Placeholder - would call actual generation
        return GenerationResult(
            text="Generated response placeholder",
            tokens_used=0,
            finish_reason="stop",
            model_name=self._current_model
        )
    
    def generate_stream(
        self,
        prompt: str,
        image: Optional[Any] = None,
        config: Optional[GenerationConfig] = None
    ) -> Generator[str, None, None]:
        """Generate response as stream.
        
        Args:
            prompt: Text prompt
            image: Optional image input
            config: Generation configuration
            
        Yields:
            Response text chunks
        """
        config = config or GenerationConfig()
        
        if not self._current_model:
            raise RuntimeError("No model loaded. Call load_model() first.")
        
        # Placeholder - would yield actual chunks
        yield "Streaming "
        yield "response "
        yield "placeholder"
    
    def unload_model(self) -> bool:
        """Unload current model.
        
        Returns:
            True if successful
        """
        logger.info(f"Unloading model: {self._current_model}")
        self._current_model = None
        return True
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about current model.
        
        Returns:
            Dictionary with model information
        """
        return {
            "name": self._current_model,
            "mode": self._current_mode,
            "loaded": self._current_model is not None
        }
