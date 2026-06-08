@echo off
pip install -q spotdl yt-dlp requests
python "%~dp0yt2audio.py" %*
