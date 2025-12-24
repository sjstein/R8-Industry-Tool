@echo off
echo ========================================
echo Building Run8 Industry Tool Executable
echo ========================================
echo.

REM Use venv Python if it exists, otherwise use system Python
if exist "venv\Scripts\python.exe" (
    set PYTHON=venv\Scripts\python.exe
    echo Using virtual environment Python
) else (
    set PYTHON=python
    echo Using system Python
)

REM Check if pyinstaller is installed
%PYTHON% -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    %PYTHON% -m pip install pyinstaller
    echo.
)

REM Update build date in version.py
echo Updating build date...
%PYTHON% update_version.py
echo.

REM Clean previous builds
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Build the executable using the .spec file (contains all configuration)
echo Building executable...
%PYTHON% -m PyInstaller Run8IndustryTool.spec

echo.
if exist "dist\Run8IndustryTool.exe" (
    echo ========================================
    echo Build successful!
    echo ========================================
    echo.
    echo Executable location: dist\Run8IndustryTool.exe
    echo.
    echo You can distribute the entire 'dist' folder
    echo or just the Run8IndustryTool.exe file.
    echo.
) else (
    echo ========================================
    echo Build failed!
    echo ========================================
    echo Please check the output above for errors.
)

pause
