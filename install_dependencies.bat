@echo off
echo Installing server dependencies...
cd /d "%~dp0"
if exist "server\package.json" (
    cd server
    echo Running npm install in server directory...
    npm install
    if %errorlevel% equ 0 (
        echo Dependencies installed successfully!
    ) else (
        echo Failed to install dependencies.
        exit /b 1
    )
) else (
    echo package.json not found in server directory
    exit /b 1
)
echo Installation complete.
