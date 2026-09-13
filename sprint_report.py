import argparse
import json
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path
from typing import Any


DONE_STATES = {"Hecho", "Done", "Completado"}


def sample_tasks(today: date | None = None) -> list[dict[str, Any]]:
    base = today or date.today()
    return [
        {"id": "T-01", "titulo": "Separar ambientes dev staging produccion", "responsable": "Dev 1", "estado": "Bloqueado", "story_points": 8, "fecha_limite": str(base + timedelta(days=2)), "ultima_actualizacion": str(base - timedelta(days=4))},
        {"id": "T-02", "titulo": "Rotar credenciales expuestas", "responsable": "Dev 2", "estado": "Bloqueado", "story_points": 5, "fecha_limite": str(base - timedelta(days=1)), "ultima_actualizacion": str(base - timedelta(days=1))},
        {"id": "T-03", "titulo": "Configurar GitHub Secrets", "responsable": "Dev 1", "estado": "Por hacer", "story_points": 3, "fecha_limite": str(base + timedelta(days=4)), "ultima_actualizacion": str(base)},
        {"id": "T-04", "titulo": "Revision trimestral de accesos", "responsable": "Soporte", "estado": "Por hacer", "story_points": 3, "fecha_limite": str(base + timedelta(days=8)), "ultima_actualizacion": str(base - timedelta(days=2))},
        {"id": "T-05", "titulo": "Healthcheck con auto recuperacion", "responsable": "Dev 1", "estado": "En progreso", "story_points": 5, "fecha_limite": str(base + timedelta(days=1)), "ultima_actualizacion": str(base)},
        {"id": "T-06", "titulo": "Reporte automatico de sprint", "responsable": "QA", "estado": "En progreso", "story_points": 5, "fecha_limite": str(base + timedelta(days=3)), "ultima_actualizacion": str(base - timedelta(days=1))},
        {"id": "T-07", "titulo": "Documentar flujos criticos N8N", "responsable": "Automation", "estado": "Por hacer", "story_points": 8, "fecha_limite": str(base + timedelta(days=5)), "ultima_actualizacion": str(base - timedelta(days=5))},
        {"id": "T-08", "titulo": "Alertas de incidencias", "responsable": "Automation", "estado": "En revision", "story_points": 5, "fecha_limite": str(base + timedelta(days=2)), "ultima_actualizacion": str(base)},
        {"id": "T-09", "titulo": "KPIs de entrega calidad operacion", "responsable": "Soporte", "estado": "Hecho", "story_points": 3, "fecha_limite": str(base - timedelta(days=2)), "ultima_actualizacion": str(base - timedelta(days=2))},
        {"id": "T-10", "titulo": "Dashboard ejecutivo", "responsable": "QA", "estado": "Hecho", "story_points": 5, "fecha_limite": str(base - timedelta(days=1)), "ultima_actualizacion": str(base - timedelta(days=1))},
        {"id": "T-11", "titulo": "Criterios de aceptacion", "responsable": "Dev 2", "estado": "Hecho", "story_points": 3, "fecha_limite": str(base), "ultima_actualizacion": str(base)},
        {"id": "T-12", "titulo": "Protocolo proveedor SAT", "responsable": "Soporte", "estado": "Por hacer", "story_points": 3, "fecha_limite": str(base + timedelta(days=9)), "ultima_actualizacion": str(base - timedelta(days=1))},
        {"id": "T-13", "titulo": "Pipeline con aprobaciones", "responsable": "Dev 1", "estado": "Hecho", "story_points": 5, "fecha_limite": str(base - timedelta(days=3)), "ultima_actualizacion": str(base - timedelta(days=3))},
        {"id": "T-14", "titulo": "Matriz RBAC", "responsable": "Dev 2", "estado": "En revision", "story_points": 3, "fecha_limite": str(base + timedelta(days=1)), "ultima_actualizacion": str(base - timedelta(days=1))},
        {"id": "T-15", "titulo": "Inventario de secretos", "responsable": "Automation", "estado": "Hecho", "story_points": 2, "fecha_limite": str(base - timedelta(days=1)), "ultima_actualizacion": str(base - timedelta(days=1))},
    ]


def ensure_data_file(path: Path) -> None:
    if not path.exists():
        path.write_text(json.dumps(sample_tasks(), indent=2, ensure_ascii=False), encoding="utf-8")


def load_tasks(path: Path) -> list[dict[str, Any]]:
    ensure_data_file(path)
    return json.loads(path.read_text(encoding="utf-8"))


def analyze(tasks: list[dict[str, Any]]) -> dict[str, Any]:
    committed = sum(task["story_points"] for task in tasks)
    completed = sum(task["story_points"] for task in tasks if task["estado"] in DONE_STATES)
    load = defaultdict(lambda: {"assigned": 0, "completed": 0, "count": 0})
    for task in tasks:
        owner = task["responsable"]
        points = task["story_points"]
        load[owner]["assigned"] += points
        load[owner]["completed"] += points if task["estado"] in DONE_STATES else 0
        load[owner]["count"] += 1
    return {"committed": committed, "completed": completed, "velocity_pct": round((completed / committed) * 100, 1) if committed else 0, "load": dict(load)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Genera reporte de sprint")
    parser.add_argument("--data", default="sprint_data.json")
    args = parser.parse_args()
    print(json.dumps(analyze(load_tasks(Path(args.data))), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())