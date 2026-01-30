#!/usr/bin/env python3
"""
Экстренное решение проблемы с памятью GPU
Использует минимальные настройки для работы хотя бы одной модели
"""

import subprocess
import time
import requests
import json

def stop_all_containers():
    """Остановка всех контейнеров"""
    print("🛑 Остановка всех vLLM контейнеров...")
    
    # Получаем список всех контейнеров
    try:
        result = subprocess.run(
            ["docker", "ps", "-a", "--format", "{{.Names}}"],
            capture_output=True, text=True, timeout=30
        )
        
        if result.returncode == 0:
            containers = result.stdout.strip().split('\n')
            vllm_containers = [c for c in containers if c and ('vllm' in c.lower() or 'dots' in c.lower() or 'qwen' in c.lower())]
            
            for container in vllm_containers:
                print(f"Остановка: {container}")
                subprocess.run(["docker", "stop", container], capture_output=True, timeout=30)
                subprocess.run(["docker", "rm", container], capture_output=True, timeout=10)
    except Exception as e:
        print(f"Ошибка остановки контейнеров: {e}")
    
    # Очистка системы
    subprocess.run(["docker", "system", "prune", "-f"], capture_output=True)
    time.sleep(5)

def get_gpu_memory_info():
    """Получение информации о GPU памяти"""
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.total,memory.free,memory.used", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=10
        )
        
        if result.returncode == 0:
            memory_info = result.stdout.strip().split(', ')
            total_mb = int(memory_info[0])
            free_mb = int(memory_info[1])
            used_mb = int(memory_info[2])
            
            return {
                "total_gb": total_mb / 1024,
                "free_gb": free_mb / 1024,
                "used_gb": used_mb / 1024,
                "available_percent": (free_mb / total_mb) * 100
            }
    except Exception as e:
        print(f"Не удалось получить информацию о GPU: {e}")
    
    return None

def start_minimal_dots_ocr():
    """Запуск dots.ocr с минимальными настройками"""
    print("🚀 Запуск dots.ocr с экстремально минимальными настройками...")
    
    # Получаем путь к кешу
    try:
        userprofile = subprocess.check_output(['echo', '%USERPROFILE%'], shell=True, text=True).strip()
        cache_path = f"{userprofile}/.cache/huggingface/hub"
    except:
        cache_path = "~/.cache/huggingface/hub"
    
    # Экстремально минимальные настройки
    command = [
        "docker", "run", "-d",
        "--name", "dots-ocr-minimal",
        "--restart", "unless-stopped",
        "-p", "8000:8000",
        "--gpus", "all",
        "--shm-size", "1g",  # Минимальный shared memory
        "-v", f"{cache_path}:/root/.cache/huggingface/hub:rw",
        "-e", "CUDA_VISIBLE_DEVICES=0",
        "-e", "NVIDIA_VISIBLE_DEVICES=all",
        "vllm/vllm-openai:latest",
        "--model", "rednote-hilab/dots.ocr",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--trust-remote-code",
        "--max-model-len", "512",  # Очень маленький контекст
        "--gpu-memory-utilization", "0.25",  # Минимальное использование
        "--dtype", "bfloat16",
        "--enforce-eager",
        "--disable-log-requests",
        "--max-num-batched-tokens", "128",  # Минимальный батч
        "--disable-custom-all-reduce",
        "--enable-prefix-caching", "false",  # Отключаем кеширование
        "--enable-chunked-prefill", "false"  # Отключаем chunked prefill
    ]
    
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            print("✅ dots.ocr запущен с минимальными настройками")
            return True
        else:
            print(f"❌ Ошибка запуска: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def wait_for_model_ready(port=8000, timeout=600):
    """Ожидание готовности модели"""
    print(f"⏳ Ожидание готовности модели на порту {port}...")
    
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            # Проверяем health
            response = requests.get(f"http://localhost:{port}/health", timeout=5)
            if response.status_code == 200:
                print("✅ Health check прошел")
                
                # Проверяем API моделей
                models_response = requests.get(f"http://localhost:{port}/v1/models", timeout=5)
                if models_response.status_code == 200:
                    print("✅ API моделей готов")
                    return True
                else:
                    print("⏳ API моделей еще не готов...")
            else:
                print("⏳ Health check не прошел...")
        except Exception as e:
            elapsed = int(time.time() - start_time)
            if elapsed % 60 == 0:  # Каждую минуту
                print(f"⏳ Ожидание... ({elapsed}s)")
        
        time.sleep(10)
    
    return False

def test_minimal_ocr():
    """Тест минимальной OCR"""
    print("🧪 Тестирование минимальной OCR...")
    
    # Создаем простое тестовое изображение
    from PIL import Image, ImageDraw, ImageFont
    
    img = Image.new('RGB', (200, 100), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 16)
    except:
        font = ImageFont.load_default()
    
    draw.text((10, 30), "Test OCR", fill='black', font=font)
    
    # Сохраняем изображение
    img.save("test_minimal_ocr.png")
    
    # Конвертируем в base64
    import base64
    import io
    
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    # Тестируем API
    payload = {
        "model": "rednote-hilab/dots.ocr",
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": "Extract text from this image"},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}}
            ]
        }],
        "max_tokens": 100,  # Минимальное количество токенов
        "temperature": 0.1
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            "http://localhost:8000/v1/chat/completions",
            json=payload,
            timeout=60
        )
        processing_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            tokens_used = result.get("usage", {}).get("total_tokens", 0)
            
            print(f"✅ OCR тест успешен!")
            print(f"   Время: {processing_time:.1f}с")
            print(f"   Токенов: {tokens_used}")
            print(f"   Результат: {content}")
            
            return True, {
                "success": True,
                "processing_time": processing_time,
                "tokens_used": tokens_used,
                "content": content
            }
        else:
            print(f"❌ API ошибка: {response.status_code}")
            print(f"   Ответ: {response.text}")
            return False, {"error": f"API error {response.status_code}"}
            
    except Exception as e:
        print(f"❌ Ошибка теста: {e}")
        return False, {"error": str(e)}

