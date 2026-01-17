# Настройка CUDA в WSL2 для ChatVLMLLM

## Обзор

Это руководство описывает настройку Docker-контейнеров с поддержкой CUDA в среде WSL2 (Windows Subsystem for Linux 2).

## Требования

### Системные требования

- Windows 10 версии 21H2 или выше / Windows 11
- WSL2 (не WSL1!)
- NVIDIA GPU с поддержкой CUDA (GTX 900 series и выше)
- Минимум 8 GB VRAM для VLM моделей (рекомендуется 12+ GB)

### Программные требования

- NVIDIA GPU Driver для Windows (версия 535.104.05 или выше)
- Docker Desktop с WSL2 backend или Docker Engine в WSL
- NVIDIA Container Toolkit

## Пошаговая установка

### Шаг 1: Обновите WSL до версии 2

```powershell
# В PowerShell (от администратора)
wsl --update
wsl --set-default-version 2
```

Проверьте версию:
```powershell
wsl --list --verbose
```

### Шаг 2: Установите NVIDIA драйвер для Windows

1. Скачайте драйвер с [NVIDIA](https://www.nvidia.com/Download/index.aspx)
2. Выберите вашу GPU и операционную систему Windows
3. Установите драйвер и перезагрузите компьютер

> **Важно:** Устанавливайте драйвер в Windows, НЕ в WSL!

### Шаг 3: Установите Docker Desktop (рекомендуется)

1. Скачайте [Docker Desktop](https://www.docker.com/products/docker-desktop/)
2. Установите с опцией "Use WSL 2 based engine"
3. В настройках Docker Desktop:
   - Settings → General → "Use the WSL 2 based engine" ✓
   - Settings → Resources → WSL Integration → Включите для вашего дистрибутива

### Шаг 4: Установите NVIDIA Container Toolkit в WSL

```bash
# В терминале WSL

# Добавьте GPG ключ NVIDIA
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg

# Добавьте репозиторий
curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
  sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

# Обновите пакеты и установите toolkit
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit

# Настройте Docker runtime
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

### Шаг 5: Проверьте установку

```bash
# Проверьте nvidia-smi в WSL
nvidia-smi

# Проверьте Docker с GPU
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi
```

## Сборка и запуск ChatVLMLLM

### Автоматическая проверка окружения

```bash
python scripts/check_wsl_cuda.py
```

Скрипт проверит:
- Версию WSL
- Наличие NVIDIA драйвера
- Доступность CUDA
- Docker и Docker Compose
- NVIDIA Container Toolkit
- Доступ к GPU из Docker контейнера

### Сборка Docker образа

```bash
# Простая сборка
docker compose -f docker-compose.cuda.yml build

# Или через скрипт с дополнительными проверками
chmod +x scripts/docker_build_cuda.sh
./scripts/docker_build_cuda.sh
```

### Запуск контейнера

```bash
# Запуск в фоне
docker compose -f docker-compose.cuda.yml up -d

# Просмотр логов
docker compose -f docker-compose.cuda.yml logs -f

# Остановка
docker compose -f docker-compose.cuda.yml down
```

### Доступ к приложению

- **Web UI (Streamlit):** http://localhost:8501
- **API (FastAPI):** http://localhost:8000 (если включён profile `api`)

## Конфигурация

### Переменные окружения

```yaml
# docker-compose.cuda.yml
environment:
  # Используемые GPU (0 = первая GPU)
  - CUDA_VISIBLE_DEVICES=0
  
  # Оптимизация памяти PyTorch
  - PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
  
  # HuggingFace токен (для приватных моделей)
  - HF_TOKEN=your_token_here
```

### Настройка GPU

```yaml
# Использовать все GPU
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: all
          capabilities: [gpu]

# Использовать конкретную GPU
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          device_ids: ['0']  # или ['0', '1'] для нескольких
          capabilities: [gpu]
```

### Персистентный кеш моделей

Модели HuggingFace кешируются в Docker volume для ускорения повторных запусков:

```yaml
volumes:
  model_cache:
    driver: local
    # Можно указать конкретную папку на хосте:
    # driver_opts:
    #   type: none
    #   device: /mnt/d/model_cache
    #   o: bind
```

## Устранение проблем

### Ошибка "NVIDIA GPU not found"

1. Убедитесь, что драйвер установлен в Windows (не в WSL)
2. Проверьте `nvidia-smi` в PowerShell
3. Перезапустите WSL: `wsl --shutdown` и откройте заново

### Ошибка "could not select device driver"

```bash
# Переконфигурируйте Docker runtime
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker

# Или для Docker Desktop - перезапустите Docker Desktop
```

### Ошибка "CUDA out of memory"

1. Используйте квантизацию (INT8 или INT4)
2. Уменьшите размер batch
3. Закройте другие приложения, использующие GPU

```yaml
# В config.yaml
models:
  qwen3_vl_8b:
    precision: "int8"  # Снижает потребление VRAM на ~40%
```

### Docker Desktop не видит WSL дистрибутив

1. Откройте Docker Desktop
2. Settings → Resources → WSL Integration
3. Включите переключатель для вашего дистрибутива
4. Нажмите "Apply & Restart"

### Медленная первая сборка

Первая сборка может занять 20-40 минут из-за:
- Загрузки базового образа CUDA (~4 GB)
- Установки PyTorch с CUDA (~2 GB)
- Компиляции flash-attention (~5-10 минут)

Последующие сборки будут быстрее благодаря кешированию слоёв Docker.

### Ошибка "No space left on device"

WSL по умолчанию ограничивает размер виртуального диска:

```powershell
# Увеличьте лимит в PowerShell
wsl --shutdown
# Отредактируйте %USERPROFILE%\.wslconfig:
# [wsl2]
# memory=16GB
# swap=8GB
```

Также очистите неиспользуемые Docker образы:

```bash
docker system prune -a
```

## Сравнение производительности

### WSL2 vs Native Linux

| Операция | Native Linux | WSL2 | Разница |
|----------|--------------|------|---------|
| Инференс VLM | 100% | 95-98% | -2-5% |
| Загрузка модели | 100% | 90-95% | -5-10% |
| I/O операции | 100% | 70-80% | -20-30% |

WSL2 имеет минимальный overhead для GPU операций, но I/O (чтение файлов) может быть медленнее.

### Рекомендации по оптимизации

1. **Храните модели в WSL файловой системе** (не в `/mnt/c/`)
2. **Используйте Docker volumes** вместо bind mounts для моделей
3. **Включите Flash Attention 2** для ускорения на 20-40%

## Полезные команды

```bash
# Статус GPU
nvidia-smi

# Мониторинг GPU в реальном времени
watch -n 1 nvidia-smi

# Проверка CUDA в контейнере
docker compose -f docker-compose.cuda.yml exec chatvlmllm python -c "import torch; print(torch.cuda.is_available())"

# Очистка CUDA кеша
docker compose -f docker-compose.cuda.yml exec chatvlmllm python -c "import torch; torch.cuda.empty_cache()"

# Перезапуск контейнера
docker compose -f docker-compose.cuda.yml restart

# Просмотр использования ресурсов
docker stats chatvlmllm-cuda
```

## Ссылки

- [NVIDIA CUDA on WSL](https://docs.nvidia.com/cuda/wsl-user-guide/index.html)
- [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)
- [Docker Desktop WSL2 Backend](https://docs.docker.com/desktop/wsl/)
- [PyTorch CUDA](https://pytorch.org/get-started/locally/)
