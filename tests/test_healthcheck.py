import json
from pathlib import Path

import healthcheck


def test_monitor_healthy_logs_ok(tmp_path: Path) -> None:
    log_file = tmp_path / "health.log"
    code = healthcheck.monitor(
        endpoint="http://example.local/health",
        interval=0.01,
        timeout=2,
        max_failures=3,
        restart_command="simulate",
        log_file=log_file,
        once=True,
        checker=lambda endpoint, timeout: True,
    )
    assert code == 0
    assert "health_ok" in log_file.read_text(encoding="utf-8")


def test_monitor_down_retries_restarts_and_notifies(tmp_path: Path, capsys) -> None:
    log_file = tmp_path / "health.log"
    calls = {"count": 0}

    def checker(endpoint: str, timeout: float) -> bool:
        calls["count"] += 1
        return False

    code = healthcheck.monitor(
        endpoint="http://down.local/health",
        interval=0.01,
        timeout=2,
        max_failures=3,
        restart_command="simulate",
        log_file=log_file,
        once=False,
        checker=checker,
    )

    assert code == 2
    assert calls["count"] == 4
    log_text = log_file.read_text(encoding="utf-8")
    assert "consecutive_failures=3" in log_text
    assert "restart_attempt" in log_text
    assert "notify" in log_text
    payload = json.loads(capsys.readouterr().out)
    assert payload["event"] == "healthcheck_failed_after_restart"
    assert payload["severity"] == "critical"