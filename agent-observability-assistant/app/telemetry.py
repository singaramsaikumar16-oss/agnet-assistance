"""Evidence-first analysis helpers for sample application telemetry."""
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "sample_logs.json"


def load_logs() -> list[dict[str, Any]]:
    """Load demo logs and shift their timestamps into a recent time window."""
    records = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    now = datetime.now(timezone.utc)
    for i, record in enumerate(records):
        # Keep the relative ordering while ensuring the sample remains recent.
        record["timestamp"] = (now - timedelta(minutes=(len(records) - i) * 3)).isoformat()
    return records


class TelemetryStore:
    def __init__(self) -> None:
        self._logs = load_logs()

    def search(
        self,
        service: str | None = None,
        severity: str | None = None,
        query: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Filter logs; return newest first."""
        result = self._logs
        if service:
            result = [r for r in result if r["service"].lower() == service.lower()]
        if severity:
            result = [r for r in result if r["severity"].lower() == severity.lower()]
        if query:
            q = query.lower()
            result = [
                r for r in result
                if q in r["message"].lower()
                or q in r["service"].lower()
                or q in r.get("error_type", "").lower()
            ]
        return sorted(result, key=lambda r: r["timestamp"], reverse=True)[:max(1, min(limit, 500))]

    def summarize_errors(self, service: str | None = None) -> dict[str, Any]:
        records = self.search(service=service, severity="ERROR", limit=500)
        signatures = Counter(
            f'{r.get("error_type", "UnknownError")}: {r["message"]}'
            for r in records
        )
        return {
            "service": service or "all",
            "error_count": len(records),
            "top_signatures": [
                {"signature": signature, "count": count}
                for signature, count in signatures.most_common(5)
            ],
            "evidence": records[:10],
        }

    def investigate(self, service: str, window_minutes: int = 30) -> dict[str, Any]:
        """Create a cautious triage report; this does not establish root cause."""
        window_minutes = max(1, min(window_minutes, 24 * 60))
        records = self.search(service=service, limit=500)
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=window_minutes)

        recent = []
        for record in records:
            ts = datetime.fromisoformat(record["timestamp"].replace("Z", "+00:00"))
            if ts >= cutoff:
                recent.append(record)

        errors = [r for r in recent if r["severity"] == "ERROR"]
        warnings = [r for r in recent if r["severity"] == "WARN"]
        signatures = Counter(r.get("error_type", "UnknownError") for r in errors)

        if not recent:
            hypothesis = "No matching telemetry was found in the requested window."
            next_steps = ["Verify the service name, time window, and telemetry ingestion."]
        elif errors:
            top_error = signatures.most_common(1)[0][0]
            hypothesis = (
                f"Errors are present; {top_error} is the most common error type "
                "in the available sample. This is a lead to investigate, not a confirmed root cause."
            )
            next_steps = [
                "Inspect the evidence records and correlate timestamps with traces and deployments.",
                "Compare the error rate with a healthy baseline before declaring an incident.",
                "Check dependent services and recent configuration changes.",
            ]
        else:
            hypothesis = "No ERROR-level records were found; warnings alone do not prove an incident."
            next_steps = [
                "Review warning context and compare key metrics with a known-good baseline.",
                "Check whether relevant logs may be missing or delayed.",
            ]

        return {
            "service": service,
            "window_minutes": window_minutes,
            "records_examined": len(recent),
            "error_count": len(errors),
            "warning_count": len(warnings),
            "hypothesis": hypothesis,
            "confidence": "low",
            "confidence_reason": "This demo uses a small sample and lacks trace, metric, and deployment correlation.",
            "recommended_next_steps": next_steps,
            "evidence": (errors or warnings or recent)[:10],
            "automated_remediation": False,
        }
