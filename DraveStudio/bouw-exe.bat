@echo off
chcp 65001 >nul
title DraveStudio - .exe bouwen (alles in een)
echo ============================================
echo    DraveStudio - een zelfstandige .exe bouwen
echo    (alles in een bestand)
echo ============================================
echo.
cd /d "%~dp0"

set "PY="
for %%V in (3.13 3.12 3.11 3.10) do (
    if not defined PY ( py -%%V -c "import sys" >nul 2>&1 && set "PY=py -%%V" )
)
if not defined PY ( where python >nul 2>&1 && set "PY=python" )
if not defined PY (
    echo [FOUT] Geen geschikte Python gevonden.
    echo   Installeer Python 3.12 van https://www.python.org/downloads/
    pause & exit /b 1
)
echo Gekozen Python: %PY%

if exist ".build-venv\Scripts\python.exe" ( ".build-venv\Scripts\python.exe" -c "import PyQt6, PIL, numpy" >nul 2>&1 || ( echo Oude bouw-omgeving opruimen... & rmdir /s /q .build-venv 2>nul ) )

if not exist ".build-venv\Scripts\python.exe" ( echo [1/3] Bouw-omgeving aanmaken... & %PY% -m venv .build-venv )
set "VPY=.build-venv\Scripts\python.exe"

echo [2/3] Benodigdheden installeren (eerste keer duurt even)...
"%VPY%" -m pip install --upgrade pip >nul
"%VPY%" -m pip install --only-binary=:all: pyinstaller PyQt6 Pillow numpy
if errorlevel 1 (
    echo.
    echo [FOUT] Installeren mislukt.
    echo   Je Python is waarschijnlijk te nieuw ^(bv. 3.14^).
    echo   Installeer Python 3.12 van https://www.python.org/downloads/
    echo   en start dit bestand opnieuw. ^(De bouw-omgeving is opgeruimd.^)
    rmdir /s /q .build-venv 2>nul
    pause & exit /b 1
)
echo [3/3] Een zelfstandige .exe bouwen...
"%VPY%" -m PyInstaller --noconfirm dravestudio.spec
if errorlevel 1 ( echo [FOUT] Bouwen mislukt. & pause & exit /b 1 )
if not exist "dist\DraveStudio.exe" ( echo [FOUT] Geen DraveStudio.exe gevonden na het bouwen. & pause & exit /b 1 )

echo.
echo KLAAR! Een enkel bestand:  dist\DraveStudio.exe
echo (config maakt de app zelf aan naast de .exe.)
echo.
pause
