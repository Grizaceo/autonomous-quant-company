#!/usr/bin/env bash
# Compose AQTC hackathon demo video.
set -eu
cd "$(dirname "$0")/../../.."

REPO=$(pwd)
CLIPS="$REPO/docs/demo-video/clips"
VOICE="$REPO/docs/demo-video/voice"
OUT="$REPO/docs/demo-video/aqtc_demo.mp4"
mkdir -p "$(dirname "$OUT")"

W=1280
H=720
FONT=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf

get_dur () { ffprobe -v error -select_streams a:0 -show_entries stream=duration -of default=noprint_wrappers=1:nokey=1 "$1"; }

render_bg_color () {
  local color="$1" duration="$2" out="$3"
  ffmpeg -hide_banner -loglevel error -y \
    -f lavfi -i "color=c=${color}:s=${W}x${H}:d=${duration}:r=24" "$out"
}

render_bg_frame () {
  local image="$1" duration="$2" out="$3"
  ffmpeg -hide_banner -loglevel error -y \
    -loop 1 -t "$duration" -i "$image" \
    -vf "scale=${W}:${H}:force_original_aspect_ratio=decrease,pad=${W}:${H}:(ow-iw)/2:(oh-ih)/2:color=black,format=yuv420p" \
    -r 24 "$out"
}

render_scene () {
  local bg="$1" audio="$2" caption_text="$3" out="$4"
  local capfile="$CLIPS/_cap_$(basename "$out" .mp4).txt"
  printf '%s' "$caption_text" > "$capfile"
  ffmpeg -hide_banner -loglevel error -y \
    -i "$bg" -i "$audio" \
    -vf "drawtext=textfile=${capfile}:fontfile=${FONT}:fontcolor=white:fontsize=34:box=1:boxcolor=black@0.55:boxborderw=14:x=(w-text_w)/2:y=h-86" \
    -c:v libx264 -preset medium -crf 22 -pix_fmt yuv420p \
    -c:a aac -b:a 160k \
    -shortest "$out"
  echo "  -> $(basename "$out")  $(ffprobe -v error -select_streams v:0 -show_entries stream=duration -of default=noprint_wrappers=1:nokey=1 "$out")s"
}

# Compute durations (raw voice + 0.4s tail)
A1=$(get_dur "$VOICE/scene1_hook.mp3")
A2=$(get_dur "$VOICE/scene2_origin.mp3")
A3=$(get_dur "$VOICE/scene3_falsify.mp3")
A4=$(get_dur "$VOICE/scene4_business.mp3")
A5=$(get_dur "$VOICE/scene5_close.mp3")
D1=$(printf "%.1f" "$(echo "$A1 + 0.4" | bc -l)")
D2=$(printf "%.1f" "$(echo "$A2 + 0.4" | bc -l)")
D3=$(printf "%.1f" "$(echo "$A3 + 0.4" | bc -l)")
D4=$(printf "%.1f" "$(echo "$A4 + 0.4" | bc -l)")
D5=$(printf "%.1f" "$(echo "$A5 + 0.4" | bc -l)")
echo "Durations s: scene1=$D1 scene2=$D2 scene3=$D3 scene4=$D4 scene5=$D5"

echo "[1] black title card"
render_bg_color black "$D1" "$CLIPS/scene1_bg.mp4"
render_scene "$CLIPS/scene1_bg.mp4" "$VOICE/scene1_hook.mp3" "AQTC :: Hackathon submission" "$CLIPS/scene1.mp4"

echo "[2] dashboard (HGAT+ES provenance)"
render_bg_frame "$CLIPS/dashboard.png" "$D2" "$CLIPS/scene2_bg.mp4"
render_scene "$CLIPS/scene2_bg.mp4" "$VOICE/scene2_origin.mp3" "Frozen HGAT+ES v4 walkforward evidence" "$CLIPS/scene2.mp4"

echo "[3] provenance dashboard (rejected candidate)"
render_bg_frame "$CLIPS/provenance_api.png" "$D3" "$CLIPS/scene3_bg.mp4"
render_scene "$CLIPS/scene3_bg.mp4" "$VOICE/scene3_falsify.mp3" "Falsification: rejected 2019+ ensemble" "$CLIPS/scene3.mp4"

echo "[4] status (regime + ledger)"
render_bg_frame "$CLIPS/status_api.png" "$D4" "$CLIPS/scene4_bg.mp4"
render_scene "$CLIPS/scene4_bg.mp4" "$VOICE/scene4_business.mp3" "Business loop: policy gate + Nemotron + Stripe" "$CLIPS/scene4.mp4"

echo "[5] dashboard close"
render_bg_frame "$CLIPS/dashboard.png" "$D5" "$CLIPS/scene5_bg.mp4"
render_scene "$CLIPS/scene5_bg.mp4" "$VOICE/scene5_close.mp3" "From evolved alpha to invoice." "$CLIPS/scene5.mp4"

echo "[concat]"
LIST=$(mktemp)
for i in 1 2 3 4 5; do echo "file '$CLIPS/scene${i}.mp4'" >> "$LIST"; done
ffmpeg -hide_banner -loglevel error -y -f concat -safe 0 -i "$LIST" -c:v copy -c:a aac -b:a 160k "$OUT"
rm -f "$LIST"

TOTAL=$(ffprobe -v error -select_streams v:0 -show_entries stream=duration -of default=noprint_wrappers=1:nokey=1 "$OUT")
SIZE=$(stat -c '%s' "$OUT")
echo "DONE: $OUT  duration=${TOTAL}s  size=${SIZE} bytes"
