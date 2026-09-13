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