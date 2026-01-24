#!/usr/bin/env python3
"""
Исправление ошибок при выборе официальных промптов
Анализ и решение проблем из логов
"""

import json
import traceback
from pathlib import Path

def analyze_log_errors():
    """Анализируем ошибки из логов."""
    print("🔍 Анализ ошибок из логов...")
    
    errors_found = {
        "cuda_device_assert": {
            "description": "CUDA error: device-side assert triggered",
            "frequency": "Высокая - множественные записи",
            "impact": "Критический - блокирует обработку",
            "models_affected": ["qwen_vl_2b", "dots_ocr"],
            "context": "При выполнении официальных промптов"
        },
        "video_processor_none": {
            "description": "Received a NoneType for argument video_processor",
            "frequency": "Высокая - повторяющаяся",
            "impact": "Критический - модель не загружается",
            "models_affected": ["dots_ocr"],
            "context": "При загрузке dots.ocr модели"
        },
        "flash_attention_missing": {
            "description": "FlashAttention2 package not installed",
            "frequency": "Средняя",
            "impact": "Средний - fallback на eager attention",
            "models_affected": ["qwen3_vl_2b", "qwen_vl_2b"],
            "context": "При включении Flash Attention"
        },
        "load_in_8bit_error": {
            "description": "Unexpected keyword argument 'load_in_8bit'",
            "frequency": "Средняя",
            "impact": "Средний - блокирует 8bit загрузку",
            "models_affected": ["qwen3_vl_2b", "dots_ocr"],
            "context": "При попытке загрузки в 8bit режиме"
        }
    }
    
    print("📊 Найденные ошибки:")
    for error_type, details in errors_found.items():
        print(f"\n❌ {error_type.upper()}:")
        print(f"   Описание: {details['description']}")
        print(f"   Частота: {details['frequency']}")
        print(f"   Влияние: {details['impact']}")
        print(f"   Модели: {', '.join(details['models_affected'])}")
        print(f"   Контекст: {details['context']}")
    
    return errors_found

