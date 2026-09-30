# JEP HTTP Quickstart — JEP Core 0.7

Create signed JEP Core 0.7 events with the Python SDK and verify them through
the local JEP reference API.

Start with the [packaged Core sample](https://github.com/hjs-spec/jep-core#verify-your-first-event)
for a first verification. This repository provides HTTP integration: an API owns
the signing key and clients send requests. For local signed recording, use the
[Agent SDK](https://github.com/hjs-spec/jep-agent-sdk#local-create--export--independent-verification).

## Start a local API

```bash
git clone --branch v0.8.5 --depth 1 https://github.com/hjs-spec/jep-api.git
cd jep-api
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
export JEP_STATE_DIR="$PWD/.local-state"
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

The current API exposes protocol profile `jep-core-0.7` on versioned
`/v0.7` endpoints.

## Install and run

Keep the API terminal running and open a second terminal for these commands.
The shell examples use Bash; Windows users can use WSL or adapt virtual-environment activation.

```bash
git clone --branch v0.7.0 --depth 1 https://github.com/hjs-spec/jep-quickstart.git
cd jep-quickstart
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .
make demo
```

```python
from jep_quickstart import create_event, export_archive, replay_verify, wrap_tool

event = create_event(
    "agent.step",
    "first-event",
    {"goal": "try JEP"},
    {"status": "started"},
)
print(event.id, event.to_dict())

archive = export_archive([event], "archives/first.jep.jsonl")
print(replay_verify(archive))
```

`create_event` records application details inside a signed Judgment event.
It does not authorize a tool, establish factual truth, or make execution and
recording atomic.

## What archival verification means

A successful replay requires current JEP Core 0.7 archival validation,
including:

- `status == valid`;
- `cryptographic == pass`;
- `event_identity == pass`;
- a computed Event Hash.

These results verify the recorded event. Actor trust, authorization and live
acceptance require their own configured checks.

`archive_digest` is a local ordering digest for this quickstart, not a JEP
Core event field or completeness anchor.

See the [Core contract](https://github.com/hjs-spec/jep-core#current-contract) for
event structure and validation requirements.

## Test

```bash
python -m pip install -e '.[test]'
JEP_API_SOURCE=../jep-api python -m pytest -q
```

CI pins API 0.8.5 at `9381cddf0dafba55cd07aa7fc4d4316c95440d08`.
Use `JEP_API_SOURCE` to select another API checkout for development tests.

## Related

- JEP Core: https://github.com/hjs-spec/jep-core
- JEP API: https://github.com/hjs-spec/jep-api
- Python SDK: https://github.com/hjs-spec/sdk-py
- Internet-Draft: https://datatracker.ietf.org/doc/draft-wang-jep-judgment-event-protocol/

- [Historical mock examples](jep_quickstart/LEGACY.md)
