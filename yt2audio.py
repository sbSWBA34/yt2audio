#!/usr/bin/env python3
"""yt2audio - Download YouTube audio with Spotify metadata. Supports playlists."""

import argparse, json, subprocess, sys, tempfile, re
from pathlib import Path

import requests


def get_tracks(url):
    r = subprocess.run(
        ["spotdl", "save", url, "--save-file", "-"],
        capture_output=True, text=True, timeout=120,
    )
    if r.returncode:
        print("SpotDL error:", r.stderr or r.stdout); sys.exit(1)
    idx = r.stdout.find("[")
    if idx == -1:
        print("Error: no JSON in spotdl output"); sys.exit(1)
    return json.loads(r.stdout[idx:])


def resolve_yt(spotify_url):
    r = subprocess.run(
        ["spotdl", "url", spotify_url],
        capture_output=True, text=True, timeout=60,
    )
    if r.returncode:
        return None
    for line in r.stdout.strip().split("\n")[::-1]:
        if line.strip().startswith("http"):
            return line.strip()
    return None


def dl_audio(youtube_url, fmt, out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    templ = str(out_dir / "%(title)s.%(ext)s")
    marker = "__FILE__:"
    cmd = [
        "yt-dlp", "-x", "--audio-format", fmt, "--audio-quality", "192",
        "-o", templ, "--no-playlist", "--no-embed-thumbnail",
        "--no-add-metadata", "--exec", f"echo {marker}{{}}",
        youtube_url,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    if r.returncode:
        print(r.stderr); return None
    for line in r.stdout.split("\n"):
        if marker in line:
            return Path(line.split(marker, 1)[1].strip().strip('"'))
    return None


def embed_meta(audio, meta, cover, fmt):
    stem = f"{meta['title']} - {meta['artist']}"
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


def process_track(t, fmt, out_dir):
    print(f"\n  {t['artist']} - {t['name']}")
    yt_url = resolve_yt(t["url"])
    if not yt_url:
        print(f"  [!] Could not find YouTube match, skipping")
        return False

    cover = None
    if t.get("cover_url"):
        cover = Path(tempfile.mktemp(suffix=".jpg"))
        try:
            r = requests.get(t["cover_url"], timeout=10)
            r.raise_for_status(); cover.write_bytes(r.content)
        except:
            cover = None

    meta = {
        "title": t["name"],
        "artist": t["artist"],
        "album": t["album_name"],
        "year": str(t["year"]),
    }

    audio = dl_audio(yt_url, fmt, out_dir)
    if not audio:
        print(f"  [!] Download failed, skipping")
        if cover and cover.exists(): cover.unlink()
        return False

    embed_meta(audio, meta, cover, fmt)
    if cover and cover.exists(): cover.unlink()
    return True


def main():
    p = argparse.ArgumentParser(
        description="yt2audio - YouTube audio + Spotify metadata",
    )
    p.add_argument("spotify_url", help="Spotify track/playlist/album URL")
    p.add_argument("youtube_url", nargs="?", help="YouTube URL (optional for single tracks)")
    p.add_argument("-f", "--format", choices=["mp3", "m4a"], default="m4a")
    p.add_argument("-o", "--output", default=".")
    args = p.parse_args()

    tracks = get_tracks(args.spotify_url)
    print(f"Found {len(tracks)} track(s)")

    out_dir = Path(args.output).resolve()

    # Single track with explicit YouTube URL
    if len(tracks) == 1 and args.youtube_url:
        t = tracks[0]
        print(f"\n  {t['artist']} - {t['name']}")
        cover = None
        if t.get("cover_url"):
            cover = Path(tempfile.mktemp(suffix=".jpg"))
            try:
                r = requests.get(t["cover_url"], timeout=10)
                r.raise_for_status(); cover.write_bytes(r.content)
            except:
                cover = None
        meta = {
            "title": t["name"], "artist": t["artist"],
            "album": t["album_name"], "year": str(t["year"]),
        }
        audio = dl_audio(args.youtube_url, args.format, out_dir)
        if audio:
            embed_meta(audio, meta, cover, args.format)
        if cover and cover.exists(): cover.unlink()
        if audio: print(f"Done: {audio.parent / (meta['title'] + ' - ' + meta['artist'] + audio.suffix)}")
        return

    # Playlist or single track (auto-search YouTube)
    success = 0
    for t in tracks:
        if process_track(t, args.format, out_dir):
            success += 1

    print(f"\nDone! {success}/{len(tracks)} downloaded.")


if __name__ == "__main__":
    main()
