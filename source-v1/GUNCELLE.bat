@echo off
setlocal
cd /d "%~dp0"
echo AZiL Video Indirici - Kurulum / Guncelleme
echo Uygulama aciksa once kapatin. Ilk kurulum internet gerektirir.
where py >nul 2>nul
if errorlevel 1 goto usepython
py -3 setup_app.py
if errorlevel 1 goto failed
goto success
:usepython
where python >nul 2>nul
if errorlevel 1 goto nopython
python setup_app.py
if errorlevel 1 goto failed
:success
echo Hazir. BASLAT.bat ile acabilirsiniz.
exit /b 0
:nopython
echo Python bulunamadi. https://www.python.org/downloads/windows/ adresinden
echo Python 3.10 veya yeni 64-bit surumu kurun. Tcl/Tk ve pip secili olmali.
:failed
echo Kurulum basarisiz. Yukaridaki hata metnini kontrol edin.
pause
exit /b 1
