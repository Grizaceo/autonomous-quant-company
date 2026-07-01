# AQTC Hackathon Demo Video

Final deliverables for the NVIDIA × Stripe × Nous Hermes Agent hackathon demo.
All assets live in this directory. The shipped artifact is `aqtc_demo.mp4`.

## Final artifact

- `aqtc_demo.mp4` — H.264 1920×1080, AAC 44.1 kHz mono, ~95 s (1:35),
  voice-over + full timed subtitles + section tag overlay + 0.35 s crossfades
  between scenes. Plays inside any browser.
- Every spoken word is captioned (not just a one-line caption per scene) — added
  after judge feedback that the TTS voice is hard to follow when it pronounces
  acronyms and numbers. Subtitle timing was derived with `whisper` word-level
  timestamps; subtitle text is the verified script (numbers shown as exact
  decimals, e.g. `3.255`, not the spoken-rounded `three point two six`).
- All six scenes are rendered from one dark-theme HTML/CSS design system
  (`clips/theme.css`) instead of a mix of designed slides and raw light-mode
  screenshots — the earlier cut mixed `flow_slide`/`financial_lab_explainer`
  (designed, dark) with live screenshots of the dashboard and raw `/provenance`
  and `/status` JSON (light, and captured with Playwright's `full_page=True`,
  which produced a 3840×4776 image that letterboxed into a thin, mostly-blank
  column at 1920×1080). Every scene is now a fixed 1920×1080 slide sharing the
  same background, card, and color tokens, so scene-to-scene cuts read as one
  video instead of stitched-together captures.

## Source assets (regenerable)

- `voice/SCRIPT.md` — 6-scene narration script and timing targets.
- `voice/scene{1,1b,2,3,4,5}_*.txt` — per-scene voiceover source (verbatim)
- `voice/scene{1,1b,2,3,4,5}_*.mp3` — per-scene TTS (Microsoft Edge `en-US-GuyNeural`)
- `clips/clip1_provenance.gif` — `asciinema` → `agg` recording of the live
  `aqtc provenance / regime / report` demo (kept as a source asset; not
  currently composited into a scene)
- `clips/theme.css` — shared design tokens (dark background, card/step/metric
  styles, color coding) for all six slide HTML files below
- `clips/flow_slide.html` / `.png` — opening flow infographic (scene 1 background)
- `clips/financial_lab_explainer.html` / `.png` — "Financial Lab vs AQTC: what's
  what" infographic clarifying that Financial Lab is a separate, open-source
  research repo and AQTC (this repo) operates the business (scene 1b background)
- `clips/scene2_hgat_es.html` / `.png` — HGAT+ES v4 architecture + walkforward
  metrics slide (scene 2 background)
- `clips/scene3_falsification.html` / `.png` — rejected-vs-accepted comparison
  card (scene 3 background)
- `clips/scene4_business_loop.html` / `.png` — policy gate → Nemotron → Stripe
  ledger → paper portfolio flow (scene 4 background)
- `clips/scene5_close.html` / `.png` — closing recap slide, bookends scene 1
  (scene 5 background)
- `clips/scene{1,1b,2,3,4,5}.srt` — full per-scene subtitle cues (text + timing)
- `clips/scene{1,1b,2,3,4,5}.mp4` — per-scene composite (image + audio + captions)
- `clips/scene{1,1b,2,3,4,5}_bg.mp4` — per-scene background loop (image-only)
- `recordings/aqtc_demo_provenance.cast` — raw asciicast (replayable in
  `asciinema play`)
- `clips/report.md` — output of `aqtc report --out` (frozen ledger)
- `scripts/demo_provenance.sh` — recorded shell session
- `scripts/capture_dashboard.py` — Playwright capture script for live
  dashboard/API screenshots; general-purpose utility, no longer part of the
  video build (see design-system note above)
- `scripts/capture_html_slide.py` — Playwright capture script (all six slide
  HTML files → fixed 1920×1080 PNG, `device_scale_factor=2` for crisp text)
- `scripts/render_scene.py` — per-scene compositor: burns in the section tag +
  timed subtitle cues from an `.srt` file as a chain of `drawtext` filters;
  pads audio to the background's exact duration (`--duration`, `apad`) instead
  of trimming with `-shortest`, so each scene keeps a quiet tail for the
  crossfade below
