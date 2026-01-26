# 🧹 Руководство по очистке проекта

## ❗ Файлы, рекомендуемые к удалению

Данное руководство описывает файлы, которые можно безопасно удалить для очистки проекта.

### Дубликаты в models/

Следующие файлы являются итерациями разработки и могут быть удалены:

```bash
# Дубликаты dots_ocr
rm models/dots_ocr_blackwell_compatible.py
rm models/dots_ocr_chatvlm_integration.py
rm models/dots_ocr_corrected.py
rm models/dots_ocr_dtype_fixed.py
rm models/dots_ocr_final.py
rm models/dots_ocr_fixed.py
rm models/dots_ocr_generation_fixed.py
rm models/dots_ocr_ultimate_fix.py
rm models/dots_ocr_video_processor_fixed.py
rm models/dots_ocr_vllm_integration.py

# Бекапы model_loader
rm models/model_loader_backup.py
rm models/model_loader_emergency.py
```

### Отчёты в корне

Файлы отчётов рекомендуется переместить в отдельную директорию:

```bash
# Создать директорию для отчётов
mkdir -p reports/development

# Переместить отчёты
mv *_REPORT.md reports/development/
mv *_FIX.md reports/development/
mv *_TEST.md reports/development/
mv *_STATUS.md reports/development/
```

Или удалить (если информация не нужна):

```bash
rm *_REPORT.md *_FIX.md *_TEST.md *_STATUS.md
```

### Временные файлы

```bash
# Файлы без расширения (версии)
rm 1.2.0 4.50.0 2>/dev/null

# Кеш Python
rm -rf __pycache__
rm -rf models/__pycache__
rm -rf utils/__pycache__
rm -rf ui/__pycache__
rm -rf .pytest_cache
```

## ✅ Файлы, которые НУЖНО сохранить

### Основные файлы
```
app.py                    # Основное приложение
api.py                    # REST API
config.yaml               # Конфигурация
requirements.txt          # Зависимости
README.md                 # Документация
CONTRIBUTING.md           # Руководство по участию
LICENSE                   # Лицензия
docker-compose.yaml       # Docker конфигурация
```

### Модули models/
```
models/__init__.py
models/base_model.py
models/model_loader.py    # Основной загрузчик
models/got_ocr.py
models/qwen_vl.py
models/qwen3_vl.py
models/dots_ocr.py        # Основной dots_ocr
models/phi3_vision.py
models/deepseek_ocr.py
models/got_ocr_variants.py
```

### Документация docs/
```
docs/RESEARCH_PROJECT.md
docs/MODEL_COMPARISON.md
docs/DEPLOYMENT_POLICY.md
```

### Тесты tests/
```
tests/__init__.py
tests/test_models.py
tests/test_api.py
```

## 📝 Скрипт очистки

Создайте файл `cleanup.sh`:

```bash
#!/bin/bash
# Скрипт очистки проекта ChatVLMLLM

echo "🧹 Начинаем очистку..."

# Создаём бекап перед удалением
mkdir -p .backup/models
mkdir -p .backup/reports

# Бекап дубликатов dots_ocr
cp models/dots_ocr_*.py .backup/models/ 2>/dev/null

# Бекап отчётов
cp *_REPORT.md *_FIX.md *_STATUS.md .backup/reports/ 2>/dev/null

# Удаляем дубликаты
rm -f models/dots_ocr_blackwell_compatible.py
rm -f models/dots_ocr_chatvlm_integration.py
rm -f models/dots_ocr_corrected.py
rm -f models/dots_ocr_dtype_fixed.py
rm -f models/dots_ocr_final.py
rm -f models/dots_ocr_fixed.py
rm -f models/dots_ocr_generation_fixed.py
rm -f models/dots_ocr_ultimate_fix.py
rm -f models/dots_ocr_video_processor_fixed.py
rm -f models/dots_ocr_vllm_integration.py
rm -f models/model_loader_backup.py
rm -f models/model_loader_emergency.py

# Удаляем кеш
rm -rf __pycache__ .pytest_cache
find . -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null
find . -name '*.pyc' -delete

echo "✅ Очистка завершена!"
echo "📦 Бекап сохранён в .backup/"
```

Запуск:
```bash
chmod +x cleanup.sh
./cleanup.sh
```

## ⚠️ Важно

1. Перед удалением сделайте бекап!
2. Проверьте, что `models/dots_ocr.py` содержит актуальный код
3. Запустите тесты после очистки: `pytest tests/`

---

*Руководство по очистке школьного проекта ChatVLMLLM*