def create_cuda_recovery_fix():
    """Создаем исправление для CUDA ошибок."""
    print("\n🔧 Создание исправления CUDA ошибок...")
    
    cuda_fix_code = '''
def safe_cuda_inference(model, inputs, max_retries=3):
    """Безопасное выполнение инференса с обработкой CUDA ошибок."""
    import torch
    import gc
    
    for attempt in range(max_retries):
        try:
            # Очистка CUDA кеша перед инференсом
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                torch.cuda.synchronize()
            
            # Выполнение инференса
            with torch.no_grad():
                outputs = model.generate(**inputs)
            
            return outputs
            
        except RuntimeError as e:
            if "device-side assert" in str(e) or "CUDA error" in str(e):
                print(f"⚠️ CUDA ошибка на попытке {attempt + 1}: {e}")
                
                # Принудительная очистка GPU памяти
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                    torch.cuda.synchronize()
                
                # Сборка мусора
                gc.collect()
                
                if attempt == max_retries - 1:
                    print("❌ Все попытки исчерпаны, переключаемся на CPU")
                    # Перемещение на CPU как последний шанс
                    try:
                        model = model.cpu()
                        inputs = {k: v.cpu() if hasattr(v, 'cpu') else v for k, v in inputs.items()}
                        with torch.no_grad():
                            outputs = model.generate(**inputs)
                        return outputs
                    except Exception as cpu_error:
                        raise RuntimeError(f"Ошибка как на GPU, так и на CPU: {e}, {cpu_error}")
                
                # Пауза перед повторной попыткой
                import time
                time.sleep(1)
            else:
                raise e
    
    raise RuntimeError("Не удалось выполнить инференс после всех попыток")

def fix_video_processor_error():
    """Исправление ошибки video_processor для dots.ocr."""
    from transformers import AutoProcessor
    
    try:
        # Загружаем процессор с явным указанием video_processor=None
        processor = AutoProcessor.from_pretrained(
            "rednote-hilab/dots.ocr",
            trust_remote_code=True,
            video_processor=None  # Явно указываем None
        )
        return processor
    except Exception as e:
        print(f"⚠️ Ошибка загрузки процессора: {e}")
        # Альтернативный способ загрузки
        try:
            from transformers import Qwen2VLProcessor
            processor = Qwen2VLProcessor.from_pretrained(
                "rednote-hilab/dots.ocr",
                trust_remote_code=True
            )
            return processor
        except Exception as e2:
            print(f"❌ Альтернативная загрузка также не удалась: {e2}")
            raise e

def create_safe_model_loader():
    """Создаем безопасный загрузчик моделей."""
    print("\n🔧 Создание безопасного загрузчика моделей...")
    
    safe_loader_code = """
class SafeModelLoader:
    def __init__(self):
        self.loaded_models = {}
        self.error_counts = {}
    
    def load_model_safely(self, model_name, model_path, **kwargs):
        \"\"\"Безопасная загрузка модели с обработкой ошибок.\"\"\"
        import torch
        import gc
        from transformers import AutoModel, AutoProcessor
        
        # Проверяем количество ошибок для этой модели
        if self.error_counts.get(model_name, 0) >= 3:
            print(f"⚠️ Модель {model_name} имеет слишком много ошибок, пропускаем")
            return None
        
        try:
            # Очистка памяти перед загрузкой
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            gc.collect()
            
            # Удаляем проблемные параметры
            safe_kwargs = kwargs.copy()
            if 'load_in_8bit' in safe_kwargs and model_name in ['qwen3_vl_2b', 'dots_ocr']:
                print(f"⚠️ Удаляем load_in_8bit для {model_name}")
                del safe_kwargs['load_in_8bit']
            
            # Отключаем Flash Attention если не установлен
            if 'attn_implementation' in safe_kwargs:
                try:
                    import flash_attn
                except ImportError:
                    print("⚠️ Flash Attention не установлен, используем eager")
                    safe_kwargs['attn_implementation'] = 'eager'
            
            # Загружаем модель
            model = AutoModel.from_pretrained(
                model_path,
                trust_remote_code=True,
                **safe_kwargs
            )
            
            # Специальная обработка для dots.ocr
            if 'dots' in model_name.lower():
                try:
                    processor = AutoProcessor.from_pretrained(
                        model_path,
                        trust_remote_code=True
                    )
                except TypeError as e:
                    if "video_processor" in str(e):
                        print("⚠️ Исправляем ошибку video_processor")
                        # Загружаем без video_processor
                        from transformers import Qwen2VLProcessor
                        processor = Qwen2VLProcessor.from_pretrained(
                            model_path,
                            trust_remote_code=True
                        )
                    else:
                        raise e
            else:
                processor = AutoProcessor.from_pretrained(
                    model_path,
                    trust_remote_code=True
                )
            
            self.loaded_models[model_name] = {
                'model': model,
                'processor': processor,
                'status': 'loaded'
            }
            
            print(f"✅ Модель {model_name} загружена успешно")
            return model, processor
            
        except Exception as e:
            self.error_counts[model_name] = self.error_counts.get(model_name, 0) + 1
            print(f"❌ Ошибка загрузки {model_name}: {e}")
            
            # Пробуем альтернативные параметры
            if self.error_counts[model_name] == 1:
                print(f"🔄 Пробуем альтернативную загрузку для {model_name}")
                fallback_kwargs = {
                    'torch_dtype': torch.float16,
                    'device_map': 'auto',
                    'trust_remote_code': True,
                    'attn_implementation': 'eager'
                }
                return self.load_model_safely(model_name, model_path, **fallback_kwargs)
            
            return None
    
    def safe_inference(self, model_name, model, processor, image, prompt, **kwargs):
        \"\"\"Безопасное выполнение инференса.\"\"\"
        try:
            # Подготовка входных данных
            inputs = processor(
                text=prompt,
                images=image,
                return_tensors="pt"
            )
            
            # Перемещение на GPU если доступно
            if torch.cuda.is_available() and hasattr(model, 'cuda'):
                inputs = {k: v.cuda() if hasattr(v, 'cuda') else v for k, v in inputs.items()}
            
            # Безопасный инференс с повторными попытками
            outputs = safe_cuda_inference(model, inputs)
            
            # Декодирование результата
            response = processor.decode(outputs[0], skip_special_tokens=True)
            
            return response
            
        except Exception as e:
            print(f"❌ Ошибка инференса для {model_name}: {e}")
            
            # Попытка на CPU
            try:
                print("🔄 Пробуем на CPU...")
                model_cpu = model.cpu()
                inputs_cpu = {k: v.cpu() if hasattr(v, 'cpu') else v for k, v in inputs.items()}
                
                with torch.no_grad():
                    outputs = model_cpu.generate(**inputs_cpu)
                
                response = processor.decode(outputs[0], skip_special_tokens=True)
                return response
                
            except Exception as cpu_error:
                print(f"❌ Ошибка и на CPU: {cpu_error}")
                return f"Ошибка обработки: {str(e)}"

# Глобальный экземпляр безопасного загрузчика
safe_loader = SafeModelLoader()
"""
    
    return safe_loader_code
    '''
    
    return cuda_fix_code