def create_final_report():
    """Создание финального отчета"""
    
    # Информация о GPU
    gpu_info = get_gpu_memory_info()
    
    # Проверка статуса контейнера
    try:
        result = subprocess.run(
            ["docker", "ps", "--filter", "name=dots-ocr-minimal", "--format", "{{.Status}}"],
            capture_output=True, text=True, timeout=10
        )
        container_status = result.stdout.strip() if result.returncode == 0 else "Unknown"
    except:
        container_status = "Unknown"
    
    # Проверка API
    api_healthy = False
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        api_healthy = response.status_code == 200
    except:
        pass
    
    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "solution": "emergency_memory_solution",
        "gpu_info": gpu_info,
        "container_status": container_status,
        "api_healthy": api_healthy,
        "configuration": {
            "model": "rednote-hilab/dots.ocr",
            "max_model_len": 512,
            "gpu_memory_utilization": 0.25,
            "max_num_batched_tokens": 128,
            "optimizations": [
                "Minimal context length (512)",
                "Low GPU utilization (25%)",
                "Small batch size (128)",
                "Disabled prefix caching",
                "Disabled chunked prefill",
                "Eager execution mode"
            ]
        },
        "recommendations": []
    }
    
    if api_healthy:
        report["status"] = "SUCCESS"
        report["recommendations"].append("Система готова к работе в минимальном режиме")
        report["recommendations"].append("Запуск приложения: streamlit run app.py")
        report["recommendations"].append("Используйте короткие тексты и простые изображения")
    else:
        report["status"] = "FAILED"
        report["recommendations"].append("Требуется дополнительная диагностика")
        report["recommendations"].append("Проверьте логи: docker logs dots-ocr-minimal")
    
    # Сохранение отчета
    with open("emergency_memory_solution_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    return report

def main():
    """Основная функция"""
    print("🚨 ЭКСТРЕННОЕ РЕШЕНИЕ ПРОБЛЕМЫ С ПАМЯТЬЮ GPU")
    print("=" * 60)
    
    # 1. Информация о GPU
    print("\n1️⃣ Анализ GPU памяти:")
    gpu_info = get_gpu_memory_info()
    
    if gpu_info:
        print(f"   Общая память: {gpu_info['total_gb']:.1f} ГБ")
        print(f"   Свободная память: {gpu_info['free_gb']:.1f} ГБ")
        print(f"   Используется: {gpu_info['used_gb']:.1f} ГБ")
        print(f"   Доступно: {gpu_info['available_percent']:.1f}%")
        
        if gpu_info['free_gb'] < 6:
            print("⚠️ ПРЕДУПРЕЖДЕНИЕ: Мало свободной GPU памяти!")
    else:
        print("❌ Не удалось получить информацию о GPU")
    
    # 2. Остановка всех контейнеров
    print("\n2️⃣ Очистка системы:")
    stop_all_containers()
    
    # 3. Запуск минимальной модели
    print("\n3️⃣ Запуск минимальной конфигурации:")
    success = start_minimal_dots_ocr()
    
    if not success:
        print("❌ Не удалось запустить даже минимальную конфигурацию")
        print("💡 Возможные причины:")
        print("   - Недостаточно GPU памяти")
        print("   - Проблемы с Docker/NVIDIA runtime")
        print("   - Конфликт с другими процессами")
        return False
    
    # 4. Ожидание готовности
    print("\n4️⃣ Ожидание готовности модели:")
    ready = wait_for_model_ready(timeout=600)  # 10 минут
    
    if not ready:
        print("❌ Модель не готова после 10 минут ожидания")
        print("💡 Проверьте логи: docker logs dots-ocr-minimal")
        return False
    
    # 5. Тестирование
    print("\n5️⃣ Тестирование OCR:")
    test_success, test_result = test_minimal_ocr()
    
    # 6. Финальный отчет
    print("\n6️⃣ Создание отчета:")
    report = create_final_report()
    
    print(f"💾 Отчет сохранен: emergency_memory_solution_report.json")
    
    # 7. Итоговый статус
    print(f"\n📊 ИТОГОВЫЙ СТАТУС:")
    print("=" * 60)
    
    if report["status"] == "SUCCESS":
        print("🎉 ЭКСТРЕННОЕ РЕШЕНИЕ УСПЕШНО!")
        print("✅ dots.ocr работает в минимальном режиме")
        print("⚠️ ОГРАНИЧЕНИЯ:")
        print("   - Максимум 512 токенов контекста")
        print("   - Только простые изображения")
        print("   - Медленная обработка")
        print("💡 ЗАПУСК: streamlit run app.py")
        
        if test_success:
            print(f"🧪 OCR тест: ✅ ПРОШЕЛ")
            print(f"   Время: {test_result.get('processing_time', 0):.1f}с")
        else:
            print(f"🧪 OCR тест: ❌ НЕ ПРОШЕЛ")
    else:
        print("❌ ЭКСТРЕННОЕ РЕШЕНИЕ НЕ СРАБОТАЛО")
        print("💡 Рекомендации:")
        print("   1. Перезагрузите систему")
        print("   2. Закройте все GPU-приложения")
        print("   3. Проверьте драйверы NVIDIA")
        print("   4. Рассмотрите использование CPU режима")
    
    return report["status"] == "SUCCESS"

if __name__ == "__main__":
    main()