@echo off
chcp 65001 >nul
title DraveStudio
cd /d "%~dp0"
set "LOG=%~dp0run-log.txt"

set "PY="
for %%V in (3.13 3.12 3.11 3.10) do (
    if not defined PY ( py -%%V -c "import sys" >nul 2>&1 && set "PY=py -%%V" )
)
if not defined PY ( where python >nul 2>&1 && set "PY=python" )
if not defined PY (
    echo Geen geschikte Python gevonden. Installeer Python 3.12 van https://www.python.org/downloads/
    pause & exit /b 1
)

if exist ".venv\Scripts\python.exe" ( ".venv\Scripts\python.exe" -c "import PyQt6, PIL" >nul 2>&1 || ( echo Oude omgeving opruimen... & rmdir /s /q .venv 2>nul ) )

if not exist ".venv\Scripts\python.exe" (
    echo Eenmalige installatie ^(dit duurt even^)...
    %PY% -m venv .venv
    ".venv\Scripts\python.exe" -m pip install --upgrade pip >> "%LOG%" 2>&1
    ".venv\Scripts\python.exe" -m pip install --only-binary=:all: -r requirements.txt >> "%LOG%" 2>&1
    if errorlevel 1 (
        echo [FOUT] Installeren mislukt. Zie run-log.txt.
        echo   Tip: is je Python te nieuw, installeer Python 3.12 en verwijder de map .venv
        pause & exit /b 1
    )
)

echo DraveStudio wordt gestart...
".venv\Scripts\pythonw.exe" dravestudio.py
