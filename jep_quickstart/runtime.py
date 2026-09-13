"""Small helpers over the installed JEP-Core-0.6 HTTP SDK."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Callable

from jep import JEPClient, JEPEvent


def client() -> JEPClient:
    return JEPClient(
        base_url=os.environ.get("JEP_API_URL", "http://127.0.0.1:8000"),
        api_key=os.environ.get("JEP_API_KEY", ""),
    )


def create_event(
    kind: str, name: str, input: dict[str, Any], output: Any, actor: str = "quickstart"
) -> JEPEvent:
    """Record a signed Judgment; application details stay inside what."""
    result = client().create_event(
        {
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
    if not result.validation.valid or result.validation.profile != "jep-core-0.6":
        raise ValueError("API did not return a valid JEP-Core-0.6 event")
    return result.event


def wrap_tool(
    name: str, func: Callable[..., Any], actor: str = "quickstart"
) -> Callable:
    def wrapped(**kwargs: Any):
        result = func(**kwargs)
        return result, create_event("tool.call", name, kwargs, result, actor=actor)

    return wrapped


def export_archive(
    events: list[JEPEvent], path: str | Path = "archives/demo.jep.jsonl"
) -> Path:
    archive = Path(path)
    archive.parent.mkdir(parents=True, exist_ok=True)
    # x mode avoids silently replacing an earlier evidence archive.
    with archive.open("x", encoding="utf-8") as handle:
        for event in events:
            handle.write(
                json.dumps(event.to_dict(), ensure_ascii=False, allow_nan=False) + "\n"
            )
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
                or result.level < 1
                or result.profile != "jep-core-0.6"
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
        "profile": "jep-core-0.6",
        "level": 1,
        "event_hashes": hashes,
        "archive_digest": "sha256:" + digest,
    }
