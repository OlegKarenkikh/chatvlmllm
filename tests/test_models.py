"""Tests for VLM models.

Тесты для проверки загрузки и работы моделей.
Школьный исследовательский проект ChatVLMLLM.
"""
import pytest
import sys
from pathlib import Path

# Добавляем корневую директорию в path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestModelLoader:
    """Тесты для ModelLoader."""
    
    def test_import_model_loader(self):
        """Проверяем, что ModelLoader импортируется."""
        from models.model_loader import ModelLoader
        assert ModelLoader is not None
    
    def test_model_loader_has_load_method(self):
        """Проверяем наличие метода load_model."""
        from models.model_loader import ModelLoader
        assert hasattr(ModelLoader, 'load_model')
    
    def test_model_loader_has_unload_method(self):
        """Проверяем наличие метода unload_all_models."""
        from models.model_loader import ModelLoader
        assert hasattr(ModelLoader, 'unload_all_models')
    
    def test_get_loaded_models(self):
        """Проверяем метод get_loaded_models."""
        from models.model_loader import ModelLoader
        assert hasattr(ModelLoader, 'get_loaded_models')
        result = ModelLoader.get_loaded_models()
        assert isinstance(result, (list, set))


class TestBaseModel:
    """Тесты для BaseModel."""
    
    def test_import_base_model(self):
        """Проверяем импорт BaseModel."""
        from models.base_model import BaseModel
        assert BaseModel is not None
    
    def test_base_model_is_abstract(self):
        """Проверяем, что BaseModel абстрактный."""
        from models.base_model import BaseModel
        from abc import ABC
        assert issubclass(BaseModel, ABC) or hasattr(BaseModel, '__abstractmethods__')


class TestModelsImport:
    """Тесты импорта модулей моделей."""
    
    def test_import_got_ocr(self):
        """Проверяем импорт GOT-OCR."""
        try:
            from models.got_ocr import GOTOCR
            assert GOTOCR is not None
        except ImportError as e:
            pytest.skip(f"GOT-OCR не установлен: {e}")
    
    def test_import_qwen_vl(self):
        """Проверяем импорт Qwen-VL."""
        try:
            from models.qwen_vl import QwenVL
            assert QwenVL is not None
        except ImportError as e:
            pytest.skip(f"Qwen-VL не установлен: {e}")
    
    def test_import_qwen3_vl(self):
        """Проверяем импорт Qwen3-VL."""
        try:
            from models.qwen3_vl import Qwen3VL
            assert Qwen3VL is not None
        except ImportError as e:
            pytest.skip(f"Qwen3-VL не установлен: {e}")
    
    def test_import_dots_ocr(self):
        """Проверяем импорт dots.ocr."""
        try:
            from models.dots_ocr import DotsOCR
            assert DotsOCR is not None
        except ImportError as e:
            pytest.skip(f"dots.ocr не установлен: {e}")


class TestConfigYaml:
    """Тесты конфигурации."""
    
    def test_config_exists(self):
        """Проверяем наличие config.yaml."""
        config_path = Path(__file__).parent.parent / 'config.yaml'
        assert config_path.exists(), "config.yaml не найден"
    
    def test_config_valid_yaml(self):
        """Проверяем валидность YAML."""
        import yaml
        config_path = Path(__file__).parent.parent / 'config.yaml'
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        assert config is not None
        assert isinstance(config, dict)
    
    def test_config_has_models(self):
        """Проверяем наличие секции models."""
        import yaml
        config_path = Path(__file__).parent.parent / 'config.yaml'
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        assert 'models' in config, "Секция 'models' отсутствует в конфиге"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])