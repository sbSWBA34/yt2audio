# yt2audio

Download YouTube audio with Spotify metadata (title, artist, album, cover art). Supports single tracks and playlists.

## Usage

```
yt2audio <spotify_url> [youtube_url]
```

**Single track — auto-search YouTube:**
```
yt2audio https://open.spotify.com/track/...
```

**Single track — specify YouTube URL:**
```
yt2audio https://open.spotify.com/track/... https://youtu.be/...
```

**Playlist or album — auto-search all tracks:**
```
yt2audio https://open.spotify.com/playlist/...
yt2audio https://open.spotify.com/album/...
```

**Options:**
- `-f mp3` — output format (default: m4a)
- `-q 320` — audio quality in kbps (default: 192, use `0` for best)
- `-o ./music` — output directory (default: Desktop/yt2audio)

## Requirements

- Python 3
- FFmpeg (https://ffmpeg.org/)

## Install — Windows

1. Install FFmpeg:
   ```
   winget install FFmpeg
   ```
2. Download `yt2audio.bat` and `yt2audio.py` to the same folder
3. Run:
   ```
   yt2audio https://open.spotify.com/track/...
   ```
   (Dependencies auto-install on first run)

Or add the folder to your PATH to use `yt2audio` from anywhere.

## Install — macOS

1. Install Homebrew + FFmpeg:
   ```
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   brew install ffmpeg
   ```
2. Download `yt2audio.py` and `yt2audio.sh`:
   ```
   chmod +x yt2audio.sh
   sudo cp yt2audio.sh /usr/local/bin/yt2audio
   sudo cp yt2audio.py /usr/local/bin/
   ```
3. Install Python deps:
   ```
   pip3 install spotdl yt-dlp requests
   ```
