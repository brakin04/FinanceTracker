@echo off
:start
for /f %%a in ('echo prompt $E^| cmd') do set "ESC=%%a"
echo --- Starting Finance Application ---
start /b python run.py
echo Commands: [r] Restart ^| [q] Quit:
:set
set "input="
set /p input=

if /i "%input%"=="r" (
    echo %ESC%[93mRestarting...%ESC%[0m
    taskkill /f /im python.exe >nul 2>&1
    goto start
)
if /i "%input%"=="q" (
    taskkill /f /im python.exe >nul 2>&1
    echo %ESC%[91mApplication stopped. Returning to prompt...%ESC%[0m
    cmd /k
)
goto set