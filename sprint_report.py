import argparse
import json
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any


REQUIRED_FIELDS = {"id", "titulo", "responsable", "estado", "story_points", "fecha_limite", "ultima_actualizacion"}
DONE_STATES = {"Hecho", "Done", "Completado"}
OVERLOAD_ABOVE_AVERAGE_RATIO = 1.35
OVERLOAD_ABSOLUTE_SP = 13
UNDERLOAD_BELOW_AVERAGE_RATIO = 0.65


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


def parse_date(value: str, field: str, task_id: str) -> date:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise ValueError(f"{task_id}: {field} debe tener formato YYYY-MM-DD") from exc


def sanitize_task(task: dict[str, Any], index: int, today: date | None = None) -> dict[str, Any]:
    current = today or date.today()
    sanitized = dict(task)
    sanitized.setdefault("id", f"TASK-{index}")
    sanitized.setdefault("titulo", "Sin titulo")
    sanitized.setdefault("responsable", "Sin responsable")
    sanitized.setdefault("estado", "Por hacer")
    sanitized.setdefault("fecha_limite", str(current))
    sanitized.setdefault("ultima_actualizacion", sanitized["fecha_limite"])

    raw_points = sanitized.get("story_points", 0)
    if raw_points is None or raw_points == "":
        sanitized["story_points"] = 0
    else:
        try:
            sanitized["story_points"] = int(raw_points)
        except (TypeError, ValueError):
            sanitized["story_points"] = 0
    if sanitized["story_points"] < 0:
        sanitized["story_points"] = 0

    parse_date(str(sanitized["fecha_limite"]), "fecha_limite", sanitized["id"])
    parse_date(str(sanitized["ultima_actualizacion"]), "ultima_actualizacion", sanitized["id"])
    sanitized["fecha_limite"] = str(sanitized["fecha_limite"])
    sanitized["ultima_actualizacion"] = str(sanitized["ultima_actualizacion"])
    return sanitized


def load_tasks(path: Path) -> list[dict[str, Any]]:
    ensure_data_file(path)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"JSON malformado en {path}: {exc}") from exc
    if not isinstance(data, list):
        raise ValueError("sprint_data.json debe contener una lista de tareas")
    sanitized_tasks = []
    for index, task in enumerate(data, start=1):
        if not isinstance(task, dict):
            raise ValueError(f"Tarea #{index} debe ser objeto JSON")
        sanitized_tasks.append(sanitize_task(task, index))
    return sanitized_tasks


def analyze(tasks: list[dict[str, Any]], today: date | None = None) -> dict[str, Any]:
    current = today or date.today()
    committed = sum(task["story_points"] for task in tasks)
    completed = sum(task["story_points"] for task in tasks if task["estado"] in DONE_STATES)

    risks = []
    load = defaultdict(lambda: {"assigned": 0, "completed": 0, "count": 0})
    for task in tasks:
        points = task["story_points"]
        owner = task["responsable"]
        done = task["estado"] in DONE_STATES
        due = parse_date(task["fecha_limite"], "fecha_limite", task["id"])
        updated = parse_date(task["ultima_actualizacion"], "ultima_actualizacion", task["id"])
        load[owner]["assigned"] += points
        load[owner]["completed"] += points if done else 0
        load[owner]["count"] += 1
        reasons = []
        if not done and due < current:
            reasons.append("vencida")
        if not done and (current - updated).days > 3:
            reasons.append("sin movimiento >3 dias")
        if reasons:
            risks.append({"id": task["id"], "titulo": task["titulo"], "responsable": owner, "story_points": points, "motivo": ", ".join(reasons)})

    average_assigned = committed / max(len(load), 1)
    load_summary = {}
    for owner, item in load.items():
        status = "balanceada"
        if item["assigned"] > average_assigned * OVERLOAD_ABOVE_AVERAGE_RATIO or item["assigned"] > OVERLOAD_ABSOLUTE_SP:
            status = "sobrecarga"
        elif item["assigned"] < average_assigned * UNDERLOAD_BELOW_AVERAGE_RATIO:
            status = "subutilizacion"
        load_summary[owner] = {**item, "status": status}

    return {"committed": committed, "completed": completed, "velocity_pct": round((completed / committed) * 100, 1) if committed else 0, "risks": risks, "load": dict(load_summary)}


def executive_report(analysis: dict[str, Any]) -> str:
    risks = analysis["risks"]
    load = analysis["load"]
    overloaded = [owner for owner, data in load.items() if data["status"] == "sobrecarga"]
    underused = [owner for owner, data in load.items() if data["status"] == "subutilizacion"]
    lines = [
        "Reporte ejecutivo de sprint - ANEPSA TI",
        "",
        f"Avance: {analysis['completed']} de {analysis['committed']} story points completados ({analysis['velocity_pct']}%).",
        f"Riesgo: {len(risks)} tareas requieren atencion por vencimiento o falta de movimiento.",
    ]
    if risks:
        lines.append("Principales bloqueos/riesgos:")
        for risk in risks[:5]:
            lines.append(f"- {risk['id']} ({risk['responsable']}): {risk['motivo']} - {risk['titulo']} ({risk['story_points']} SP).")
    if overloaded:
        lines.append(f"Carga: posible sobrecarga en {', '.join(overloaded)}; recomiendo reasignar trabajo antes de tomar alcance nuevo.")
    if underused:
        lines.append(f"Capacidad disponible: {', '.join(underused)} podria apoyar tareas de menor riesgo o validaciones.")
    lines.append("Decision requerida: confirmar ventana para rotacion de credenciales y ambiente staging para desbloquear seguridad.")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Genera reporte ejecutivo de sprint")
    parser.add_argument("--data", default="sprint_data.json")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    tasks = load_tasks(Path(args.data))
    print(executive_report(analyze(tasks)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())