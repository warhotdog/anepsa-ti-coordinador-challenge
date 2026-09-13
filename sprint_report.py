import argparse
import json
from datetime import date, timedelta
from pathlib import Path
from typing import Any


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


def main() -> int:
    parser = argparse.ArgumentParser(description="Genera datos de sprint")
    parser.add_argument("--data", default="sprint_data.json")
    args = parser.parse_args()
    ensure_data_file(Path(args.data))
    print(f"Datos listos en {args.data}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())