@echo off
title yt2audio
echo yt2audio - Download songs with Spotify metadata
echo ===============================================
echo.

where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [^!] Python is not installed!
    echo     Download from: https://python.org
    pause
    exit /b 1
)

where ffmpeg >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [^!] FFmpeg is not installed!
    echo     Run: winget install FFmpeg
    echo     Or download: https://ffmpeg.org
    pause
    exit /b 1
)

echo [*] Installing/updating Python packages...
pip install -q spotdl yt-dlp requests yt-dlp-ejs

echo.
python "%~dp0yt2audio.py" %*
echo.
pause
