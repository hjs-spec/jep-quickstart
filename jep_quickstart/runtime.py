"""Small helpers over the installed JEP Core 0.7 HTTP SDK."""

from __future__ import annotations

import hashlib
import json
import os
from copy import deepcopy
from functools import wraps
from pathlib import Path
from typing import Any, Callable
from uuid import uuid4

from jep import JEPClient, JEPEvent


def client() -> JEPClient:
    return JEPClient(
        base_url=os.environ.get("JEP_API_URL", "http://127.0.0.1:8000"),
        api_key=os.environ.get("JEP_API_KEY", ""),
    )


def _snapshot(value):
    return json.loads(json.dumps(value, ensure_ascii=False, allow_nan=False))


def _request(kind, name, input, output, actor, event_id):
    return _snapshot(
        {
            "id": event_id,
            "verb": "J",
            "who": actor,
            "what": {
                "claim": kind,
                "subject": name,
                "context": {"input": input, "output": output},
            },
            "aud": "jep-quickstart",
        }
    )


def _submit_event(request) -> JEPEvent:
    result = client().create_event(deepcopy(request))
    if not result.validation.valid or result.validation.profile != "jep-core-0.7":
        raise ValueError("API did not return a valid JEP Core 0.7 event")
    return result.event


class RecordingError(RuntimeError):
    """Recording failed; call_executed describes whether the wrapped business call ran."""

    def __init__(self, *, call_executed, result=None, request=None):
        super().__init__(
            "Business call completed; do not rerun it. Recover the recording separately."
            if call_executed
            else "Recording inputs could not be prepared; business call did not run."
        )
        self.call_executed = call_executed
        self.result = result
        self._request = deepcopy(request)

    @property
    def request(self):
        """A copy of the frozen request; may contain sensitive inputs and results."""
        return deepcopy(self._request)

    def retry_recording(self) -> JEPEvent:
        """Retry only the unchanged request against API 0.8.6+; never invokes the callable."""
        if self._request is None:
            raise ValueError("No serializable recording request is available; resolve manually")
        try:
            return _submit_event(self._request)
        except Exception as exc:
            raise RecordingError(
                call_executed=self.call_executed, result=self.result, request=self._request
            ) from exc


def create_event(
    kind: str,
    name: str,
    input: dict[str, Any],
    output: Any,
    actor: str = "quickstart",
    *,
    event_id: str | None = None,
) -> JEPEvent:
    """Record a signed Judgment. Reuse event_id and all inputs to recover a create request."""
    request = _request(
        kind,
        name,
        input,
        output,
        actor,
        event_id if event_id is not None else f"urn:uuid:{uuid4()}",
    )
    return _submit_event(request)


def wrap_tool(name: str, func: Callable[..., Any], actor: str = "quickstart") -> Callable:
    @wraps(func)
    def wrapped(**kwargs: Any):
        try:
            inputs = _snapshot(kwargs)
        except Exception as exc:
            raise RecordingError(call_executed=False) from exc
        event_id = f"urn:uuid:{uuid4()}"
        result = func(**kwargs)
        request = None
        try:
            request = _request("tool.call", name, inputs, result, actor, event_id)
            return result, _submit_event(request)
        except Exception as exc:
            raise RecordingError(call_executed=True, result=result, request=request) from exc

    return wrapped


def export_archive(events: list[JEPEvent], path: str | Path = "archives/demo.jep.jsonl") -> Path:
    archive = Path(path)
    archive.parent.mkdir(parents=True, exist_ok=True)
    # x mode avoids silently replacing an earlier evidence archive.
    with archive.open("x", encoding="utf-8") as handle:
        for event in events:
            handle.write(json.dumps(event.to_dict(), ensure_ascii=False, allow_nan=False) + "\n")
    return archive


def strict_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate archive member: {key}")
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError(f"Non-finite archive value: {value}")


def replay_verify(path: str | Path) -> dict[str, Any]:
    """Verify each signed event in archival mode; no claim of complete logging."""
    hashes = []
    api = client()
    with Path(path).open(encoding="utf-8") as handle:
        for line in handle:
            event = json.loads(
                line, object_pairs_hook=strict_object, parse_constant=reject_constant
            )
            if not isinstance(event, dict):
                raise ValueError("Archive entries must be event objects")
            result = api.verify_event({"event": event, "mode": "archival"})
            if (
                not result.valid
                or result.profile != "jep-core-0.7"
                or result.checks.get("syntax") != "pass"
                or result.checks.get("cryptographic") != "pass"
                or result.checks.get("event_identity") != "pass"
                or not result.event_hash
            ):
                raise ValueError(f"Event verification failed: {result.errors}")
            if result.event_hash in hashes:
                raise ValueError("Duplicate event in archive")
            hashes.append(result.event_hash)
    if not hashes:
        raise ValueError("Empty archive")
    digest = hashlib.sha256("\n".join(hashes).encode("ascii")).hexdigest()
    return {
        "ok": True,
        "events": len(hashes),
        "profile": "jep-core-0.7",
        "checks": ["syntax", "cryptographic", "event_identity"],
        "event_hashes": hashes,
        "archive_digest": "sha256:" + digest,
    }