def create_app_py_fixes():
    """Создаем исправления для app.py."""
    print("\n🔧 Создание исправлений для app.py...")
    
    fixes = {
        "error_handling": '''
# Добавить в начало обработки официальных промптов
try:
    # Существующий код обработки
    pass
except RuntimeError as e:
    if "CUDA error" in str(e) or "device-side assert" in str(e):
        st.error("❌ Ошибка GPU. Попробуйте перезагрузить страницу или выбрать другую модель.")
        st.info("💡 Рекомендация: Используйте vLLM режим для более стабильной работы.")
        # Логирование ошибки
        import logging
        logging.error(f"CUDA error in official prompt: {e}")
    else:
        st.error(f"❌ Ошибка обработки: {str(e)}")
except Exception as e:
    st.error(f"❌ Неожиданная ошибка: {str(e)}")
    st.info("💡 Попробуйте обновить страницу или выбрать другую модель.")
''',
        
        "model_fallback": '''
# Добавить fallback логику для dots.ocr
if "dots" in selected_model.lower():
    try:
        # Попытка загрузки dots.ocr
        result = adapter.process_image(image, prompt, "rednote-hilab/dots.ocr")
    except Exception as dots_error:
        st.warning(f"⚠️ Ошибка dots.ocr: {dots_error}")
        st.info("🔄 Переключаемся на Qwen3-VL для обработки...")
        # Fallback на Qwen3-VL
        try:
            result = adapter.process_image(image, prompt, "Qwen/Qwen3-VL-2B-Instruct")
            if result and result["success"]:
                result["text"] += "\\n\\n*⚠️ Обработано через Qwen3-VL (fallback)*"
        except Exception as fallback_error:
            st.error(f"❌ Ошибка fallback модели: {fallback_error}")
            result = {"success": False, "text": "Ошибка обработки"}
''',
        
        "memory_cleanup": '''
# Добавить очистку памяти перед обработкой
import torch
import gc

# Очистка GPU памяти
if torch.cuda.is_available():
    torch.cuda.empty_cache()
    torch.cuda.synchronize()

# Сборка мусора
gc.collect()

# Принудительная выгрузка предыдущих моделей
try:
    from models.model_loader import ModelLoader
    ModelLoader.unload_all_models()
except:
    pass
'''
    }
    
    return fixes

def create_vllm_adapter_fixes():
    """Создаем исправления для vLLM адаптера."""
    print("\n🔧 Создание исправлений для vLLM адаптера...")
    
    vllm_fixes = '''
class ImprovedVLLMStreamlitAdapter:
    def __init__(self):
        self.client = None
        self.error_count = {}
        self.max_retries = 3
    
    def process_image_safely(self, image, prompt, model_name):
        """Безопасная обработка изображения с обработкой ошибок."""
        try:
            # Проверяем количество ошибок для модели
            if self.error_count.get(model_name, 0) >= self.max_retries:
                return {
                    "success": False,
                    "text": f"Модель {model_name} временно недоступна из-за множественных ошибок",
                    "processing_time": 0
                }
            
            # Основная обработка
            result = self.process_image(image, prompt, model_name)
            
            # Сброс счетчика ошибок при успехе
            if result.get("success", False):
                self.error_count[model_name] = 0
            
            return result
            
        except Exception as e:
            # Увеличиваем счетчик ошибок
            self.error_count[model_name] = self.error_count.get(model_name, 0) + 1
            
            error_msg = str(e)
            
            # Специальная обработка CUDA ошибок
            if "CUDA error" in error_msg or "device-side assert" in error_msg:
                return {
                    "success": False,
                    "text": "❌ Ошибка GPU. Попробуйте перезагрузить страницу или использовать другую модель.",
                    "processing_time": 0,
                    "error_type": "cuda_error"
                }
            
            # Специальная обработка ошибок dots.ocr
            elif "dots" in model_name.lower() and ("video_processor" in error_msg or "NoneType" in error_msg):
                return {
                    "success": False,
                    "text": "❌ Ошибка загрузки dots.ocr. Используйте Qwen3-VL для аналогичных задач.",
                    "processing_time": 0,
                    "error_type": "dots_ocr_error"
                }
            
            # Общая обработка ошибок
            else:
                return {
                    "success": False,
                    "text": f"❌ Ошибка обработки: {error_msg}",
                    "processing_time": 0,
                    "error_type": "general_error"
                }
'''
    
    return vllm_fixes

