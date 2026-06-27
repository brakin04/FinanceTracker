@echo off
setlocal enabledelayedexpansion

cls
echo =====================================
echo Checking and installing dependencies...
echo =====================================
pip install -r requirements.txt

set FLASK_APP=app.py

:start
echo --- Starting Finance Application ---
start "Finance App Engine" flask run --port=5050

echo Application started on port 5050!
echo Commands: [r] Restart ^| [q] Quit

:loop
set /p user_input="> "

if /i "%user_input%"=="r" (
    echo Restarting Finance Application...
    
    for /f "tokens=5" %%P in ('netstat -aon ^| findstr :5050 ^| findstr LISTENING') do (
        taskkill /pid %%P /f /t >nul 2>&1
    )
    
    timeout /t 1 >nul
    goto start
)

if /i "%user_input%"=="q" (
    echo Exiting...
    
    for /f "tokens=5" %%P in ('netstat -aon ^| findstr :5050 ^| findstr LISTENING') do (
        taskkill /pid %%P /f /t >nul 2>&1
    )
    exit /b 0
)

goto loop
