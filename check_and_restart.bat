@echo off
echo ========================================
echo Проверка и перезапуск Streamlit
echo ========================================
echo.

echo 1. Останавливаем Streamlit...
taskkill /F /IM streamlit.exe 2>nul
if %errorlevel% == 0 (
    echo    ✓ Streamlit остановлен
) else (
    echo    ℹ Streamlit не был запущен
)

timeout /t 2 /nobreak >nul

echo.
echo 2. Проверяем парсер...
python test_parser.py
if %errorlevel% == 0 (
    echo    ✓ Парсер работает корректно
) else (
    echo    ✗ Ошибка парсера
    pause
    exit /b 1
)

echo.
echo 3. Запускаем Streamlit...
start "ChatVLMLLM" cmd /k "streamlit run app.py"

timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo ✓ Готово!
echo ========================================
echo.
echo Откройте браузер: http://localhost:8501
echo.
echo Парсер теперь находит все 13 элементов!
echo.
pause
