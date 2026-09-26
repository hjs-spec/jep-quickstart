# Release 0.7.0

A reproducible local entry point for JEP Core 0.7 using the released Python SDK and a pinned reference API revision.

- Signed tool calls, JSONL export, archival replay and tamper detection are tested over real loopback HTTP.
- The LangGraph-style example uses Event Identity instead of the removed Core nonce.
- Replay checks syntax, signatures and Event Identity independently.
- Tests fail rather than skip when the reference API is unavailable.
- GitHub release includes the wheel and source distribution; no new package-registry credentials are required.