- `scripts/concat_with_transitions.py` — final assembly: chains the six scene
  clips with `xfade`/`acrossfade` (0.35 s) instead of a hard-cut `concat` demuxer
- `scripts/compose.sh` — orchestrates the full pipeline (backgrounds → per-scene
  render → transitioned concat)

## Reproduce

```bash
cd docs/demo-video/scripts
python3 capture_html_slide.py \
  ../clips/flow_slide.html \
  ../clips/financial_lab_explainer.html \
  ../clips/scene2_hgat_es.html \
  ../clips/scene3_falsification.html \
  ../clips/scene4_business_loop.html \
  ../clips/scene5_close.html        # all six slides -> PNG
asciinema rec -c demo_provenance.sh \
  ../recordings/aqtc_demo_provenance.cast  # terminal recording (source asset only)
edge-tts --voice en-US-GuyNeural \
  --file ../voice/scene1_hook.txt \
  --write-media ../voice/scene1_hook.mp3   # x6 (one per scene, incl. scene1b)
agg ../recordings/aqtc_demo_provenance.cast \
  ../clips/clip1_provenance.gif
./compose.sh                                # final assembly (captions + crossfades)
```

Subtitle cues in `clips/scene*.srt` are hand-verified against `voice/SCRIPT.md`
(timing scaffolded from `whisper --word_timestamps True`, text corrected to the
canonical script — TTS/STT mishears acronyms and numbers). If voice-over wording
changes, regenerate timestamps and re-check cue text before re-running `compose.sh`.
If slide content changes, edit the relevant `clips/scene*.html` (or `theme.css`
for a system-wide style change) and re-run `capture_html_slide.py` before
`compose.sh`.

## Timing per scene

| # | Visual                                        | Duration | Section tag                                                          |
|---|------------------------------------------------|----------|------------------------------------------------------------------------|
| 1  | flow_slide.png (opening infographic)           | 14.4 s   | "From evolved alpha to invoice"                                       |
| 1b | financial_lab_explainer.png                    | 16.1 s   | "What is Financial Lab?"                                               |
| 2  | scene2_hgat_es.png (architecture + metrics)    | 20.7 s   | "Financial Lab: Heterogeneous Graph Attention + Evolution Strategies" |
| 3  | scene3_falsification.png (rejected vs accepted)| 15.2 s   | "Falsification: 2019+ ensemble rejected"                               |
| 4  | scene4_business_loop.png (policy/Nemotron/ledger)| 23.0 s | "Business loop: policy gate + Nemotron + Stripe ledger"               |
| 5  | scene5_close.png (recap + tagline)             | 7.7 s    | "From evolved alpha to invoice."                                       |

Rendered `aqtc_demo.mp4` runs 95.4 s (1:35) — six scenes at the durations above,
joined by five 0.35 s crossfades (raw sum 97.2 s minus 1.75 s of overlap).
Scene 1b was added so a viewer who only sees the opening "Financial Lab"
infographic card immediately gets a spoken + on-screen explanation that
Financial Lab is a separate, open-source research repo (not part of AQTC's
codebase) before the rest of the demo assumes that context.

## What the demo proves (evidence shown in video)

- Alpha origin: `Financial Lab HGAT+ES v4` — Sharpe **3.255**, 5 folds,
  100 % positive, MaxDD **0.032**. Visual: scene 2 (architecture + metrics slide).
- Falsification: the 2019+ ensemble (Sharpe **-0.544**, MaxDD **0.486**)
  is rejected and surfaced, not buried. Visual: scene 3 (rejected-vs-accepted card).
- Closed loop: NemoClaw-compatible policy gate, Nemotron regime summary,
  Stripe-style ledger with paper rebalance status. Visual: scene 4 (business-loop flow).
- Demo is reproducible end-to-end: every command in the recording is real
  (`aqtc provenance`, `aqtc regime --provider mock`, `aqtc report --out ...`,
  `aqtc status`). No fake prompts, no chart-only bait. All figures on every
  slide are taken verbatim from those commands' live output (see `voice/SCRIPT.md`
  and `data/demo/*.json`), not restated from memory.
