@echo off

:: Append to hosts file
echo 10.1.15.50 Asguard >> "%windir%\system32\drivers\etc\hosts"

:: Check if successful
if %errorlevel% equ 0 (
    echo Successfully appended entry to hosts file
) else (
    echo Failed to append entry to hosts file
)
