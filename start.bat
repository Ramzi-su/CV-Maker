@echo off
setlocal enabledelayedexpansion

echo ======================================================
echo         Demarrage de CV-Maker (React + LaTeX)
echo ======================================================

set "ROOT_DIR=%~dp0"

:: 1. Verification & Preparation Backend
echo.
echo [1/3] Verification du backend Python...
cd /d "%ROOT_DIR%backend"

if not exist ".venv" (
    echo Creation de l'environnement virtuel Python...
    python -m venv .venv
)

call .venv\Scripts\activate.bat
pip install -q -r requirements.txt

:: 2. Verification & Preparation Frontend
echo.
echo [2/3] Verification du frontend React...
cd /d "%ROOT_DIR%frontend"

if not exist "node_modules" (
    echo Installation des dependances npm...
    call npm install
)

:: 3. Lancement des serveurs
echo.
echo [3/3] Lancement des services...

start "CV-Maker Backend" cmd /c "cd /d "%ROOT_DIR%backend" && call .venv\Scripts\activate.bat && uvicorn app.main:app --host 127.0.0.1 --port 8000"
start "CV-Maker Frontend" cmd /c "cd /d "%ROOT_DIR%frontend" && npm run dev -- --host 127.0.0.1 --port 5173"

timeout /t 2 /nobreak >nul

echo.
echo ======================================================
echo  CV-Maker est pret !
echo  - Application Web React : http://localhost:5173
echo  - Documentation API     : http://localhost:8000/docs
echo ======================================================
echo Les serveurs tournent dans les fenetres dediees.
echo Fermez ces fenetres pour arreter les serveurs.
echo.
pause
