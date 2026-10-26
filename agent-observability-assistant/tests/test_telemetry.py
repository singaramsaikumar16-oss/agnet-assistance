from app.telemetry import TelemetryStore


def test_search_filters_service_and_severity():
    store = TelemetryStore()
    records = store.search(service="checkout", severity="ERROR")
    assert records
    assert all(r["service"] == "checkout" and r["severity"] == "ERROR" for r in records)


def test_summary_returns_evidence():
    result = TelemetryStore().summarize_errors("checkout")
    assert result["error_count"] >= 1
    assert result["top_signatures"][0]["signature"].startswith("DatabaseTimeout")
    assert result["evidence"]


def test_triage_never_runs_remediation():
    result = TelemetryStore().investigate("checkout", 30)
    assert result["automated_remediation"] is False
    assert result["confidence"] == "low"
    assert "evidence" in result
