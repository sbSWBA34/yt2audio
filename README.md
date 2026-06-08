# yt2audio

Download any song from YouTube with full Spotify metadata — title, artist, album, cover art. Works with single tracks, playlists, and albums.

## How it works

You type a song name (or Spotify URL). yt2audio looks it up on Spotify, finds the matching video on YouTube, downloads the audio, and tags it with the correct title, artist, album, and album art.

## Requirements

- **Python 3** (get it from https://python.org)
- **FFmpeg** (install with `winget install FFmpeg` or download from https://ffmpeg.org)

## Install & Use (Windows)

**1. Install FFmpeg**

Open Command Prompt and run:
```
winget install FFmpeg
```

**2. Download yt2audio**

Go to https://github.com/sbSWBA34/yt2audio, click the green **Code** button, then **Download ZIP**. Extract the ZIP to a folder called `yt2audio` on your Desktop.

**3. Use it**

Open the `yt2audio` folder on your Desktop. Click the address bar at the top, type `cmd`, and press Enter. Then type:
```
yt2audio "artist name - song name"
```

The first time you run it, it will automatically install the required Python packages.

### Make it work from anywhere (optional)

If you don't want to open cmd in the folder every time:

1. Open the `yt2audio` folder on your Desktop
2. Click the address bar (white bar at the top showing the folder path)
3. Copy the path (Ctrl+C)
4. Press Win + R, type `sysdm.cpl`, press Enter
5. Go to the **Advanced** tab, click **Environment Variables**
6. Under **System variables**, find `Path`, click **Edit**
7. Click **New**, paste the path (Ctrl+V), click **OK** on all windows
8. Open a new Command Prompt — now `yt2audio` works from anywhere

## Commands

```
yt2audio "song name"
yt2audio https://open.spotify.com/track/...
yt2audio https://open.spotify.com/playlist/...
yt2audio https://open.spotify.com/album/...
yt2audio "song name" https://youtu.be/...
```

### Options
- `-f mp3` — output format (default: m4a)
- `-q 320` — audio quality (default: 192, use `0` for best)
- `-o ./music` — output folder (default: Desktop\yt2audio)
