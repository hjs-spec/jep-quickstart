"""Quickstart LangGraph: minimal graph-shaped flow producing a JEP event."""

import _bootstrap

from jep_quickstart import create_event


def enrich_node(state: dict[str, str]) -> dict[str, str]:
    output = {**state, "summary": f"hello {state['user']}"}
    event = create_event("langgraph.node", "enrich_node", state, output, actor="langgraph")
    output["jep_event_id"] = event.event_id
    print("jep event:", event.to_dict())
    return output


def run_graph() -> dict[str, str]:
    state = {"user": "developer"}
    return enrich_node(state)


if __name__ == "__main__":
    print("graph output:", run_graph())
