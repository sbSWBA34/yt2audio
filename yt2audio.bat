@echo off
pip install -q spotdl yt-dlp requests 2>nul
python "%~dp0yt2audio.py" %*
