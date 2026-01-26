"""Tests for API endpoints.

Тесты API эндпоинтов.
Школьный исследовательский проект ChatVLMLLM.
"""
import pytest
import sys
from pathlib import Path

# Добавляем корневую директорию в path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestAPIImports:
    """Тесты импорта API."""
    
    def test_import_fastapi(self):
        """Проверяем доступность FastAPI."""
        try:
            from fastapi import FastAPI
            assert FastAPI is not None
        except ImportError:
            pytest.skip("FastAPI не установлен")
    
    def test_api_file_exists(self):
        """Проверяем наличие api.py."""
        api_path = Path(__file__).parent.parent / 'api.py'
        assert api_path.exists(), "api.py не найден"


class TestAppImports:
    """Тесты импорта приложения."""
    
    def test_import_streamlit(self):
        """Проверяем доступность Streamlit."""
        try:
            import streamlit
            assert streamlit is not None
        except ImportError:
            pytest.skip("Streamlit не установлен")
    
    def test_app_file_exists(self):
        """Проверяем наличие app.py."""
        app_path = Path(__file__).parent.parent / 'app.py'
        assert app_path.exists(), "app.py не найден"


class TestVLLMIntegration:
    """Тесты vLLM интеграции."""
    
    def test_vllm_adapter_file_exists(self):
        """Проверяем наличие vllm_streamlit_adapter.py."""
        adapter_path = Path(__file__).parent.parent / 'vllm_streamlit_adapter.py'
        # Может отсутствовать, если vLLM не используется
        if not adapter_path.exists():
            pytest.skip("vLLM адаптер не найден (опционально)")
    
    def test_single_container_manager_exists(self):
        """Проверяем наличие single_container_manager.py."""
        manager_path = Path(__file__).parent.parent / 'single_container_manager.py'
        if not manager_path.exists():
            pytest.skip("Container manager не найден (опционально)")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])