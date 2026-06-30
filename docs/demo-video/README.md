# AQTC Hackathon Demo Video

Final deliverables for the NVIDIA × Stripe × Nous Hermes Agent hackathon demo.
All assets live in this directory. The shipped artifact is `aqtc_demo.mp4`.

## Final artifact

- `aqtc_demo.mp4` — H.264 1920×1080, AAC 44.1 kHz mono, ~95 s (1:35),
  voice-over + full timed subtitles + section tag overlay. Plays inside any browser.
- Every spoken word is captioned (not just a one-line caption per scene) — added
  after judge feedback that the TTS voice is hard to follow when it pronounces
  acronyms and numbers. Subtitle timing was derived with `whisper` word-level
  timestamps; subtitle text is the verified script (numbers shown as exact
  decimals, e.g. `3.255`, not the spoken-rounded `three point two six`).

## Source assets (regenerable)

- `voice/SCRIPT.md` — 6-scene narration script and timing targets.
- `voice/scene{1,1b,2,3,4,5}_*.txt` — per-scene voiceover source (verbatim)
- `voice/scene{1,1b,2,3,4,5}_*.mp3` — per-scene TTS (Microsoft Edge `en-US-GuyNeural`)
- `clips/clip1_provenance.gif` — `asciinema` → `agg` recording of the live
  `aqtc provenance / regime / report` demo (provenance-of-the-alpha evidence)
- `clips/flow_slide.html` / `.png` — opening flow infographic (scene 1 background)
- `clips/financial_lab_explainer.html` / `.png` — "Financial Lab vs AQTC: what's
  what" infographic clarifying that Financial Lab is a separate, open-source
  research repo and AQTC (this repo) operates the business (scene 1b background)
- `clips/dashboard.png` — FastAPI dashboard `/` (HTML, full page)
- `clips/provenance_api.png` — endpoint `GET /provenance` (JSON, full page)
- `clips/status_api.png` — endpoint `GET /status` (JSON, full page)
- `clips/scene{1,1b,2,3,4,5}.srt` — full per-scene subtitle cues (text + timing)
- `clips/scene{1,1b,2,3,4,5}.mp4` — per-scene composite (image + audio + captions)
- `clips/scene{1,1b,2,3,4,5}_bg.mp4` — per-scene background loop (image-only)
- `recordings/aqtc_demo_provenance.cast` — raw asciicast (replayable in
  `asciinema play`)
- `clips/report.md` — output of `aqtc report --out` (frozen ledger)
- `scripts/demo_provenance.sh` — recorded shell session
- `scripts/capture_dashboard.py` — Playwright capture script (live dashboard endpoints)
- `scripts/capture_html_slide.py` — Playwright capture script (static HTML infographics)
- `scripts/render_scene.py` — per-scene compositor: burns in the section tag +
  timed subtitle cues from an `.srt` file as a chain of `drawtext` filters
- `scripts/compose.sh` — orchestrates the full assembly (calls the two scripts above)

## Reproduce

```bash
cd docs/demo-video/scripts
uvicorn aqtc.api.app:app --port 8010 &     # start dashboard
python3 capture_dashboard.py               # live endpoint screenshots
python3 capture_html_slide.py \
  ../clips/flow_slide.html \
  ../clips/financial_lab_explainer.html    # static infographic screenshots
asciinema rec -c demo_provenance.sh \
  ../recordings/aqtc_demo_provenance.cast  # terminal recording
edge-tts --voice en-US-GuyNeural \
  --file ../voice/scene1_hook.txt \
  --write-media ../voice/scene1_hook.mp3   # x6 (one per scene, incl. scene1b)
agg ../recordings/aqtc_demo_provenance.cast \
  ../clips/clip1_provenance.gif
./compose.sh                                # final assembly (captions + concat)
```

Subtitle cues in `clips/scene*.srt` are hand-verified against `voice/SCRIPT.md`
(timing scaffolded from `whisper --word_timestamps True`, text corrected to the
canonical script — TTS/STT mishears acronyms and numbers). If voice-over wording
changes, regenerate timestamps and re-check cue text before re-running `compose.sh`.

## Timing per scene

| # | Visual                                  | Duration | Section tag                                                          |
|---|------------------------------------------|----------|------------------------------------------------------------------------|
| 1  | flow_slide.png (opening infographic)     | 14.4 s   | "From evolved alpha to invoice"                                       |
| 1b | financial_lab_explainer.png (NEW)        | 16.1 s   | "What is Financial Lab?"                                               |
| 2  | dashboard.png (HTML)                     | 20.7 s   | "Financial Lab: Heterogeneous Graph Attention + Evolution Strategies" |
| 3  | provenance_api.png (rejected candidate)  | 15.2 s   | "Falsification: 2019+ ensemble rejected"                               |
| 4  | status_api.png (regime + ledger)         | 23.0 s   | "Business loop: policy gate + Nemotron + Stripe ledger"               |
| 5  | dashboard.png (close)                    | 7.7 s    | "From evolved alpha to invoice."                                       |

Rendered `aqtc_demo.mp4` runs 94.6 s (1:35). Scene 1b was added so a viewer who
only sees the opening "Financial Lab" infographic card immediately gets a
spoken + on-screen explanation that Financial Lab is a separate, open-source
research repo (not part of AQTC's codebase) before the rest of the demo
assumes that context.

## What the demo proves (evidence shown in video)

- Alpha origin: `Financial Lab HGAT+ES v4` — Sharpe **3.255**, 5 folds,
  100 % positive, MaxDD **0.032**. Visual: scene 2 + dashboard endpoint.
- Falsification: the 2019+ ensemble (Sharpe **-0.544**, MaxDD **0.486**)
  is rejected and surfaced, not buried. Visual: scene 3 + provenance JSON.
- Closed loop: NemoClaw-compatible policy gate, Nemotron regime summary,
  Stripe-style ledger with paper rebalance status. Visual: scene 4 + status JSON.
- Demo is reproducible end-to-end: every command in the recording is real
  (`aqtc provenance`, `aqtc regime --provider mock`, `aqtc report --out ...`,
  `aqtc status`). No fake prompts, no chart-only bait.
