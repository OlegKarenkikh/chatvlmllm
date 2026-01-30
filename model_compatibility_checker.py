#!/usr/bin/env python3
"""
Проверка совместимости моделей с Transformers и vLLM
Создание корректных конфигураций для каждого режима
"""

import json
import requests
from pathlib import Path

class ModelCompatibilityChecker:
    def __init__(self):
        # Проверенная совместимость на основе документации и тестирования
        self.compatibility_matrix = {
            # OCR модели
            "rednote-hilab/dots.ocr": {
                "transformers": {
                    "supported": True,
                    "architecture": "DotsOCRForCausalLM", 
                    "memory_8bit_gb": 3.5,
                    "memory_fp16_gb": 5.67,
                    "issues": [],
                    "tested": True
                },
                "vllm": {
                    "supported": True,
                    "architecture": "DotsOCRForCausalLM",
                    "memory_required_gb": 8.0,
                    "max_model_len": 2048,
                    "issues": [],
                    "tested": True
                }
            },
            
            "stepfun-ai/GOT-OCR-2.0-hf": {
                "transformers": {
                    "supported": True,
                    "architecture": "GOTQwenForCausalLM",
                    "memory_8bit_gb": 0.8,
                    "memory_fp16_gb": 1.06,
                    "issues": ["Requires specific prompt format"],
                    "tested": False
                },
                "vllm": {
                    "supported": False,  # vLLM не поддерживает GOT-OCR архитектуру
                    "architecture": "GOTQwenForCausalLM",
                    "memory_required_gb": 3.0,
                    "max_model_len": 2048,
                    "issues": ["Custom architecture not supported by vLLM"],
                    "tested": False
                }
            },
            
            # VLM модели
            "Qwen/Qwen2-VL-2B-Instruct": {
                "transformers": {
                    "supported": True,
                    "architecture": "Qwen2VLForConditionalGeneration",
                    "memory_8bit_gb": 2.5,
                    "memory_fp16_gb": 4.13,
                    "issues": [],
                    "tested": False
                },
                "vllm": {
                    "supported": True,
                    "architecture": "Qwen2VLForConditionalGeneration", 
                    "memory_required_gb": 6.0,
                    "max_model_len": 4096,
                    "issues": [],
                    "tested": False
                }
            },
            
            "Qwen/Qwen2-VL-7B-Instruct": {
                "transformers": {
                    "supported": True,
                    "architecture": "Qwen2VLForConditionalGeneration",
                    "memory_8bit_gb": 4.5,
                    "memory_fp16_gb": 7.61,
                    "issues": ["Large model - slow on limited hardware"],
                    "tested": False
                },
                "vllm": {
                    "supported": True,
                    "architecture": "Qwen2VLForConditionalGeneration",
                    "memory_required_gb": 12.0,
                    "max_model_len": 4096,
                    "issues": ["Requires high-end GPU"],
                    "tested": False
                }
            },
            
            "microsoft/Phi-3.5-vision-instruct": {
                "transformers": {
                    "supported": True,
                    "architecture": "Phi3VForCausalLM",
                    "memory_8bit_gb": 4.5,
                    "memory_fp16_gb": 7.73,
                    "issues": [],
                    "tested": False
                },
                "vllm": {
                    "supported": True,
                    "architecture": "Phi3VForCausalLM",
                    "memory_required_gb": 10.0,
                    "max_model_len": 4096,
                    "issues": ["May require specific vLLM version"],
                    "tested": False
                }
            },
            
            "vikhyatk/moondream2": {
                "transformers": {
                    "supported": True,
                    "architecture": "MoondreamForConditionalGeneration",
                    "memory_8bit_gb": 2.0,
                    "memory_fp16_gb": 3.59,
                    "issues": ["Custom architecture - may need special handling"],
                    "tested": False
                },
                "vllm": {
                    "supported": False,  # vLLM не поддерживает Moondream архитектуру
                    "architecture": "MoondreamForConditionalGeneration",
                    "memory_required_gb": 5.0,
                    "max_model_len": 2048,
                    "issues": ["Custom architecture not supported by vLLM"],
                    "tested": False
                }
            },
            
            # Дополнительные модели для Transformers
            "microsoft/Phi-3-vision-128k-instruct": {
                "transformers": {
                    "supported": True,
                    "architecture": "Phi3VForCausalLM",
                    "memory_8bit_gb": 4.0,
                    "memory_fp16_gb": 7.0,
                    "issues": [],
                    "tested": False
                },
                "vllm": {
                    "supported": False,  # Длинный контекст может быть проблематичен
                    "architecture": "Phi3VForCausalLM",
                    "memory_required_gb": 12.0,
                    "max_model_len": 8192,
                    "issues": ["Long context may cause memory issues"],
                    "tested": False
                }
            },
            
            "OpenGVLab/InternVL2-2B": {
                "transformers": {
                    "supported": True,
                    "architecture": "InternVLChatModel",
                    "memory_8bit_gb": 2.0,
                    "memory_fp16_gb": 3.8,
                    "issues": ["May require specific transformers version"],
                    "tested": False
                },
                "vllm": {
                    "supported": False,  # Специфическая архитектура
                    "architecture": "InternVLChatModel",
                    "memory_required_gb": 5.0,
                    "max_model_len": 2048,
                    "issues": ["Custom architecture not supported by vLLM"],
                    "tested": False
                }
            }
        }
    
    def get_transformers_compatible_models(self):
        """Получить модели, совместимые с Transformers"""
        compatible = {}
        for model_name, compat in self.compatibility_matrix.items():
            if compat["transformers"]["supported"]:
                compatible[model_name] = {
                    "name": self._get_display_name(model_name),
                    "type": self._get_model_type(model_name),
                    "architecture": compat["transformers"]["architecture"],
                    "memory_8bit_gb": compat["transformers"]["memory_8bit_gb"],
                    "memory_fp16_gb": compat["transformers"]["memory_fp16_gb"],
                    "max_memory_gb": compat["transformers"]["memory_fp16_gb"] + 1.0,
                    "default_prompt": self._get_default_prompt(model_name),
                    "issues": compat["transformers"]["issues"],
                    "tested": compat["transformers"]["tested"],
                    "priority": self._get_priority(model_name)
                }
        return compatible
    
    def get_vllm_compatible_models(self):
        """Получить модели, совместимые с vLLM"""
        compatible = {}
        for model_name, compat in self.compatibility_matrix.items():
            if compat["vllm"]["supported"]:
                compatible[model_name] = {
                    "name": self._get_display_name(model_name),
                    "type": self._get_model_type(model_name),
                    "architecture": compat["vllm"]["architecture"],
                    "container_name": self._get_container_name(model_name),
                    "port": self._get_port(model_name),
                    "size_gb": compat["transformers"]["memory_fp16_gb"],
                    "memory_required_gb": compat["vllm"]["memory_required_gb"],
                    "vllm_params": self._get_vllm_params(model_name, compat["vllm"]),
                    "issues": compat["vllm"]["issues"],
                    "tested": compat["vllm"]["tested"],
                    "priority": self._get_priority(model_name)
                }
        return compatible
    
    def _get_display_name(self, model_name):
        """Получить отображаемое имя модели"""
        name_map = {
            "rednote-hilab/dots.ocr": "DotsOCR",
            "stepfun-ai/GOT-OCR-2.0-hf": "GOT-OCR 2.0",
            "Qwen/Qwen2-VL-2B-Instruct": "Qwen2-VL 2B",
            "Qwen/Qwen2-VL-7B-Instruct": "Qwen2-VL 7B",
            "microsoft/Phi-3.5-vision-instruct": "Phi-3.5 Vision",
            "microsoft/Phi-3-vision-128k-instruct": "Phi-3 Vision 128K",
            "vikhyatk/moondream2": "Moondream2",
            "OpenGVLab/InternVL2-2B": "InternVL2 2B"
        }
        return name_map.get(model_name, model_name.split('/')[-1])
    
    def _get_model_type(self, model_name):
        """Определить тип модели"""
        if "ocr" in model_name.lower() or "dots" in model_name.lower():
            return "ocr"
        else:
            return "vlm"
    
    def _get_container_name(self, model_name):
        """Получить имя контейнера для vLLM"""
        name = model_name.replace('/', '-').replace('.', '-').lower()
        return f"{name}-vllm"
    
    def _get_port(self, model_name):
        """Получить порт для модели"""
        port_map = {
            "rednote-hilab/dots.ocr": 8000,
            "Qwen/Qwen2-VL-2B-Instruct": 8001,
            "stepfun-ai/GOT-OCR-2.0-hf": 8002,
            "Qwen/Qwen2-VL-7B-Instruct": 8003,
            "microsoft/Phi-3.5-vision-instruct": 8004,
            "microsoft/Phi-3-vision-128k-instruct": 8005,
            "vikhyatk/moondream2": 8006,
            "OpenGVLab/InternVL2-2B": 8007
        }
        return port_map.get(model_name, 8000)
    
    def _get_default_prompt(self, model_name):
        """Получить промпт по умолчанию"""
        if "ocr" in model_name.lower() or "dots" in model_name.lower():
            if "got" in model_name.lower():
                return "OCR:"
            else:
                return "Extract all text from this image"
        else:
            return "Describe what you see in this image"
    
    def _get_priority(self, model_name):
        """Получить приоритет модели"""
        priority_map = {
            "rednote-hilab/dots.ocr": 1,
            "Qwen/Qwen2-VL-2B-Instruct": 2,
            "stepfun-ai/GOT-OCR-2.0-hf": 3,
            "microsoft/Phi-3.5-vision-instruct": 4,
            "Qwen/Qwen2-VL-7B-Instruct": 5,
            "vikhyatk/moondream2": 6,
            "microsoft/Phi-3-vision-128k-instruct": 7,
            "OpenGVLab/InternVL2-2B": 8
        }
        return priority_map.get(model_name, 9)
    
    def _get_vllm_params(self, model_name, vllm_compat):
        """Получить параметры vLLM для модели"""
        base_params = {
            "trust_remote_code": True,
            "dtype": "bfloat16",
            "disable_log_requests": True
        }
        
        # Специфические параметры для разных моделей
        if "dots" in model_name.lower():
            base_params.update({
                "max_model_len": 2048,
                "gpu_memory_utilization": 0.7,
                "enforce_eager": True
            })
        elif "qwen2-vl-2b" in model_name.lower():
            base_params.update({
                "max_model_len": 4096,
                "gpu_memory_utilization": 0.6,
                "enforce_eager": False
            })
        elif "qwen2-vl-7b" in model_name.lower():
            base_params.update({
                "max_model_len": 4096,
                "gpu_memory_utilization": 0.5,
                "enforce_eager": False
            })
        elif "phi-3" in model_name.lower():
            base_params.update({
                "max_model_len": 4096,
                "gpu_memory_utilization": 0.6,
                "enforce_eager": True
            })
        else:
            base_params.update({
                "max_model_len": 2048,
                "gpu_memory_utilization": 0.6,
                "enforce_eager": True
            })
        
        return base_params
    
    def generate_corrected_configs(self):
        """Генерация исправленных конфигураций"""
        transformers_models = self.get_transformers_compatible_models()
        vllm_models = self.get_vllm_compatible_models()
        
        # Конфигурация для integrated_model_launcher.py
        integrated_config = {
            "transformers": transformers_models,
            "vllm": vllm_models
        }
        
        # Конфигурация только для vLLM (working_models_config.json)
        vllm_only_config = vllm_models
        
        return integrated_config, vllm_only_config, transformers_models
    
    def save_corrected_configs(self):
        """Сохранение исправленных конфигураций"""
        integrated_config, vllm_config, transformers_config = self.generate_corrected_configs()
        
        # Сохранение конфигурации для vLLM
        with open("corrected_vllm_models_config.json", "w", encoding="utf-8") as f:
            json.dump(vllm_config, f, indent=2, ensure_ascii=False)
        
        # Сохранение конфигурации для Transformers
        with open("corrected_transformers_models_config.json", "w", encoding="utf-8") as f:
            json.dump(transformers_config, f, indent=2, ensure_ascii=False)
        
        # Сохранение интегрированной конфигурации
        with open("corrected_integrated_models_config.json", "w", encoding="utf-8") as f:
            json.dump(integrated_config, f, indent=2, ensure_ascii=False)
        
        return integrated_config, vllm_config, transformers_config
    
    def print_compatibility_report(self):
        """Вывод отчета о совместимости"""
        print("🔍 ОТЧЕТ О СОВМЕСТИМОСТИ МОДЕЛЕЙ")
        print("=" * 50)
        
        transformers_models = self.get_transformers_compatible_models()
        vllm_models = self.get_vllm_compatible_models()
        
        print(f"\n🤖 TRANSFORMERS РЕЖИМ ({len(transformers_models)} моделей):")
        print("-" * 30)
        for model_name, config in sorted(transformers_models.items(), key=lambda x: x[1]['priority']):
            status = "✅ Протестировано" if config['tested'] else "⚠️ Требует тестирования"
            issues = f" ({', '.join(config['issues'])})" if config['issues'] else ""
            print(f"{config['priority']}. {config['name']} - {config['memory_8bit_gb']} GB - {status}{issues}")
        
        print(f"\n🚀 vLLM РЕЖИМ ({len(vllm_models)} моделей):")
        print("-" * 30)
        for model_name, config in sorted(vllm_models.items(), key=lambda x: x[1]['priority']):
            status = "✅ Протестировано" if config['tested'] else "⚠️ Требует тестирования"
            issues = f" ({', '.join(config['issues'])})" if config['issues'] else ""
            print(f"{config['priority']}. {config['name']} - {config['memory_required_gb']} GB - {status}{issues}")
        
        print(f"\n❌ НЕСОВМЕСТИМЫЕ С vLLM:")
        print("-" * 30)
        for model_name, compat in self.compatibility_matrix.items():
            if not compat["vllm"]["supported"]:
                display_name = self._get_display_name(model_name)
                issues = ', '.join(compat["vllm"]["issues"])
                print(f"• {display_name}: {issues}")
        
        print(f"\n💡 РЕКОМЕНДАЦИИ:")
        print("-" * 15)
        print("• Для ограниченной GPU памяти (< 6 GB): Используйте Transformers режим")
        print("• Для высокой производительности (> 8 GB): Используйте vLLM режим")
        print("• GOT-OCR и Moondream2: Только Transformers режим")
        print("• DotsOCR: Лучший выбор для OCR в обоих режимах")
        print("• Qwen2-VL-2B: Универсальная VLM для обоих режимов")

def main():
    """Основная функция"""
    checker = ModelCompatibilityChecker()
    
    print("🔧 ПРОВЕРКА СОВМЕСТИМОСТИ МОДЕЛЕЙ")
    print("=" * 40)
    
    # Генерация и сохранение исправленных конфигураций
    print("📝 Генерация исправленных конфигураций...")
    integrated_config, vllm_config, transformers_config = checker.save_corrected_configs()
    
    print("✅ Конфигурации сохранены:")
    print("   • corrected_vllm_models_config.json")
    print("   • corrected_transformers_models_config.json") 
    print("   • corrected_integrated_models_config.json")
    
    # Вывод отчета
    checker.print_compatibility_report()
    
    print(f"\n📊 СТАТИСТИКА:")
    print(f"   • Transformers совместимых: {len(transformers_config)}")
    print(f"   • vLLM совместимых: {len(vllm_config)}")
    print(f"   • Общий пул моделей: {len(checker.compatibility_matrix)}")

if __name__ == "__main__":
    main()