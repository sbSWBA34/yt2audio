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
- `-o ./music` — output directory (default: current dir)

## Requirements

- Python 3
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [FFmpeg](https://ffmpeg.org/)
- [spotdl](https://github.com/spotDL/spotify-downloader)
- `requests` (Python package)

## Install

1. Install Python dependencies:
   ```
   pip install spotdl yt-dlp requests
   ```
2. Install FFmpeg
3. Add `yt2audio.py` to your PATH