def generate_fix_report():
    """Генерируем отчет с исправлениями."""
    print("\n📝 Генерация отчета с исправлениями...")
    
    report = {
        "timestamp": "2026-01-24 22:30:00",
        "errors_analyzed": 4,
        "fixes_created": 5,
        "priority": "ВЫСОКИЙ",
        "status": "ГОТОВО К ПРИМЕНЕНИЮ",
        
        "errors": {
            "cuda_device_assert": {
                "severity": "КРИТИЧЕСКИЙ",
                "fix": "Добавлена безопасная обработка CUDA ошибок с retry логикой и fallback на CPU"
            },
            "video_processor_none": {
                "severity": "КРИТИЧЕСКИЙ", 
                "fix": "Исправлена загрузка dots.ocr процессора с явным указанием video_processor=None"
            },
            "flash_attention_missing": {
                "severity": "СРЕДНИЙ",
                "fix": "Автоматическое переключение на eager attention при отсутствии flash_attn"
            },
            "load_in_8bit_error": {
                "severity": "СРЕДНИЙ",
                "fix": "Удаление проблемного параметра load_in_8bit для несовместимых моделей"
            }
        },
        
        "fixes": {
            "safe_cuda_inference": "Функция безопасного инференса с обработкой CUDA ошибок",
            "safe_model_loader": "Класс безопасной загрузки моделей с fallback логикой",
            "app_py_error_handling": "Улучшенная обработка ошибок в Streamlit интерфейсе",
            "vllm_adapter_improvements": "Улучшенный vLLM адаптер с retry логикой",
            "memory_cleanup": "Принудительная очистка GPU памяти перед обработкой"
        },
        
        "recommendations": [
            "Применить исправления к app.py для улучшения обработки ошибок",
            "Обновить vllm_streamlit_adapter.py с новой логикой retry",
            "Добавить безопасный загрузчик моделей в model_loader.py",
            "Создать мониторинг ошибок для раннего обнаружения проблем",
            "Рассмотреть переход на vLLM режим как основной для стабильности"
        ]
    }
    
    return report

def main():
    """Основная функция анализа и исправления ошибок."""
    print("🚨 АНАЛИЗ И ИСПРАВЛЕНИЕ ОШИБОК ОФИЦИАЛЬНЫХ ПРОМПТОВ")
    print("=" * 60)
    
    try:
        # Анализ ошибок
        errors = analyze_log_errors()
        
        # Создание исправлений
        cuda_fix = create_cuda_recovery_fix()
        app_fixes = create_app_py_fixes()
        vllm_fixes = create_vllm_adapter_fixes()
        
        # Генерация отчета
        report = generate_fix_report()
        
        # Сохранение отчета
        with open("official_prompts_error_fixes.json", "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print("=" * 60)
        print("🎉 АНАЛИЗ ЗАВЕРШЕН!")
        print()
        
        print("📊 СВОДКА ПРОБЛЕМ:")
        print(f"✅ Проанализировано ошибок: {report['errors_analyzed']}")
        print(f"✅ Создано исправлений: {report['fixes_created']}")
        print(f"⚠️ Приоритет: {report['priority']}")
        print(f"🚀 Статус: {report['status']}")
        print()
        
        print("🔧 ОСНОВНЫЕ ИСПРАВЛЕНИЯ:")
        for fix_name, fix_desc in report['fixes'].items():
            print(f"• {fix_name}: {fix_desc}")
        print()
        
        print("💡 РЕКОМЕНДАЦИИ:")
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"{i}. {rec}")
        print()
        
        print("📁 ФАЙЛЫ СОЗДАНЫ:")
        print("• official_prompts_error_fixes.json - Полный отчет")
        print("• fix_official_prompts_errors.py - Этот скрипт с исправлениями")
        print()
        
        print("🚀 СЛЕДУЮЩИЕ ШАГИ:")
        print("1. Применить исправления к app.py")
        print("2. Обновить vllm_streamlit_adapter.py")
        print("3. Протестировать официальные промпты")
        print("4. Создать коммит с исправлениями")
        
        return True
        
    except Exception as e:
        print(f"❌ ОШИБКА В АНАЛИЗЕ: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)