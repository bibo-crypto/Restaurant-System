@echo off
title Building RestaurantManager...
color 0A

:: Change to the directory where this batch file is located
cd /d "%~dp0"

echo ======================================
echo    RestaurantManager Build Script
echo ======================================
echo.

echo [1/5] Checking for PyInstaller...

if not exist "icon.ico" (
    color 0C
    echo ERROR: icon.ico not found in the root folder!
    echo Please place your icon.ico next to this bat file.
    pause
    exit /b
)

pip show pyinstaller >nul 2>&1

if %errorlevel% neq 0 (
    echo PyInstaller is not installed.
    echo Installing PyInstaller...
    pip install pyinstaller

    if %errorlevel% neq 0 (
        echo Failed to install PyInstaller!
        pause
        exit /b
    )
)

echo.
echo [2/5] Cleaning old build files...
if exist "build" rd /s /q "build"
if exist "dist" rd /s /q "dist"
if exist "RestaurantManager.exe" del /f /q "RestaurantManager.exe"

echo.
echo [3/5] Removing old spec cache...

if exist __pycache__ rmdir /s /q __pycache__

echo.
echo [4/5] Building EXE from main.spec...
echo.
:: Added --log-level DEBUG to see exactly what fails
pyinstaller --noconfirm --clean --log-level INFO main.spec

if %errorlevel% neq 0 (
    echo.
    color 0C
    echo ERROR: Build failed. Please check the error message above.
    pause
    exit /b
)

echo.
echo [5/5] Build Completed Successfully!
echo.

echo EXE Location:
echo dist\RestaurantManager\RestaurantManager.exe

echo.
pause
