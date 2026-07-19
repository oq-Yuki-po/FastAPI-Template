import json
import logging
import sys

from app.core.logging import JsonFormatter


def test_json_formatter_emits_machine_readable_context() -> None:
    record = logging.LogRecord("app.test", logging.WARNING, __file__, 1, "failed %s", ("x",), None)
    payload = json.loads(JsonFormatter().format(record))
    assert payload["level"] == "WARNING"
    assert payload["logger"] == "app.test"
    assert payload["message"] == "failed x"
    assert payload["timestamp"].endswith("+00:00")


def test_json_formatter_includes_exception() -> None:
    try:
        raise ValueError("sensitive failure")
    except ValueError:
        exc_info = sys.exc_info()
    record = logging.LogRecord(
        "app.test", logging.ERROR, __file__, 1, "request failed", (), exc_info
    )

    payload = json.loads(JsonFormatter().format(record))

    assert "ValueError: sensitive failure" in payload["exception"]
