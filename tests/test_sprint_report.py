from datetime import date
from pathlib import Path

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