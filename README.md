# JEP HTTP Quickstart — JEP Core 0.7

Create signed JEP Core 0.7 events with the Python SDK and verify them through
the local JEP reference API.

For a first signed event without running a service, use the
[Agent SDK local create/export/verify example](https://github.com/hjs-spec/jep-agent-sdk#local-create--export--independent-verification).
This repository is the HTTP path: an API owns the signing key and clients send requests.

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
`/v0.7` endpoints. Historical pre-0.7 handling remains explicit and is not
selected by fallback.

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

It does **not** imply:

- actor binding unless a trust profile required and performed it;
- freshness or acceptance eligibility;
- complete logging;
- chain/cascade semantics;
- authorization validity;
- factual truth or legal effect.

`archive_digest` is a local ordering digest for this quickstart, not a JEP
Core event field or completeness anchor.

## Core 0.7 differences from older examples

- every event has stable `id`;
- Event Identity is `(who,id)`;
- Core does not require a top-level nonce;
- validation uses independent checks instead of Levels 0–4;
- Event Hash identifies the exact signed artifact, not the logical event;
- D/T/V have verb-specific minimum structures;
- chain and policy meaning remain outside Core.

Historical mock examples remain isolated behind explicitly named legacy
modules; they are not treated as current JEP Core events.

## Test

```bash
python -m pip install -e '.[test]'
JEP_API_SOURCE=../jep-api python -m pytest -q
```

## Related

- JEP Core: https://github.com/hjs-spec/jep-core
- JEP API: https://github.com/hjs-spec/jep-api
- Python SDK: https://github.com/hjs-spec/sdk-py
- Internet-Draft: https://datatracker.ietf.org/doc/draft-wang-jep-judgment-event-protocol/

CI and release tests pin the reference API to `9381cddf0dafba55cd07aa7fc4d4316c95440d08` (API software 0.8.5, Core profile 0.7).

The commands above select a versioned release combination. For development, use
separate source checkouts and run the same tests against an explicitly selected API revision.
A successful local run does not configure or validate a hosted production service.
