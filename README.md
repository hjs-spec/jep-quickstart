# JEP HTTP Quickstart — JEP Core 0.7

Create signed JEP Core 0.7 events with the Python SDK and verify them through
the local JEP reference API.

Start with the [packaged Core sample](https://github.com/hjs-spec/jep-core#verify-your-first-event)
for a first verification. This repository provides HTTP integration: an API owns
the signing key and clients send requests. For local signed recording, use the
[Agent SDK](https://github.com/hjs-spec/jep-agent-sdk#local-create--export--independent-verification).

## Start a local API

```bash
git clone --branch v0.8.7 --depth 1 https://github.com/hjs-spec/jep-api.git
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
git clone --branch v0.7.2 --depth 1 https://github.com/hjs-spec/jep-quickstart.git
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

## Recover after recording fails

Quickstart 0.7.1 and later require API **0.8.6+** for safe creation retries. `wrap_tool`
raises `RecordingError` if it cannot record a call. Check `call_executed` before
deciding what to do:

| Failure state | Next step |
|---|---|
| `call_executed == False` | The callable did not run. Correct the input serialization problem. |
| `call_executed == True`, `request` available | The callable returned; its result is in `result`. Keep the exception and retry only the recording after resolving the transport/server failure. |
| `call_executed == True`, `request is None` | The result could not be serialized. Recover manually using `result`; do not repeat the business call. |

```python
from jep_quickstart import RecordingError, wrap_tool

pending = None
tool = wrap_tool("addition", lambda a, b: a + b)
try:
    result, event = tool(a=2, b=3)
except RecordingError as error:
    pending = error
    print("Call executed:", error.call_executed, "Result:", error.result)
```

After resolving a timeout or temporary service failure, recover the original
signed event without calling `tool` again:

```python
if pending is not None and pending.call_executed and pending.request is not None:
    event = pending.retry_recording()
    result = pending.result
```

`retry_recording()` sends the same saved request and `id`; it never invokes the
callable. HTTP 409 means the ID belongs to different request content: stop and
reconcile it. Other business exceptions remain the original exception and are
not converted to `RecordingError`.

The recovery object lives in memory. For process-restart recovery, retain
`pending.request` in your application's durable storage and resend it through
`JEPClient.create_event` after recovery. It includes the captured inputs and
result, so store it with appropriate access controls. A process crash between
business execution and saving that request still needs application reconciliation.

For direct `create_event` calls, choose and persist `event_id` before sending;
reuse it with unchanged arguments if a response is lost. Omitted IDs are generated
anew on each direct call. Verification and acceptance remain separate operations.

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

CI pins API 0.8.7 at `24bf1ff6d158f1329d8e5397c58e896786efef06`.
Use `JEP_API_SOURCE` to select another API checkout for development tests.

## Related

- JEP Core: https://github.com/hjs-spec/jep-core
- JEP API: https://github.com/hjs-spec/jep-api
- Python SDK: https://github.com/hjs-spec/sdk-py
- Internet-Draft: https://datatracker.ietf.org/doc/draft-wang-jep-judgment-event-protocol/

- [Historical mock examples](jep_quickstart/LEGACY.md)
- [Contributing and private security reports](https://github.com/hjs-spec/.github/blob/main/CONTRIBUTING.md)

## License

[BSD-3-Clause](LICENSE); see [licensing scope and notices](NOTICE.md).
