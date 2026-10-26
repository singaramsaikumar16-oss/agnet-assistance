# Agent Observability Assistant

A small, demo-ready project that analyzes application telemetry, highlights error patterns, and produces evidence-backed incident summaries. It includes a FastAPI HTTP API and an optional Model Context Protocol (MCP) server.

> **Safety note:** This demo uses sample/local telemetry only. It does not connect to production systems or execute remediation actions.

## Features
- Search structured application logs by service, severity, and text.
- Summarize errors and identify the most frequent error signatures.
- Generate a cautious incident triage report with supporting log evidence.
- Expose the same tools through an MCP server for compatible AI clients.
- Includes sample telemetry and tests.

## Quick start

Python 3.10+ recommended.

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs for the interactive API docs.

### Example API requests

```bash
curl "http://127.0.0.1:8000/health"
curl "http://127.0.0.1:8000/logs?service=checkout&severity=ERROR"
curl -X POST "http://127.0.0.1:8000/triage" \
  -H "Content-Type: application/json" \
  -d '{"service":"checkout","window_minutes":30}'
```

## Run the tests

```bash
pytest -q
```

## Run the MCP server

Install the project requirements, then run:

```bash
python -m app.mcp_server
```

The MCP server exposes `search_logs`, `summarize_errors`, and `investigate_incident`. Configure the command and working directory in your MCP-compatible client according to that client's documentation.

## Project layout

```text
app/
  __init__.py
  main.py          # FastAPI endpoints
  telemetry.py     # Sample telemetry loading and analysis
  mcp_server.py    # Optional MCP tool server
data/
  sample_logs.json
tests/
  test_telemetry.py
requirements.txt
```

## Design choices and limitations

- **Evidence first:** summaries include the log records that support them.
- **No false certainty:** the triage output calls out hypotheses, not definitive root causes.
- **No unsafe actions:** the project only reads demo logs and recommends investigation steps.
- **Time window:** timestamps are evaluated relative to the current UTC time; sample records are generated relative to a fixed recent window so the demo remains useful.
- **Production readiness:** before real use, add authentication, authorization, tenant isolation, rate limiting, secret management, retention controls, and tests against your observability provider.

## Suggested next improvements
1. Add OpenTelemetry trace/span correlation.
2. Add a real log backend adapter behind the `TelemetryStore` interface.
3. Add an evaluation dataset for false positives and missed incidents.
4. Add a UI showing the evidence behind each hypothesis.
5. Add configurable redaction for secrets and personal data before logs reach a model.

## GitHub publishing

Create a new public repository on GitHub, then from this folder run:

```bash
git init
git add .
git commit -m "Build agent observability assistant"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/agent-observability-assistant.git
git push -u origin main
```

Replace `YOUR-USERNAME` with your GitHub username. Do not claim the repository is public until you have pushed it and verified the link.
