@echo off

:: Append to hosts file
echo Unable to detect public IP address (/32 mask). Asguard >> "%windir%\system32\drivers\etc\hosts"

:: Check if successful
if %errorlevel% equ 0 (
    echo Successfully appended entry to hosts file
) else (
    echo Failed to append entry to hosts file
)
