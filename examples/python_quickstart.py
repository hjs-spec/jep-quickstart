"""Quickstart Python: create event, wrap a tool, export, replay."""

import _bootstrap

from jep_quickstart import create_event, export_archive, replay_verify, wrap_tool


def mock_search(query: str) -> dict[str, str]:
    return {"title": "JEP Quickstart", "query": query}


def main() -> None:
    events = []

    first_event = create_event(
        kind="agent.step",
        name="first-event",
        input={"goal": "try JEP"},
        output={"status": "started"},
    )
    events.append(first_event)

    search = wrap_tool("mock_search", mock_search)
    result, tool_event = search(query="how to integrate JEP")
    events.append(tool_event)

    archive = export_archive(events)
    report = replay_verify(archive)

    print("tool result:", result)
    print("archive:", archive)
    print("replay:", report)


if __name__ == "__main__":
    main()
