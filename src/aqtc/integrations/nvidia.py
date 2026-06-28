from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from aqtc.secrets import get_secret


@dataclass(frozen=True)
class MarketRegimeSummary:
    provider: str
    text: str
    model: str = "mock"
    live: bool = False


class MockNemotronAdapter:
    provider = "mock"
    model = "mock-nemotron"

    def summarize_market_regime(self, context: dict[str, Any] | None = None) -> MarketRegimeSummary:
        return MarketRegimeSummary(
            provider="mock-nemotron",
            model=self.model,
            live=False,
            text=(
                "Demo regime: operate in paper mode, prefer validated HGAT+ES v4, "
                "reject strategies with poor out-of-sample drawdown."
            ),
        )


class OpenAICompatibleNemotronAdapter:
    """Nemotron adapter for OpenAI-compatible endpoints.

    Supported modes:
    - openrouter: https://openrouter.ai/api/v1 with OPENROUTER_API_KEY
    - nvidia: https://integrate.api.nvidia.com/v1 with NVIDIA_API_KEY
    - opencode_zen: configurable OpenAI-compatible endpoint with OPENCODE_ZEN_API_KEY
    """

    def __init__(self, *, provider: str, model: str, base_url: str, api_key_name: str):
        self.provider = provider
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.api_key_name = api_key_name
        self.api_key = get_secret(api_key_name)

    @property
    def available(self) -> bool:
        return bool(self.api_key)

    def summarize_market_regime(self, context: dict[str, Any] | None = None) -> MarketRegimeSummary:
        if not self.available:
            return MockNemotronAdapter().summarize_market_regime(context)
        try:
            from openai import OpenAI
        except Exception as exc:  # pragma: no cover - dependency guard
            raise RuntimeError("openai package is required for live Nemotron mode") from exc

        payload = context or {}
        prompt = (
            "You are the risk and market-regime reviewer for an autonomous quant company. "
            "Use the supplied validation and risk context. Return 3 concise sentences: "
            "regime, strategy decision, and safety constraint. Context: "
            f"{payload}"
        )
        client = OpenAI(api_key=self.api_key, base_url=self.base_url, max_retries=1)
        try:
            completion = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Be concise, evidence-grounded, and risk-aware."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=180,
                temperature=0.2,
            )
        except Exception as exc:
            fallback = MockNemotronAdapter().summarize_market_regime(context)
            return MarketRegimeSummary(
                provider=f"{self.provider}-unavailable",
                model=self.model,
                live=False,
                text=f"{fallback.text} Live provider error: {type(exc).__name__}.",
            )
        text = completion.choices[0].message.content or "No summary returned."
        return MarketRegimeSummary(provider=self.provider, model=self.model, text=text.strip(), live=True)


def make_nemotron_adapter(
    *,
    mode: str,
    openrouter_model: str,
    nvidia_model: str,
    opencode_zen_model: str,
) -> MockNemotronAdapter | OpenAICompatibleNemotronAdapter:
    normalized = mode.lower()
    if normalized == "auto":
        if get_secret("OPENROUTER_API_KEY"):
            normalized = "openrouter"
        elif get_secret("NVIDIA_API_KEY"):
            normalized = "nvidia"
        elif get_secret("OPENCODE_ZEN_API_KEY"):
            normalized = "opencode_zen"
        else:
            normalized = "mock"

    if normalized == "openrouter":
        return OpenAICompatibleNemotronAdapter(
            provider="openrouter",
            model=openrouter_model,
            base_url="https://openrouter.ai/api/v1",
            api_key_name="OPENROUTER_API_KEY",
        )
    if normalized == "nvidia":
        return OpenAICompatibleNemotronAdapter(
            provider="nvidia-nim",
            model=nvidia_model,
            base_url="https://integrate.api.nvidia.com/v1",
            api_key_name="NVIDIA_API_KEY",
        )
    if normalized in {"opencode", "opencode_zen", "zen"}:
        return OpenAICompatibleNemotronAdapter(
            provider="opencode-zen",
            model=opencode_zen_model,
            base_url="https://openrouter.ai/api/v1",
            api_key_name="OPENCODE_ZEN_API_KEY",
        )
    return MockNemotronAdapter()
