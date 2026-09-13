"""Tiny mock JEP runtime used by the quickstart examples."""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable
from uuid import uuid4


@dataclass
class JEPEvent:
    """Minimal event shape for a first JEP integration."""

    kind: str
    name: str
    input: dict[str, Any]
    output: Any
    actor: str = "quickstart"
    event_id: str = field(default_factory=lambda: f"evt_{uuid4().hex[:12]}")
    ts: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "jep": "0.1",
            "event_id": self.event_id,
            "kind": self.kind,
            "name": self.name,
            "actor": self.actor,
            "ts": self.ts,
            "input": self.input,
            "output": self.output,
        }


def create_event(kind: str, name: str, input: dict[str, Any], output: Any, actor: str = "quickstart") -> JEPEvent:
    return JEPEvent(kind=kind, name=name, input=input, output=output, actor=actor)


def wrap_tool(name: str, func: Callable[..., Any], actor: str = "quickstart") -> Callable[..., tuple[Any, JEPEvent]]:
    """Wrap a normal Python callable so every call returns `(result, event)`."""

    def wrapped(**kwargs: Any) -> tuple[Any, JEPEvent]:
        result = func(**kwargs)
        return result, create_event("tool.call", name, kwargs, result, actor=actor)

    return wrapped


def export_archive(events: list[JEPEvent], path: str | Path = "archives/demo.jep.jsonl") -> Path:
    archive = Path(path)
    archive.parent.mkdir(parents=True, exist_ok=True)
    with archive.open("w", encoding="utf-8") as handle:
        for event in events:
            handle.write(json.dumps(event.to_dict(), sort_keys=True) + "\n")
    return archive


def replay_verify(path: str | Path) -> dict[str, Any]:
    """Replay an archive by validating each line and returning a stable digest."""

    archive = Path(path)
    digest = hashlib.sha256()
    count = 0
    with archive.open(encoding="utf-8") as handle:
        for line in handle:
            event = json.loads(line)
            for key in ("jep", "event_id", "kind", "name", "input", "output"):
                if key not in event:
                    raise ValueError(f"missing {key} in event {count + 1}")
            digest.update(json.dumps(event, sort_keys=True).encode())
            count += 1
    return {"ok": True, "events": count, "sha256": digest.hexdigest()[:16]}
