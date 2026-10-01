"""Recover recording over real HTTP without repeating an executed business call."""

import time
from uuid import uuid4

import pytest
from jep import JEPAPIError
from jep_quickstart import RecordingError, create_event, export_archive, replay_verify, wrap_tool
from jep_quickstart import runtime


def test_lost_response_recovers_original_without_repeating_business(monkeypatch, tmp_path):
    real_client = runtime.client()
    calls = []
    committed = []

    class LoseResponse:
        def create_event(self, request):
            committed.append(real_client.create_event(request).event)
            # The old API created a conflicting artifact after the clock advanced.
            time.sleep(1.1)
            raise ConnectionError("response lost after commit")

    monkeypatch.setattr(runtime, "client", lambda: LoseResponse())
    wrapped = wrap_tool("charge", lambda amount: calls.append(amount) or {"paid": amount})
    with pytest.raises(RecordingError) as caught:
        wrapped(amount=10)
    failure = caught.value
    assert failure.call_executed is True
    assert failure.result == {"paid": 10}
    assert isinstance(failure.__cause__, ConnectionError)
    original_request = failure.request
    changed_copy = failure.request
    changed_copy["what"]["claim"] = "changed"
    assert failure.request == original_request

    # Another recording failure also keeps the completed result and exact request.
    with pytest.raises(RecordingError) as repeated:
        failure.retry_recording()
    assert repeated.value.request == original_request
    assert repeated.value.result == failure.result
    assert calls == [10]
    monkeypatch.setattr(runtime, "client", lambda: real_client)
    recovered = repeated.value.retry_recording()
    assert recovered.to_dict() == committed[0].to_dict() == committed[1].to_dict()
    assert failure.retry_recording().to_dict() == recovered.to_dict()
    assert calls == [10]
    assert replay_verify(export_archive([recovered], tmp_path / "recovered.jsonl"))["ok"]


def test_explicit_create_id_recovers_and_rejects_changed_request():
    event_id = "urn:uuid:" + str(uuid4())
    first = create_event("test", "direct", {}, 1, event_id=event_id)
    assert create_event("test", "direct", {}, 1, event_id=event_id).to_dict() == first.to_dict()
    with pytest.raises(JEPAPIError) as caught:
        create_event("test", "direct", {}, 2, event_id=event_id)
    assert caught.value.status_code == 409


def test_unserializable_input_fails_before_business():
    calls = []
    with pytest.raises(RecordingError) as caught:
        wrap_tool("test", lambda value: calls.append(value))(value=object())
    assert caught.value.call_executed is False
    assert caught.value.request is None
    assert calls == []


def test_unserializable_result_requires_manual_recovery():
    result = object()
    calls = []
    with pytest.raises(RecordingError) as caught:
        wrap_tool("test", lambda: calls.append(1) or result)()
    assert caught.value.call_executed is True
    assert caught.value.result is result
    assert caught.value.request is None
    with pytest.raises(ValueError, match="resolve manually"):
        caught.value.retry_recording()
    assert calls == [1]


def test_business_exception_remains_original():
    error = RuntimeError("business failed")

    def business():
        raise error

    with pytest.raises(RuntimeError) as caught:
        wrap_tool("test", business)()
    assert caught.value is error


def test_records_input_snapshot_before_business_mutates_it():
    value = {"count": 1}

    def business(value):
        value["count"] = 2
        return value

    result, event = wrap_tool("test", business)(value=value)
    assert result == {"count": 2}
    context = event.to_dict()["what"]["context"]
    assert context == {"input": {"value": {"count": 1}}, "output": {"count": 2}}
