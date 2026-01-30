#!/usr/bin/env python3
"""
Диагностика проблем с моделями vLLM
"""

import json
import subprocess
import requests
import time
import os
from pathlib import Path

class VLLMDiagnostics:
    def __init__(self):
        self.cache_path = str(os.path.expanduser("~/.cache/huggingface/hub")).replace('\\', '/')
        
    def run_command(self, command):
        """Выполнение команды"""
        try:
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
            return True, result.stdout.strip()
        except subprocess.CalledProcessError as e:
            return False, e.stderr.strip() if e.stderr else str(e)
    
    def check_gpu_memory(self):
        """Проверка памяти GPU"""
        print("🎮 ПРОВЕРКА GPU ПАМЯТИ")
        print("=" * 25)
        
        success, output = self.run_command("nvidia-smi --query-gpu=memory.total,memory.used,memory.free --format=csv,noheader,nounits")
        
        if success:
            lines = output.strip().split('\n')
            for i, line in enumerate(lines):
                parts = line.split(', ')
                if len(parts) == 3:
                    total, used, free = map(int, parts)
                    usage_percent = round((used / total) * 100, 1)
                    print(f"GPU {i}: {used}/{total} МБ ({usage_percent}%)")
                    print(f"   Свободно: {free} МБ")
                    
                    if free < 2000:
                        print(f"   ⚠️ Мало свободной памяти!")
                    elif free < 4000:
                        print(f"   💡 Достаточно для легких моделей")
                    else:
                        print(f"   ✅ Достаточно памяти")
        else:
            print(f"❌ Ошибка получения информации о GPU: {output}")
    
    def check_model_requirements(self, model_name):
        """Проверка требований модели"""
        model_path = Path(self.cache_path) / f"models--{model_name.replace('/', '--')}"
        
        if not model_path.exists():
            return {"status": "not_cached", "error": "Модель не кеширована"}
        
        # Проверка конфигурации
        snapshots_dir = model_path / "snapshots"
        if not snapshots_dir.exists():
            return {"status": "invalid_cache", "error": "Нет папки snapshots"}
        
        snapshot_dirs = [d for d in snapshots_dir.iterdir() if d.is_dir()]
        if not snapshot_dirs:
            return {"status": "no_snapshots", "error": "Нет снапшотов"}
        
        latest_snapshot = max(snapshot_dirs, key=lambda x: x.stat().st_mtime)
        
        # Проверка файлов
        config_path = latest_snapshot / "config.json"
        if not config_path.exists():
            return {"status": "no_config", "error": "Нет config.json"}
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Проверка специальных требований
            issues = []
            
            # Проверка архитектуры
            architectures = config.get('architectures', [])
            if any('got' in arch.lower() for arch in architectures):
                # GOT модели могут требовать дополнительные пакеты
                issues.append("GOT модели могут требовать дополнительные пакеты (verovio)")
            
            # Проверка размера словаря
            vocab_size = config.get('vocab_size', 0)
            if vocab_size > 100000:
                issues.append(f"Большой словарь ({vocab_size} токенов)")
            
            # Проверка размера модели
            hidden_size = config.get('hidden_size', 0)
            if hidden_size > 4096:
                issues.append(f"Большой hidden_size ({hidden_size})")
            
            return {
                "status": "ok",
                "config": config,
                "issues": issues,
                "architectures": architectures,
                "vocab_size": vocab_size,
                "hidden_size": hidden_size
            }
            
        except Exception as e:
            return {"status": "config_error", "error": str(e)}
    
    def test_model_launch(self, model_name, port, timeout=120):
        """Тестовый запуск модели"""
        print(f"\n🧪 ТЕСТ ЗАПУСКА: {model_name}")
        print("-" * 40)
        
        # Проверка требований
        requirements = self.check_model_requirements(model_name)
        print(f"📋 Статус кеша: {requirements['status']}")
        
        if requirements['status'] != 'ok':
            print(f"❌ {requirements.get('error', 'Неизвестная ошибка')}")
            return False
        
        if requirements['issues']:
            print(f"⚠️ Потенциальные проблемы:")
            for issue in requirements['issues']:
                print(f"   • {issue}")
        
        # Формирование команды
        container_name = f"test-{model_name.replace('/', '-').replace('.', '-').lower()}"
        
        # Остановка существующего контейнера
        self.run_command(f"docker stop {container_name}")
        self.run_command(f"docker rm {container_name}")
        
        docker_command = f"""
        docker run -d \
            --gpus all \
            --name {container_name} \
            -p {port}:{port} \
            -v {self.cache_path}:/root/.cache/huggingface/hub:ro \
            --shm-size=4g \
            vllm/vllm-openai:latest \
            --model {model_name} \
            --trust-remote-code \
            --max-model-len 1024 \
            --gpu-memory-utilization 0.6 \
            --host 0.0.0.0 \
            --port {port} \
            --disable-log-requests \
            --enforce-eager
        """.strip().replace('\n', ' ').replace('\\', '')
        
        print(f"🚀 Запуск контейнера...")
        success, output = self.run_command(docker_command)
        
        if not success:
            print(f"❌ Ошибка запуска контейнера: {output}")
            return False
        
        print(f"✅ Контейнер запущен, ожидание готовности...")
        
        # Ожидание готовности
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"http://localhost:{port}/health", timeout=5)
                if response.status_code == 200:
                    print(f"✅ Модель готова за {int(time.time() - start_time)} секунд!")
                    
                    # Остановка тестового контейнера
                    self.run_command(f"docker stop {container_name}")
                    self.run_command(f"docker rm {container_name}")
                    return True
                    
            except requests.exceptions.ConnectionError:
                pass
            except Exception as e:
                print(f"⚠️ Ошибка проверки: {e}")
            
            time.sleep(5)
        
        # Проверка логов при неудаче
        print(f"❌ Модель не готова за {timeout} секунд")
        print(f"📋 Последние логи:")
        
        success, logs = self.run_command(f"docker logs {container_name} --tail 10")
        if success:
            print(logs)
        
        # Очистка
        self.run_command(f"docker stop {container_name}")
        self.run_command(f"docker rm {container_name}")
        return False
    
    def find_compatible_models(self):
        """Поиск совместимых моделей"""
        print("🔍 ПОИСК СОВМЕСТИМЫХ МОДЕЛЕЙ")
        print("=" * 35)
        
        # Загрузка конфигураций
        try:
            with open('vllm_models_config.json', 'r', encoding='utf-8') as f:
                configs = json.load(f)
        except Exception as e:
            print(f"❌ Ошибка загрузки конфигураций: {e}")
            return []
        
        compatible_models = []
        
        # Приоритет тестирования (от простых к сложным)
        test_order = [
            "rednote-hilab/dots.ocr",  # Уже работает
            "Qwen/Qwen3-VL-2B-Instruct",  # Легкая VLM
            "Qwen/Qwen2-VL-2B-Instruct",  # Легкая VLM
            "microsoft/Phi-3.5-vision-instruct",  # Microsoft модель
            "Qwen/Qwen2.5-VL-7B-Instruct",  # Средняя VLM
            "Qwen/Qwen2-VL-7B-Instruct"  # Тяжелая VLM
        ]
        
        port = 9000  # Используем отдельные порты для тестов
        
        for model_name in test_order:
            if model_name in configs:
                print(f"\n{'='*50}")
                
                # Проверка памяти перед тестом
                self.check_gpu_memory()
                
                if self.test_model_launch(model_name, port):
                    compatible_models.append(model_name)
                    print(f"✅ {model_name} - СОВМЕСТИМА")
                else:
                    print(f"❌ {model_name} - НЕ СОВМЕСТИМА")
                
                port += 1
                time.sleep(5)  # Пауза между тестами
        
        return compatible_models
    
    def create_working_config(self, compatible_models):
        """Создание конфигурации только для работающих моделей"""
        if not compatible_models:
            print("❌ Нет совместимых моделей")
            return
        
        # Загрузка полной конфигурации
        try:
            with open('vllm_models_config.json', 'r', encoding='utf-8') as f:
                full_config = json.load(f)
        except Exception as e:
            print(f"❌ Ошибка загрузки конфигураций: {e}")
            return
        
        # Создание конфигурации только для работающих моделей
        working_config = {}
        port = 8000
        
        for model_name in compatible_models:
            if model_name in full_config:
                config = full_config[model_name].copy()
                config['port'] = port
                config['container_name'] = f"{model_name.replace('/', '-').replace('.', '-').lower()}-vllm"
                working_config[model_name] = config
                port += 1
        
        # Сохранение
        with open('vllm_working_models.json', 'w', encoding='utf-8') as f:
            json.dump(working_config, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Конфигурация работающих моделей сохранена в vllm_working_models.json")
        print(f"✅ Найдено {len(compatible_models)} совместимых моделей:")
        
        for model_name in compatible_models:
            config = working_config[model_name]
            print(f"   • {model_name} (порт {config['port']})")

def main():
    """Основная функция"""
    print("🔧 ДИАГНОСТИКА МОДЕЛЕЙ VLLM")
    print("=" * 30)
    
    diagnostics = VLLMDiagnostics()
    
    # Проверка GPU
    diagnostics.check_gpu_memory()
    
    # Поиск совместимых моделей
    compatible = diagnostics.find_compatible_models()
    
    if compatible:
        diagnostics.create_working_config(compatible)
        
        print(f"\n🎉 ДИАГНОСТИКА ЗАВЕРШЕНА!")
        print(f"✅ Совместимых моделей: {len(compatible)}")
        print(f"💡 Используйте vllm_working_models.json для запуска")
    else:
        print(f"\n❌ Совместимые модели не найдены")
        print(f"💡 Проверьте логи и требования моделей")

if __name__ == "__main__":
    main()