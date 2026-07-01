"""Concatenate scene clips with short audio/video crossfades instead of hard cuts.

Each input clip already has a silence-padded tail (see render_scene.py's
--duration/apad), so a crossfade shorter than that tail only ever overlaps
quiet background, never two scenes' caption text.

Usage: concat_with_transitions.py --out out.mp4 [--xfade 0.35] clip1.mp4 clip2.mp4 ...
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys


def probe_duration(path: str) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", path],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    return float(json.loads(out)["format"]["duration"])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--xfade", type=float, default=0.35)
    ap.add_argument("clips", nargs="+")
    args = ap.parse_args()

    clips = args.clips
    if len(clips) < 2:
        print("need >= 2 clips", file=sys.stderr)
        return 2

    d = args.xfade
    durations = [probe_duration(c) for c in clips]
    for clip, dur in zip(clips, durations, strict=True):
        if dur <= d * 2:
            print(
                f"{clip}: {dur:.2f}s too short for a {d}s crossfade on both sides", file=sys.stderr
            )
            return 2

    inputs: list[str] = []
    for c in clips:
        inputs += ["-i", c]

    vfilters = []
    afilters = []
    cum = durations[0]
    v_prev, a_prev = "0:v", "0:a"
    last = len(clips) - 1
    for i in range(1, len(clips)):
        v_out = f"v{i}" if i != last else "vout"
        a_out = f"a{i}" if i != last else "aout"
        offset = cum - d
        vfilters.append(
            f"[{v_prev}][{i}:v]xfade=transition=fade:duration={d}:offset={offset:.3f}[{v_out}]"
        )
        afilters.append(f"[{a_prev}][{i}:a]acrossfade=d={d}:c1=tri:c2=tri[{a_out}]")
        cum = cum + durations[i] - d
        v_prev, a_prev = v_out, a_out

    filter_complex = ";".join(vfilters + afilters)

    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        *inputs,
        "-filter_complex",
        filter_complex,
        "-map",
        f"[{v_prev}]",
        "-map",
        f"[{a_prev}]",
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "18",
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
        args.out,
    ]
    subprocess.run(cmd, check=True)
    total = probe_duration(args.out)
    print(
        f"DONE: {args.out} duration={total:.2f}s "
        f"(raw sum={sum(durations):.2f}s, {len(clips) - 1}x{d}s crossfades)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
