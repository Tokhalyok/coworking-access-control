@echo off
echo ============================================
echo    Сборка Coworking Access Control .exe
echo ============================================

echo.
echo [1/3] Устанавливаем PyInstaller...
pip install pyinstaller

echo.
echo [2/3] Собираем .exe...
pyinstaller --onefile --windowed --name "CoworkingAccess" --add-data "abi.json;." Run.py

echo.
echo [3/3] Готово!
echo.
echo Файл находится в папке: dist/CoworkingAccess.exe
echo.
echo ВАЖНО: скопируй abi.json рядом с .exe файлом!
pause