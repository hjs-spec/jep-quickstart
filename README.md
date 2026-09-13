# JEP Quickstart

Create signed Judgment Event Protocol events with the installed Python SDK and verify them through the local JEP-Core-0.6 API. All default examples use real signatures; the small business tools are demonstrations.

## Start a local API (terminal 1)

Python 3.10 or newer is required. From the parent directory of this clone:

```bash
git clone https://github.com/hjs-spec/jep-api.git
cd jep-api
git checkout v0.7.3
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
export JEP_STATE_DIR="$PWD/.local-state"
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

This starts a loopback development service and preserves its local verification keys across restarts. Keep that state directory to replay prior archives. This is not a live deployment; no public service or database is required. API software version 0.7.3 implements protocol profile `jep-core-0.6`, wire `jep: "1"`.

The SDK defaults to `http://127.0.0.1:8000`. Set `JEP_API_URL` to another explicitly trusted API, and `JEP_API_KEY` if it requires a signing token. Archival verification relies on that API's trusted key store.

## Install and run (terminal 2)

```bash
git clone https://github.com/hjs-spec/jep-quickstart.git
cd jep-quickstart
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .
make demo
```

The Python example writes a uniquely named `archives/demo-*.jep.jsonl` and verifies each signed event in archival mode. Running the demo again preserves earlier archives.

```python
from jep_quickstart import create_event, export_archive, replay_verify, wrap_tool

event = create_event("agent.step", "first-event", {"goal": "try JEP"}, {"status": "started"})
print(event.to_dict())
archive = export_archive([event], "archives/first.jep.jsonl")
print(replay_verify(archive))
```

`create_event` records application details inside a signed `J` event's `what`. `wrap_tool` calls the supplied function, then records its returned result; it does not authorize the tool or make tool execution and archive writing atomic. Handle recording failures in the application's execution policy.

## Examples and verification limits

- `examples/python_quickstart.py`: signed event, tool wrapper, export and real API verification.
- `examples/mcp_quickstart.py`: simulated MCP tool with real event recording.
- `examples/langgraph_quickstart.py`: graph-shaped function with real event recording.
- `examples/openai_agents_quickstart.py`: illustrative middleware with real event recording.

These examples do not install or execute the actual MCP, LangGraph or OpenAI Agents frameworks. Use the dedicated adapter repositories for those integrations.

A successful report means Level 1 syntax and cryptographic verification. It does not bind `who` to an identity, authorize a tool, establish complete logging, or verify HJS/JAC semantics. `archive_digest` is a local ordering digest, not a protocol event field or a trusted completeness anchor. Raw signed event members are preserved during export.

For the four-verb flow, see [jep-e2e-demo](https://github.com/hjs-spec/jep-e2e-demo). The original unsigned examples are retained in [legacy_mock.py](jep_quickstart/LEGACY.md), accessible only by explicit import; default replay rejects that format.

## Test

```bash
python -m pip install -e '.[test]' -r ../jep-api/requirements.txt
JEP_API_SOURCE=../jep-api python -m pytest -q
```

Tests start an isolated local API subprocess with a temporary key store. They verify real signatures and rejection of tampered, duplicate, empty and historical archives.
