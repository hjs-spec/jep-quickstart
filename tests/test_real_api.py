import json
from pathlib import Path
import subprocess
import sys
import pytest
from jep import JEPAPIError
from jep_quickstart import create_event, export_archive, replay_verify, wrap_tool

ROOT = Path(__file__).resolve().parents[1]


def test_signed_tool_and_archival_replay(tmp_path):
    wrapped = wrap_tool("addition", lambda a, b: a + b)
    result, event = wrapped(a=2, b=3)
    assert result == 5
    assert event.jep == "1" and event.verb == "J" and event.sig
    path = export_archive([event], tmp_path / "archive.jsonl")
    assert json.loads(path.read_text()) == event.to_dict()
    report = replay_verify(path)
    assert report["ok"] and report["level"] == 1
    assert replay_verify(path) == report  # archival verification is repeatable
    with pytest.raises(FileExistsError):
        export_archive([event], path)
    tampered = event.to_dict()
    tampered["what"]["claim"] = "tampered"
    path.write_text(json.dumps(tampered) + "\n")
    with pytest.raises(ValueError, match="verification failed"):
        replay_verify(path)


@pytest.mark.parametrize(
    "content",
    [
        "",
        "{}\n",
        '{"jep":"0.1","kind":"tool"}\n',
        '{"verb":"J","verb":"D"}\n',
        '{"what":NaN}\n',
        "[]\n",
    ],
)
def test_reject_invalid_archives(tmp_path, content):
    path = tmp_path / "bad.jsonl"
    path.write_text(content)
    with pytest.raises((ValueError, JEPAPIError)) as exc:
        replay_verify(path)
    assert exc.value


def test_duplicate_event(tmp_path):
    event = create_event("test", "duplicate", {}, {})
    path = export_archive([event, event], tmp_path / "duplicate.jsonl")
    with pytest.raises(ValueError, match="Duplicate event"):
        replay_verify(path)


@pytest.mark.parametrize(
    "example",
    [
        "python_quickstart.py",
        "mcp_quickstart.py",
        "langgraph_quickstart.py",
        "openai_agents_quickstart.py",
    ],
)
def test_documented_examples(tmp_path, example):
    result = subprocess.run(
        [sys.executable, str(ROOT / "examples" / example)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr
