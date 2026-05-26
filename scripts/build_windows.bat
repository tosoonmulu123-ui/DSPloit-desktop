@echo off
REM Build DSPloit PC for Windows using PyInstaller

echo === DSPloit PC Windows Build ===
echo.

pip install -r requirements.txt
pip install pyinstaller

pyinstaller --onefile --windowed ^
    --name "DSPloit PC" ^
    --icon assets/icon.ico ^
    --add-data "payloads;payloads" ^
    main.py

echo.
echo Build complete! Check dist/ folder.
pause
