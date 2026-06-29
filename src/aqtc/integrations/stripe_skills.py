from __future__ import annotations

import base64
import json
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Literal, Protocol

from aqtc.secrets import get_secret


@dataclass(frozen=True)
class StripeLedgerEvent:
    kind: Literal["spend", "earn"]
    description: str
    amount_usd: float
    mode: str = "mock"
    external_id: str | None = None
    status: str = "recorded"
    metadata: dict[str, Any] = field(default_factory=dict)


class StripeLedger:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("[]", encoding="utf-8")

    def append(self, event: StripeLedgerEvent) -> None:
        events = self.read()
        events.append(asdict(event))
        self.path.write_text(json.dumps(events, indent=2, sort_keys=True), encoding="utf-8")

    def read(self) -> list[dict[str, Any]]:
        return json.loads(self.path.read_text(encoding="utf-8"))

    def net(self) -> float:
        total = 0.0
        for event in self.read():
            total += event["amount_usd"] if event["kind"] == "earn" else -event["amount_usd"]
        return round(total, 2)


class StripeAdapter(Protocol):
    mode: str

    def spend(self, description: str, amount_usd: float) -> StripeLedgerEvent: ...

    def earn(self, description: str, amount_usd: float) -> StripeLedgerEvent: ...


class MockStripeAdapter:
    def __init__(self, ledger: StripeLedger, *, mode: str = "mock", daily_budget_usd: float = 25.0):
        self.ledger = ledger
        self.mode = mode
        self.daily_budget_usd = daily_budget_usd

    def _spent_so_far(self) -> float:
        return sum(event["amount_usd"] for event in self.ledger.read() if event["kind"] == "spend")

    def spend(self, description: str, amount_usd: float) -> StripeLedgerEvent:
        spent = self._spent_so_far()
        if spent + amount_usd > self.daily_budget_usd:
            raise RuntimeError(
                f"budget exceeded: attempted {spent + amount_usd:.2f} > {self.daily_budget_usd:.2f}"
            )
        event = StripeLedgerEvent(
            kind="spend",
            description=description,
            amount_usd=amount_usd,
            mode=self.mode,
            external_id=f"mock_spend_{len(self.ledger.read()) + 1}",
            status="mock_recorded",
        )
        self.ledger.append(event)
        return event

    def earn(self, description: str, amount_usd: float) -> StripeLedgerEvent:
        event = StripeLedgerEvent(
            kind="earn",
            description=description,
            amount_usd=amount_usd,
            mode=self.mode,
            external_id=f"mock_earn_{len(self.ledger.read()) + 1}",
            status="mock_recorded",
        )
        self.ledger.append(event)
        return event


class StripeTestModeAdapter(MockStripeAdapter):
    """Stripe test-mode adapter using Stripe's HTTPS API directly.

    Revenue (`earn`) creates a real test-mode PaymentIntent when STRIPE_SECRET_KEY
    is available. Outbound `spend` remains a budgeted procurement ledger event;
    true outbound payments require Stripe Link / MPP and user approval in P2.
    """

    api_base = "https://api.stripe.com/v1"

    def __init__(
        self,
        ledger: StripeLedger,
        *,
        daily_budget_usd: float = 25.0,
        currency: str = "usd",
        api_key: str | None = None,
    ):
        super().__init__(ledger, mode="stripe_test", daily_budget_usd=daily_budget_usd)
        self.currency = currency.lower()
        self.api_key = api_key or get_secret("STRIPE_SECRET_KEY")

    @property
    def available(self) -> bool:
        return bool(self.api_key)

    def _post_form(self, path: str, data: dict[str, str | int]) -> dict[str, Any]:
        if not self.api_key:
            raise RuntimeError("STRIPE_SECRET_KEY is not available")
        encoded = urllib.parse.urlencode(data).encode("utf-8")
        token = base64.b64encode(f"{self.api_key}:".encode()).decode("ascii")
        request = urllib.request.Request(
            self.api_base + path,
            data=encoded,
            method="POST",
            headers={
                "Authorization": f"Basic {token}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="ignore")[:500]
            raise RuntimeError(f"Stripe API error {exc.code}: {body}") from exc

    def earn(self, description: str, amount_usd: float) -> StripeLedgerEvent:
        if not self.available:
            return super().earn(description, amount_usd)
        amount_cents = int(round(amount_usd * 100))
        payment_intent = self._post_form(
            "/payment_intents",
            {
                "amount": amount_cents,
                "currency": self.currency,
                "description": description,
                "metadata[agent]": "autonomous-quant-company",
                "metadata[mode]": "hackathon-demo",
                "payment_method_types[]": "card",
                "automatic_payment_methods[enabled]": "false",
                "payment_method": "pm_card_visa",
                "confirm": "true",
            },
        )
        status = str(payment_intent.get("status", "created"))
        event = StripeLedgerEvent(
            kind="earn",
            description=description,
            amount_usd=amount_usd,
            mode=self.mode,
            external_id=payment_intent.get("id"),
            status=status,
            metadata={
                "object": payment_intent.get("object"),
                "livemode": payment_intent.get("livemode"),
                "currency": payment_intent.get("currency"),
                "collection": "succeeded" if status == "succeeded" else "authorized_not_collected",
            },
        )
        self.ledger.append(event)
        return event

    def spend(self, description: str, amount_usd: float) -> StripeLedgerEvent:
        event = super().spend(description, amount_usd)
        upgraded = StripeLedgerEvent(
            kind=event.kind,
            description=event.description,
            amount_usd=event.amount_usd,
            mode=self.mode,
            external_id=event.external_id,
            status="budgeted_procurement_recorded",
            metadata={"note": "Outbound Stripe Link/MPP payment is planned for P2."},
        )
        events = self.ledger.read()
        events[-1] = asdict(upgraded)
        self.ledger.path.write_text(json.dumps(events, indent=2, sort_keys=True), encoding="utf-8")
        return upgraded


def make_stripe_adapter(
    ledger: StripeLedger,
    *,
    mode: str,
    daily_budget_usd: float,
    currency: str = "usd",
) -> StripeAdapter:
    normalized = mode.lower()
    if normalized in {"stripe", "stripe_test", "test"}:
        return StripeTestModeAdapter(ledger, daily_budget_usd=daily_budget_usd, currency=currency)
    return MockStripeAdapter(ledger, mode=mode, daily_budget_usd=daily_budget_usd)
