import json
import logging

from app.core.logging import JsonFormatter


def test_json_formatter_emits_machine_readable_context() -> None:
    record = logging.LogRecord("app.test", logging.WARNING, __file__, 1, "failed %s", ("x",), None)
    payload = json.loads(JsonFormatter().format(record))
    assert payload["level"] == "WARNING"
    assert payload["logger"] == "app.test"
    assert payload["message"] == "failed x"
    assert payload["timestamp"].endswith("+00:00")
