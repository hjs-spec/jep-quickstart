# JEP Quickstart

Five-minute developer quickstart for integrating a JEP Runtime into agents, tools, and workflows.

## What is JEP Runtime?

JEP Runtime records important execution moments as portable events: agent steps, tool calls, MCP calls, and graph nodes.

This repo is intentionally tiny. It uses a local mock runtime so you can see the integration shape before wiring in a real SDK.

## Install

```bash
git clone <this-repo>
cd jep-quickstart
python3 --version
```

Install is just a clone: the quickstart uses only the Python standard library and runs directly from the repo.

## First Event

```python
from jep_quickstart import create_event

event = create_event(
    kind="agent.step",
    name="first-event",
    input={"goal": "try JEP"},
    output={"status": "started"},
)
print(event.to_dict())
```

Run it as part of the Python quickstart:

```bash
python3 examples/python_quickstart.py
```

## Wrap a Tool

```python
from jep_quickstart import wrap_tool


def mock_search(query: str) -> dict[str, str]:
    return {"title": "JEP Quickstart", "query": query}

search = wrap_tool("mock_search", mock_search)
result, event = search(query="how to integrate JEP")
```

More examples:

- `examples/mcp_quickstart.py` wraps a mock MCP tool call and generates a JEP event.
- `examples/langgraph_quickstart.py` runs a minimal graph-shaped node that emits a JEP event.
- `examples/openai_agents_quickstart.py` shows pseudo middleware for OpenAI Agents tool calls.

## Replay Archive

Export and verify a JSONL archive:

```python
from jep_quickstart import export_archive, replay_verify

archive = export_archive([event], "archives/demo.jep.jsonl")
report = replay_verify(archive)
print(report)
```

## One Command Demo

```bash
make demo
```

The demo runs all quickstarts and writes `archives/demo.jep.jsonl`.

## Next Steps

- Replace the mock runtime in `jep_quickstart/runtime.py` with the real JEP SDK.
- Add your production tool names and inputs.
- Store archives in CI or object storage.
- Replay archives before changing agent prompts, tools, or graph nodes.
