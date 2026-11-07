@echo off
title HireSphere - KTU Mini Project
echo ========================================================
echo   Starting HireSphere - KTU CS Mini Project Platform
echo ========================================================
echo.

cd /d "%~dp0django_backend"

set PY_CMD=
where python >nul 2>nul
if %errorlevel% equ 0 (
    set PY_CMD=python
) else (
    where py >nul 2>nul
    if %errorlevel% equ 0 (
        set PY_CMD=py
    ) else if exist "C:\Python314\python.exe" (
        set PY_CMD="C:\Python314\python.exe"
    )
)

if "%PY_CMD%"=="" (
    echo [ERROR] Python was not found in PATH or C:\Python314\python.exe.
    echo Please ensure Python is installed.
    pause
    exit /b 1
)

echo [OK] Using Python: %PY_CMD%
echo [OK] Starting Django server at http://127.0.0.1:8000/ ...
echo.

start "" "http://127.0.0.1:8000/"

%PY_CMD% manage.py runserver 127.0.0.1:8000

if %errorlevel% neq 0 (
    echo.
    echo [WARNING] Server stopped with error code %errorlevel%.
)

pause
