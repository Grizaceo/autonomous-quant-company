# NVIDIA / Nemotron Integration

AQTC supports live Nemotron-compatible calls through OpenAI-compatible endpoints while keeping a deterministic mock fallback.

## Modes

```bash
AQTC_NVIDIA_MODE=mock          # deterministic default
AQTC_NVIDIA_MODE=auto          # prefer OpenRouter, then NVIDIA NIM, then OpenCode Zen, else mock
AQTC_NVIDIA_MODE=openrouter    # OpenRouter endpoint
AQTC_NVIDIA_MODE=nvidia        # NVIDIA NIM endpoint
AQTC_NVIDIA_MODE=opencode_zen  # OpenCode Zen key with OpenRouter-compatible endpoint
```

Defaults:

```bash
AQTC_OPENROUTER_MODEL=nvidia/nemotron-3-ultra-550b-a55b:free
AQTC_NVIDIA_MODEL=nvidia/nemotron-3-ultra-550b-a55b
AQTC_OPENCODE_ZEN_MODEL=nvidia/nemotron-3-ultra-550b-a55b:free
```

Smoke tests:

```bash
aqtc regime --provider openrouter --json
aqtc regime --provider nvidia --json
aqtc demo --nvidia-mode openrouter --json
```

Local verification on this machine showed both OpenRouter and NVIDIA NIM modes returned live Nemotron summaries. The demo still defaults to mock so public users can run it without keys.

## Safety role

Nemotron summarizes market/regime context; it does not approve trades. Approval remains in the explicit NemoClaw-style policy layer.
