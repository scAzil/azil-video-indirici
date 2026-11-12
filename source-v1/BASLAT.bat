@echo off
setlocal
cd /d "%~dp0"
if not exist ".ready" call GUNCELLE.bat
if not exist ".ready" exit /b 1
if not exist ".venv\Scripts\python.exe" goto broken
".venv\Scripts\python.exe" app.py
if errorlevel 1 pause
exit /b
:broken
echo Uygulama ortami eksik. GUNCELLE.bat dosyasini calistirin.
pause
