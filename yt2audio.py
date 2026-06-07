#!/usr/bin/env python3
"""yt2audio - Download YouTube audio with Spotify metadata. Supports playlists."""

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional

import requests


def _run(cmd, timeout=120):
    """Run command, decode output as UTF-8 with error replacement."""
    r = subprocess.run(cmd, capture_output=True, text=False, timeout=timeout)
    stdout = r.stdout.decode("utf-8", errors="replace")
    stderr = r.stderr.decode("utf-8", errors="replace") if r.stderr else ""
    return type("Result", (), {"returncode": r.returncode, "stdout": stdout, "stderr": stderr})()


def check_deps() -> None:
    missing = []
    for dep in ["yt-dlp", "ffmpeg"]:
        if not shutil.which(dep):
            missing.append(dep)
    if not shutil.which("spotdl"):
        missing.append("spotdl")
    if missing:
        print(f"Missing dependencies: {', '.join(missing)}")
        print("Install: pip install yt-dlp spotdl requests  and  ffmpeg")
        sys.exit(1)


def sanitize(name: str) -> str:
    return re.sub(r'[\\/*?:"<>|]', "", name).strip() or "untitled"


def get_tracks(url: str) -> list[dict]:
    r = _run(["spotdl", "save", url, "--save-file", "-"], timeout=120)
    if r.returncode:
        print("SpotDL error:", r.stderr or r.stdout)
        sys.exit(1)
    normalized = r.stdout.replace("\r\n", "\n")
    idx = normalized.find("[")
    if idx == -1:
        print("Error: no JSON in spotdl output")
        sys.exit(1)
    return json.loads(normalized[idx:])


def resolve_yt(spotify_url: str) -> Optional[str]:
    r = _run(["spotdl", "url", "--", spotify_url], timeout=120)
    if r.returncode:
        return None
    for line in r.stdout.strip().split("\n")[::-1]:
        if line.strip().startswith("http"):
            return line.strip()
    return None


def dl_audio(youtube_url: str, fmt: str, quality: str, out_dir: Path) -> Optional[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    templ = str(out_dir / "%(title)s.%(ext)s")
    marker = "__FILE__:"
    cmd = [
        "yt-dlp", "-x", "--audio-format", fmt,
        "--audio-quality", quality, "--newline",
        "-o", templ, "--no-playlist", "--no-embed-thumbnail",
        "--no-add-metadata", "--exec", f"echo {marker}{{}}",
        "--", youtube_url,
    ]
    stdout_lines = []
    r = subprocess.run(cmd, capture_output=True, text=False, timeout=300)
    stderr = r.stderr.decode("utf-8", errors="replace")
    for line in stderr.split("\n"):
        line = line.strip()
        if line:
            print(f"  {line}")
    stdout = r.stdout.decode("utf-8", errors="replace")
    if r.returncode:
        return None
    for line in stdout.split("\n"):
        if marker in line:
            return Path(line.split(marker, 1)[1].strip().strip('"'))
    return None


def download_cover(url: str) -> Optional[Path]:
    tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        tmp.write(r.content)
        tmp.close()
        return Path(tmp.name)
    except Exception:
        tmp.close()
        Path(tmp.name).unlink(missing_ok=True)
        return None


def embed_meta(audio: Path, meta: dict, cover: Optional[Path], fmt: str) -> Path:
    stem = f"{sanitize(meta['title'])} - {sanitize(meta['artist'])}"
    out = audio.parent / f"{stem}{audio.suffix}"
    cmd = ["ffmpeg", "-y", "-i", str(audio)]
    if cover and cover.exists():
        cmd += ["-i", str(cover)]
    cmd += ["-map", "0:a", "-c:a", "copy"]
    if cover and cover.exists():
        cmd += ["-map", "1", "-c:v", "copy", "-disposition:v", "attached_pic"]
    cmd += [
        "-metadata", f"title={meta['title']}",
        "-metadata", f"artist={meta['artist']}",
        "-metadata", f"album={meta['album']}",
        "-metadata", f"date={meta['year']}",
    ]
    if fmt == "mp3":
        cmd += ["-id3v2_version", "3"]
    cmd.append(str(out))
    subprocess.run(cmd, check=True, timeout=30)
    audio.unlink(missing_ok=True)
    return out


def process_track(t: dict, fmt: str, quality: str, out_dir: Path) -> bool:
    print(f"\n  {t['artist']} - {t['name']}")
    yt_url = resolve_yt(t["url"])
    if not yt_url:
        print(f"  [!] Could not find YouTube match, skipping")
        return False

    cover = download_cover(t["cover_url"]) if t.get("cover_url") else None

    meta = {
        "title": t["name"],
        "artist": t["artist"],
        "album": t["album_name"],
        "year": str(t["year"]),
    }

    audio = dl_audio(yt_url, fmt, quality, out_dir)
    if not audio:
        print("  [!] Download failed, skipping")
        if cover:
            cover.unlink(missing_ok=True)
        return False

    embed_meta(audio, meta, cover, fmt)
    if cover:
        cover.unlink(missing_ok=True)
    return True


def main() -> None:
    p = argparse.ArgumentParser(
        description="yt2audio - YouTube audio + Spotify metadata",
    )
    p.add_argument("spotify_url", help="Spotify track/playlist/album URL")
    p.add_argument("youtube_url", nargs="?", help="YouTube URL (optional for single tracks)")
    p.add_argument("-f", "--format", choices=["mp3", "m4a"], default="m4a")
    p.add_argument("-q", "--quality", default="192",
                   help="Audio quality (e.g. 128, 192, 320, or 0 for best)")
    p.add_argument("-o", "--output", default=".")
    args = p.parse_args()

    check_deps()
    tracks = get_tracks(args.spotify_url)
    print(f"Found {len(tracks)} track(s)")

    out_dir = Path(args.output).resolve()

    # Single track with explicit YouTube URL
    if len(tracks) == 1 and args.youtube_url:
        t = tracks[0]
        print(f"\n  {t['artist']} - {t['name']}")
        cover = download_cover(t["cover_url"]) if t.get("cover_url") else None
        meta = {
            "title": t["name"], "artist": t["artist"],
            "album": t["album_name"], "year": str(t["year"]),
        }
        audio = dl_audio(args.youtube_url, args.format, args.quality, out_dir)
        if audio:
            out = embed_meta(audio, meta, cover, args.format)
            print(f"Done: {out}")
        if cover:
            cover.unlink(missing_ok=True)
        return

    # Playlist / auto-search
    success = 0
    for t in tracks:
        if process_track(t, args.format, args.quality, out_dir):
            success += 1

    print(f"\nDone! {success}/{len(tracks)} downloaded.")


if __name__ == "__main__":
    main()
