"""HTTP API for the Agent Observability Assistant."""
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from app.telemetry import TelemetryStore

app = FastAPI(
    title="Agent Observability Assistant",
    description="Evidence-first triage of sample telemetry. No production actions are performed.",
    version="0.1.0",
)
store = TelemetryStore()


class TriageRequest(BaseModel):
    service: str = Field(min_length=1, max_length=100)
    window_minutes: int = Field(default=30, ge=1, le=1440)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "mode": "sample-telemetry-only"}


@app.get("/logs")
def search_logs(
    service: str | None = None,
    severity: str | None = Query(default=None, pattern="^(DEBUG|INFO|WARN|ERROR|CRITICAL|debug|info|warn|error|critical)$"),
    query: str | None = Query(default=None, max_length=200),
    limit: int = Query(default=100, ge=1, le=500),
) -> dict:
    return {"count": len(store.search(service, severity, query, limit)), "records": store.search(service, severity, query, limit)}


@app.get("/errors/summary")
def summarize_errors(service: str | None = None) -> dict:
    return store.summarize_errors(service)


@app.post("/triage")
def triage(request: TriageRequest) -> dict:
    result = store.investigate(request.service, request.window_minutes)
    if result["records_examined"] == 0:
        # Return the useful report even when empty; absence of evidence is not an error.
        return result
    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
