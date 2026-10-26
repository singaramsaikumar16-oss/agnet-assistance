"""Optional MCP server exposing read-only telemetry tools."""
from mcp.server.fastmcp import FastMCP
from app.telemetry import TelemetryStore

mcp = FastMCP("agent-observability-assistant")
store = TelemetryStore()


@mcp.tool()
def search_logs(service: str = "", severity: str = "", query: str = "", limit: int = 50) -> dict:
    """Search the bundled sample logs by service, severity, or text."""
    records = store.search(
        service=service or None,
        severity=severity or None,
        query=query or None,
        limit=max(1, min(limit, 200)),
    )
    return {"count": len(records), "records": records}


@mcp.tool()
def summarize_errors(service: str = "") -> dict:
    """Summarize ERROR-level sample logs and return supporting evidence."""
    return store.summarize_errors(service or None)


@mcp.tool()
def investigate_incident(service: str, window_minutes: int = 30) -> dict:
    """Produce a cautious incident triage report from sample logs; performs no remediation."""
    return store.investigate(service, window_minutes)


if __name__ == "__main__":
    mcp.run()
