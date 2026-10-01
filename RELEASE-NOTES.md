# Software 0.7.2

- Use Python SDK 0.7.1+ and test against the API 0.8.7 release so the documented dependency path includes the new license materials.

- License original Quickstart code, examples and implementation documentation under BSD-3-Clause.
- Include LICENSE and NOTICE.md in wheel and source distributions with SPDX metadata, and check those files during CI and release validation.

Runtime behavior and JEP Core 0.7 semantics are unchanged. Existing published artifacts are not overwritten.

# Release 0.7.1

- Distinguish recording failures before and after a wrapped business call with `RecordingError.call_executed`; retain the completed result and serializable request for recovery.
- Add `retry_recording()` to resend only the original request. It never reruns the callable. Preserve business exceptions and snapshot input before invocation.
- Add a caller-supplied `event_id` option to direct `create_event` calls. Safe recovery requires API 0.8.6+ and preserved server state.
- Cover lost responses over real HTTP, repeated recording failures, unserializable values and request conflicts; document process-restart limits.

The release includes a wheel and source distribution on GitHub. Core 0.7 semantics and archival verification are unchanged.

# Release 0.7.0

A reproducible local entry point for JEP Core 0.7 using the released Python SDK and a pinned reference API revision.

- Signed tool calls, JSONL export, archival replay and tamper detection are tested over real loopback HTTP.
- The LangGraph-style example uses Event Identity instead of the removed Core nonce.
- Replay checks syntax, signatures and Event Identity independently.
- Tests fail rather than skip when the reference API is unavailable.
- GitHub release includes the wheel and source distribution; no new package-registry credentials are required.
