"""Render one demo-video scene: background clip + audio + top tag + timed subtitles.

Subtitles are read from an SRT file and burned in as a sequence of drawtext
filters gated by enable='between(t,start,end)', so each cue's text is sized
and time-boxed independently (avoids depending on libass/fontconfig lookup).

Usage: render_scene.py --bg bg.mp4 --audio voice.mp3 --srt scene.srt
                        --top-tag "Section label" --out scene.mp4 --clips-dir clips/
"""

from __future__ import annotations

import argparse
import pathlib
import re
import subprocess

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def parse_srt_time(value: str) -> float:
    h, m, rest = value.strip().split(":")
    sec, ms = rest.split(",")
    return int(h) * 3600 + int(m) * 60 + int(sec) + int(ms) / 1000


def parse_srt(path: pathlib.Path) -> list[tuple[float, float, str]]:
    blocks = re.split(r"\n\s*\n", path.read_text().strip())
    cues = []
    for block in blocks:
        lines = block.strip().splitlines()
        if len(lines) < 3:
            continue
        start_s, end_s = [t.strip() for t in lines[1].split("-->")]
        text = " ".join(lines[2:])
        cues.append((parse_srt_time(start_s), parse_srt_time(end_s), text))
    return cues


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bg", required=True)
    ap.add_argument("--audio", required=True)
    ap.add_argument("--srt", required=True)
    ap.add_argument("--top-tag", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--clips-dir", required=True)
    args = ap.parse_args()

    clips = pathlib.Path(args.clips_dir)
    out_stem = pathlib.Path(args.out).stem

    top_file = clips / f"_top_{out_stem}.txt"
    top_file.write_text(args.top_tag)

    filters = [
        f"drawtext=textfile={top_file}:fontfile={FONT}:fontcolor=0x58A6FF:fontsize=34:"
        "expansion=none:box=1:boxcolor=black@0.6:boxborderw=14:x=(w-text_w)/2:y=50"
    ]

    cues = parse_srt(pathlib.Path(args.srt))
    for i, (start, end, text) in enumerate(cues):
        cue_file = clips / f"_sub_{out_stem}_{i:02d}.txt"
        cue_file.write_text(text)
        filters.append(
            f"drawtext=textfile={cue_file}:fontfile={FONT}:fontcolor=white:fontsize=36:"
            "expansion=none:box=1:boxcolor=black@0.6:boxborderw=18:x=(w-text_w)/2:y=h-110:"
            f"enable='between(t,{start:.2f},{end:.2f})'"
        )

    vf = ",".join(filters)
    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-i",
        args.bg,
        "-i",
        args.audio,
        "-vf",
        vf,
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "20",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-ar",
        "44100",
        "-ac",
        "1",
        "-b:a",
        "192k",
        "-shortest",
        args.out,
    ]
    subprocess.run(cmd, check=True)
    print(f"  -> {pathlib.Path(args.out).name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
