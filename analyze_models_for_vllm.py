#!/usr/bin/env python3
"""
Анализ кешированных моделей для подготовки к vLLM с проверкой параметров на HuggingFace
"""

import os
import json
import requests
from pathlib import Path
from typing import Dict, Any, Optional

class ModelAnalyzer:
    def __init__(self):
        self.cache_dir = Path.home() / ".cache" / "huggingface" / "hub"
        self.models_info = {}
        
    def get_cached_models(self) -> Dict[str, Dict]:
        """Получение списка кешированных моделей"""
        print("🔍 АНАЛИЗ КЕШИРОВАННЫХ МОДЕЛЕЙ")
        print("=" * 40)
        
        if not self.cache_dir.exists():
            print("❌ Директория кеша HuggingFace не найдена!")
            return {}
        
        model_dirs = [d for d in self.cache_dir.iterdir() if d.is_dir() and d.name.startswith('models--')]
        
        models = {}
        for model_dir in model_dirs:
            model_name = model_dir.name.replace('models--', '').replace('--', '/')
            
            # Проверка наличия файлов модели
            snapshots_dir = model_dir / "snapshots"
            if not snapshots_dir.exists():
                continue
                
            snapshot_dirs = [d for d in snapshots_dir.iterdir() if d.is_dir()]
            if not snapshot_dirs:
                continue
            
            latest_snapshot = max(snapshot_dirs, key=lambda x: x.stat().st_mtime)
            
            # Анализ конфигурации модели
            config_path = latest_snapshot / "config.json"
            if config_path.exists():
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                    
                    # Вычисление размера
                    size_gb = self.get_model_size(model_dir)
                    
                    models[model_name] = {
                        'path': str(model_dir),
                        'size_gb': round(size_gb, 2),
                        'config': config,
                        'model_type': config.get('model_type', 'unknown'),
                        'architectures': config.get('architectures', []),
                        'max_position_embeddings': config.get('max_position_embeddings'),
                        'hidden_size': config.get('hidden_size'),
                        'vocab_size': config.get('vocab_size')
                    }
                except Exception as e:
                    print(f"⚠️ Ошибка чтения конфига {model_name}: {e}")
        
        return models
    
    def get_model_size(self, model_path: Path) -> float:
        """Вычисление размера модели в ГБ"""
        total_size = 0
        for root, dirs, files in os.walk(model_path):
            for file in files:
                file_path = os.path.join(root, file)
                if os.path.exists(file_path):
                    total_size += os.path.getsize(file_path)
        return total_size / (1024**3)
    
    def get_huggingface_info(self, model_name: str) -> Optional[Dict]:
        """Получение информации о модели с HuggingFace"""
        try:
            url = f"https://huggingface.co/api/models/{model_name}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"⚠️ Не удалось получить информацию о {model_name}: {e}")
        return None
    
    def analyze_vllm_compatibility(self, model_name: str, config: Dict) -> Dict[str, Any]:
        """Анализ совместимости с vLLM"""
        compatibility = {
            'vllm_supported': False,
            'recommended_params': {},
            'issues': [],
            'category': 'unknown'
        }
        
        model_type = config.get('model_type', '').lower()
        architectures = config.get('architectures', [])
        
        # Определение категории модели
        if any(keyword in model_name.lower() for keyword in ['ocr', 'got', 'dots']):
            compatibility['category'] = 'ocr'
        elif any(keyword in model_name.lower() for keyword in ['vision', 'vlm', 'qwen', 'phi']):
            compatibility['category'] = 'vlm'
        else:
            compatibility['category'] = 'other'
        
        # Проверка поддержки vLLM
        supported_architectures = [
            'qwen2vlforconditionalgeneration',
            'qwen3vlforconditionalgeneration', 
            'qwen2_5_vlforconditionalgeneration',
            'phi3vforcausallm',
            'dotsocrcausallm',
            'gotqwenforcausallm',
            'gotocrforconditionalgeneration',
            'deepseekocrcausallm'
        ]
        
        arch_lower = [arch.lower() for arch in architectures]
        
        # Специальная проверка для dots.ocr (известно что работает)
        if 'dots.ocr' in model_name:
            compatibility['vllm_supported'] = True
        elif any(arch in supported_architectures for arch in arch_lower):
            compatibility['vllm_supported'] = True
        
        # Рекомендуемые параметры
        max_pos = config.get('max_position_embeddings', 2048)
        
        if compatibility['category'] == 'ocr':
            compatibility['recommended_params'] = {
                'max_model_len': min(max_pos, 2048),
                'gpu_memory_utilization': 0.8,
                'trust_remote_code': True,
                'enforce_eager': True,
                'port_offset': 0
            }
        elif compatibility['category'] == 'vlm':
            compatibility['recommended_params'] = {
                'max_model_len': min(max_pos, 4096),
                'gpu_memory_utilization': 0.7,
                'trust_remote_code': True,
                'enforce_eager': False,
                'port_offset': 10
            }
        else:
            compatibility['recommended_params'] = {
                'max_model_len': min(max_pos, 2048),
                'gpu_memory_utilization': 0.6,
                'trust_remote_code': True,
                'enforce_eager': True,
                'port_offset': 20
            }
        
        # Проверка потенциальных проблем
        if config.get('vocab_size', 0) > 100000:
            compatibility['issues'].append('Large vocabulary size may require more memory')
        
        if config.get('hidden_size', 0) > 4096:
            compatibility['issues'].append('Large hidden size may require more GPU memory')
        
        return compatibility
    
    def generate_vllm_configs(self):
        """Генерация конфигураций для vLLM"""
        print("\n📝 ГЕНЕРАЦИЯ КОНФИГУРАЦИЙ VLLM")
        print("=" * 40)
        
        models = self.get_cached_models()
        
        # Приоритетные модели для настройки
        priority_models = [
            'rednote-hilab/dots.ocr',
            'stepfun-ai/GOT-OCR2_0', 
            'ucaslcl/GOT-OCR2_0',
            'stepfun-ai/GOT-OCR-2.0-hf',
            'deepseek-ai/deepseek-ocr',
            'Qwen/Qwen3-VL-2B-Instruct',
            'Qwen/Qwen2-VL-2B-Instruct',
            'Qwen/Qwen2-VL-7B-Instruct',
            'Qwen/Qwen2.5-VL-7B-Instruct',
            'microsoft/Phi-3.5-vision-instruct'
        ]
        
        configs = {}
        port = 8000
        
        for model_name in priority_models:
            if model_name in models:
                model_info = models[model_name]
                compatibility = self.analyze_vllm_compatibility(model_name, model_info['config'])
                
                if compatibility['vllm_supported']:
                    config = {
                        'model_name': model_name,
                        'container_name': model_name.replace('/', '-').replace('.', '-').lower() + '-vllm',
                        'port': port,
                        'size_gb': model_info['size_gb'],
                        'category': compatibility['category'],
                        'vllm_params': compatibility['recommended_params'],
                        'issues': compatibility['issues'],
                        'priority': self.get_model_priority(model_name, compatibility['category'])
                    }
                    
                    configs[model_name] = config
                    port += 1
                    
                    print(f"✅ {model_name}")
                    print(f"   Категория: {compatibility['category']}")
                    print(f"   Размер: {model_info['size_gb']} ГБ")
                    print(f"   Порт: {port-1}")
                    if compatibility['issues']:
                        print(f"   Проблемы: {', '.join(compatibility['issues'])}")
                    print()
                else:
                    print(f"❌ {model_name} - не поддерживается vLLM")
            else:
                print(f"⚠️ {model_name} - не найдена в кеше")
        
        return configs
    
    def get_model_priority(self, model_name: str, category: str) -> int:
        """Определение приоритета модели"""
        if 'dots.ocr' in model_name:
            return 1  # Высший приоритет
        elif category == 'ocr':
            return 2  # Высокий приоритет для OCR
        elif 'Qwen3' in model_name:
            return 3  # Новые модели
        elif category == 'vlm':
            return 4  # VLM модели
        else:
            return 5  # Остальные
    
    def save_configs(self, configs: Dict):
        """Сохранение конфигураций"""
        # Сохранение в JSON
        with open('vllm_models_config.json', 'w', encoding='utf-8') as f:
            json.dump(configs, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Конфигурации сохранены в vllm_models_config.json")
        
        # Создание краткого отчета
        with open('models_summary.txt', 'w', encoding='utf-8') as f:
            f.write("АНАЛИЗ МОДЕЛЕЙ ДЛЯ VLLM\n")
            f.write("=" * 30 + "\n\n")
            
            # Группировка по категориям
            categories = {}
            for model_name, config in configs.items():
                cat = config['category']
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append((model_name, config))
            
            for category, models in categories.items():
                f.write(f"{category.upper()} МОДЕЛИ:\n")
                f.write("-" * 20 + "\n")
                
                # Сортировка по приоритету
                models.sort(key=lambda x: x[1]['priority'])
                
                for model_name, config in models:
                    f.write(f"• {model_name}\n")
                    f.write(f"  Размер: {config['size_gb']} ГБ\n")
                    f.write(f"  Порт: {config['port']}\n")
                    f.write(f"  Max tokens: {config['vllm_params']['max_model_len']}\n")
                    if config['issues']:
                        f.write(f"  Проблемы: {', '.join(config['issues'])}\n")
                    f.write("\n")
                f.write("\n")
        
        print(f"📄 Краткий отчет сохранен в models_summary.txt")

def main():
    """Основная функция"""
    analyzer = ModelAnalyzer()
    configs = analyzer.generate_vllm_configs()
    
    if configs:
        analyzer.save_configs(configs)
        print(f"\n✅ Проанализировано {len(configs)} моделей для vLLM")
    else:
        print("\n❌ Подходящие модели не найдены")

if __name__ == "__main__":
    main()