import json
from datetime import date
from pathlib import Path

import pytest

import sprint_report


def test_load_tasks_generates_sample_file(tmp_path: Path) -> None:
    data_file = tmp_path / "sprint_data.json"
    tasks = sprint_report.load_tasks(data_file)
    assert data_file.exists()
    assert len(tasks) >= 15
    assert {"id", "titulo", "responsable", "estado", "story_points", "fecha_limite", "ultima_actualizacion"}.issubset(tasks[0])


def test_analyze_calculates_velocity_risks_and_load() -> None:
    today = date(2026, 9, 11)
    tasks = [
        {"id": "A", "titulo": "Done task", "responsable": "Dev", "estado": "Hecho", "story_points": 5, "fecha_limite": "2026-09-10", "ultima_actualizacion": "2026-09-10"},
        {"id": "B", "titulo": "Overdue task", "responsable": "Dev", "estado": "En progreso", "story_points": 3, "fecha_limite": "2026-09-09", "ultima_actualizacion": "2026-09-11"},
        {"id": "C", "titulo": "Stale task", "responsable": "QA", "estado": "Por hacer", "story_points": 2, "fecha_limite": "2026-09-20", "ultima_actualizacion": "2026-09-01"},
    ]
    result = sprint_report.analyze(tasks, today=today)
    assert result["committed"] == 10
    assert result["completed"] == 5
    assert result["velocity_pct"] == 50.0
    assert len(result["risks"]) == 2
    assert result["load"]["Dev"]["assigned"] == 8


def test_load_tasks_rejects_malformed_json(tmp_path: Path) -> None:
    data_file = tmp_path / "bad.json"
    data_file.write_text("{not-json", encoding="utf-8")
    with pytest.raises(ValueError, match="JSON malformado"):
        sprint_report.load_tasks(data_file)


def test_load_tasks_sanitizes_missing_non_critical_fields(tmp_path: Path) -> None:
    data_file = tmp_path / "missing.json"
    data_file.write_text(json.dumps([{"id": "A", "story_points": "5"}, {"id": "B", "story_points": None}]), encoding="utf-8")
    tasks = sprint_report.load_tasks(data_file)
    assert tasks[0]["story_points"] == 5
    assert tasks[0]["titulo"] == "Sin titulo"
    assert tasks[1]["story_points"] == 0