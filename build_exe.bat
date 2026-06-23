@echo off
title Building RestaurantManager...
color 0A

:: Change to the directory where this batch file is located
cd /d "%~dp0"

echo ======================================
echo    RestaurantManager Build Script
echo ======================================
echo.

if not exist "icon.ico" (
    color 0C
    echo ERROR: icon.ico not found in the root folder!
    echo Please place your icon.ico next to this bat file.
    pause
    exit /b
)

echo [1/7] Checking Python...

python --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo ERROR: Python is not installed or not in PATH!
    pause
    exit /b
)

echo.
echo [2/7] Checking virtual environment...

if not exist "venv\Scripts\activate.bat" (
    echo Virtual environment not found. Creating venv...
    python -m venv venv

    if errorlevel 1 (
        color 0C
        echo ERROR: Failed to create virtual environment!
        pause
        exit /b
    )
) else (
    echo Virtual environment found. Skipping creation.
)

echo.
echo [3/7] Activating virtual environment...

call "venv\Scripts\activate.bat"

if errorlevel 1 (
    color 0C
    echo ERROR: Failed to activate virtual environment!
    pause
    exit /b
)

echo.
echo [4/7] Installing requirements.txt...

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if errorlevel 1 (
    color 0C
    echo ERROR: Failed to install requirements!
    pause
    exit /b
)

echo.
echo [5/7] Checking PyInstaller...

python -m pip show pyinstaller >nul 2>&1

if errorlevel 1 (
    echo PyInstaller is not installed.
    echo Installing PyInstaller...
    python -m pip install --upgrade pyinstaller

    if errorlevel 1 (
        color 0C
        echo ERROR: Failed to install PyInstaller!
        pause
        exit /b
    )
)

echo.
echo [6/7] Cleaning old build files...

if exist "build" rd /s /q "build"
if exist "dist" rd /s /q "dist"
if exist "RestaurantManager.exe" del /f /q "RestaurantManager.exe"
if exist __pycache__ rmdir /s /q __pycache__
if exist restaurant_system\__pycache__ rmdir /s /q restaurant_system\__pycache__

echo.
echo [7/7] Building EXE from main.spec...
echo.

pyinstaller --noconfirm --clean --log-level INFO main.spec

if errorlevel 1 (
    echo.
    color 0C
    echo ========================================
    echo              BUILD FAILED
    echo ========================================
    echo Please check the error message above.
    pause
    exit /b
)

echo.
echo ========================================
echo      BUILD COMPLETED SUCCESSFULLY
echo ========================================
echo.
echo EXE Location:
echo dist\RestaurantManager\RestaurantManager.exe
echo.

pause
