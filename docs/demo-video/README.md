# AQTC Hackathon Demo Video

Final deliverables for the NVIDIA × Stripe × Nous Hermes Agent hackathon demo.
All assets live in this directory. The shipped artifact is `aqtc_demo.mp4`.

## Final artifact

- `aqtc_demo.mp4` — H.264 1280×720, AAC 24 kHz mono, 89.6 s (1:29),
  voice-over + captions overlay. Plays inside any browser.

## Source assets (regenerable)

- `voice/SCRIPT.md` — 5-scene narration script and timing targets.
- `voice/scene{1..5}_*.txt` — per-scene voiceover source (verbatim)
- `voice/scene{1..5}_*.mp3` — per-scene TTS (Microsoft Edge `en-US-GuyNeural`)
- `clips/clip1_provenance.gif` — `asciinema` → `agg` recording of the live
  `aqtc provenance / regime / report` demo (provenance-of-the-alpha evidence)
- `clips/dashboard.png` — FastAPI dashboard `/` (HTML, full page)
- `clips/provenance_api.png` — endpoint `GET /provenance` (JSON, full page)
- `clips/status_api.png` — endpoint `GET /status` (JSON, full page)
- `clips/scene{1..5}.mp4` — per-scene composite (image + audio + captions)
- `clips/scene{1..5}_bg.mp4` — per-scene background loop (image-only)
- `recordings/aqtc_demo_provenance.cast` — raw asciicast (replayable in
  `asciinema play`)
- `clips/report.md` — output of `aqtc report --out` (frozen ledger)
- `scripts/demo_provenance.sh` — recorded shell session
- `scripts/capture_dashboard.py` — Playwright capture script
- `scripts/compose.sh` — ffmpeg compositor

## Reproduce

```bash
cd docs/demo-video/scripts
uvicorn aqtc.api.app:app --port 8010 &     # start dashboard
python3 capture_dashboard.py               # screenshots
asciinema rec -c demo_provenance.sh \
  ../recordings/aqtc_demo_provenance.cast  # terminal recording
edge-tts --voice en-US-GuyNeural \
  --file ../voice/scene1_hook.txt \
  --write-media ../voice/scene1_hook.mp3   # x5
agg ../recordings/aqtc_demo_provenance.cast \
  ../clips/clip1_provenance.gif
./compose.sh                                # final assembly
```

## Timing per scene

| # | Visual                                | Voiceover period | Caption                                    |
|---|---------------------------------------|------------------|--------------------------------------------|
| 1 | black title card                      | 12.0 s           | "AQTC :: Hackathon submission"             |
| 2 | dashboard.png (HTML)                  | 17.4 s           | "Frozen HGAT+ES v4 walkforward evidence"   |
| 3 | provenance_api.png (rejected candle)  | 16.2 s           | "Falsification: rejected 2019+ ensemble"   |
| 4 | status_api.png (regime + ledger)      | 23.2 s           | "Business loop: policy gate + Nemotron + Stripe" |
| 5 | dashboard.png (close)                 | 20.8 s           | "From evolved alpha to invoice."           |

Total: 89.6 s.

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
