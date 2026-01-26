"""Sidebar component for ChatVLMLLM.

This module handles the sidebar UI including model selection,
parameters, and navigation.
"""
import streamlit as st
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass


@dataclass
class ModelConfig:
    """Configuration for selected model."""
    name: str
    mode: str  # 'local' or 'vllm'
    max_tokens: int
    temperature: float
    use_vllm: bool
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "mode": self.mode,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "use_vllm": self.use_vllm
        }


class SidebarComponent:
    """Sidebar UI component."""
    
    # Available pages
    PAGES = [
        ("🏠 Главная", "home"),
        ("📄 Режим OCR", "ocr"),
        ("💬 Режим чата", "chat"),
        ("📚 Документация", "docs"),
    ]
    
    # Default parameter values
    DEFAULT_MAX_TOKENS = 2048
    DEFAULT_TEMPERATURE = 0.7
    
    def __init__(self, models_config: Optional[Dict] = None):
        """Initialize sidebar component.
        
        Args:
            models_config: Dictionary with available models configuration
        """
        self.models_config = models_config or {}
        self._init_session_state()
    
    def _init_session_state(self):
        """Initialize session state variables."""
        defaults = {
            'current_page': 'home',
            'selected_model': None,
            'use_vllm': True,
            'max_tokens': self.DEFAULT_MAX_TOKENS,
            'temperature': self.DEFAULT_TEMPERATURE,
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
    
    def render(self) -> Tuple[str, ModelConfig]:
        """Render the sidebar and return selected page and model config.
        
        Returns:
            Tuple of (page_name, ModelConfig)
        """
        with st.sidebar:
            # Logo/Title
            st.markdown("## 🤖 ChatVLM")
            st.markdown("---")
            
            # Navigation
            page = self._render_navigation()
            
            st.markdown("---")
            
            # Model selection
            model_config = self._render_model_selection()
            
            st.markdown("---")
            
            # Parameters
            self._render_parameters(model_config)
            
            st.markdown("---")
            
            # Footer
            self._render_footer()
        
        return page, model_config
    
    def _render_navigation(self) -> str:
        """Render navigation section.
        
        Returns:
            Selected page identifier
        """
        st.markdown("### 📍 Навигация")
        
        for label, page_id in self.PAGES:
            if st.button(
                label,
                key=f"nav_{page_id}",
                use_container_width=True,
                type="primary" if st.session_state.current_page == page_id else "secondary"
            ):
                st.session_state.current_page = page_id
        
        return st.session_state.current_page
    
    def _render_model_selection(self) -> ModelConfig:
        """Render model selection section.
        
        Returns:
            ModelConfig with selected settings
        """
        st.markdown("### 🧠 Модель")
        
        # Mode selection
        use_vllm = st.toggle(
            "Использовать vLLM",
            value=st.session_state.use_vllm,
            help="vLLM обеспечивает стабильную работу и лучшую производительность"
        )
        st.session_state.use_vllm = use_vllm
        
        # Get available models based on mode
        if use_vllm:
            models = self._get_vllm_models()
            mode = "vllm"
        else:
            models = self._get_local_models()
            mode = "local"
        
        # Model selector
        if models:
            selected = st.selectbox(
                "Выберите модель",
                options=list(models.keys()),
                index=0,
                key="model_selector"
            )
            st.session_state.selected_model = selected
        else:
            st.warning("Модели не найдены")
            selected = None
        
        return ModelConfig(
            name=selected or "unknown",
            mode=mode,
            max_tokens=st.session_state.max_tokens,
            temperature=st.session_state.temperature,
            use_vllm=use_vllm
        )
    
    def _render_parameters(self, model_config: ModelConfig):
        """Render generation parameters section.
        
        Args:
            model_config: Current model configuration
        """
        st.markdown("### ⚙️ Параметры")
        
        # Max tokens
        max_tokens = st.slider(
            "Максимум токенов",
            min_value=256,
            max_value=8192,
            value=st.session_state.max_tokens,
            step=256,
            help="Максимальное количество токенов в ответе"
        )
        st.session_state.max_tokens = max_tokens
        
        # Temperature
        temperature = st.slider(
            "Температура",
            min_value=0.0,
            max_value=2.0,
            value=st.session_state.temperature,
            step=0.1,
            help="Контролирует случайность генерации"
        )
        st.session_state.temperature = temperature
    
    def _render_footer(self):
        """Render sidebar footer."""
        st.markdown("### ℹ️ Информация")
        
        # GPU status (placeholder)
        st.markdown("**GPU:** Проверка...")
        
        # Version
        st.caption("ChatVLM v2.0.0")
    
    def _get_vllm_models(self) -> Dict[str, Any]:
        """Get available vLLM models.
        
        Returns:
            Dictionary of model names to configs
        """
        # This would typically load from config
        return self.models_config.get('vllm', {
            "Qwen2-VL-7B": {"path": "Qwen/Qwen2-VL-7B-Instruct"},
            "InternVL2-8B": {"path": "OpenGVLab/InternVL2-8B"},
        })
    
    def _get_local_models(self) -> Dict[str, Any]:
        """Get available local models.
        
        Returns:
            Dictionary of model names to configs
        """
        return self.models_config.get('local', {})
