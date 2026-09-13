# Historical mock

`legacy_mock.py` preserves the original unsigned `jep: "0.1"` demonstration. Import it explicitly (`from jep_quickstart.legacy_mock import create_event`) only to inspect old examples. Its local replay checks do not verify JEP-Core-0.6 signatures, authenticity, or completeness. The default package exports use the real SDK/API and reject this old format.
