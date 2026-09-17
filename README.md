# ANEPSA TI Coordinador Challenge

[![CI](https://github.com/warhotdog/anepsa-ti-coordinador-challenge/actions/workflows/ci.yml/badge.svg)](https://github.com/warhotdog/anepsa-ti-coordinador-challenge/actions/workflows/ci.yml)

## Codigo De Verificacion

CTI-EVAL-2026

## Objetivo

Repositorio publico para la evaluacion tecnica de Coordinador de Area de TI.

Incluye los ejercicios obligatorios del Caso 2 y la evidencia tecnica requerida por el Caso 8.

## Contenido

- `healthcheck.py`: monitoreo de endpoint HTTP con reintentos, reinicio simulado, logging y notificacion simulada.
- `sprint_report.py`: reporte ejecutivo de sprint generado desde `sprint_data.json`.
- `tests/`: pruebas basicas automatizadas.
- `.github/workflows/ci.yml`: pipeline de CI en GitHub Actions.

## Tablero Jira

URL Jira prevista para entrega final:

```text
https://dsuzan.atlassian.net/jira/software/projects/ANEPSA/boards/1
```

## Instalacion

```bash
python -m pip install -r requirements.txt
```

## Ejecutar Pruebas

```bash
python -m pytest
```

## Ejecutar Scripts

```bash
python healthcheck.py --self-test
python sprint_report.py
```

## Comando Unico De Verificacion

```bash
python -m pytest && python healthcheck.py --self-test && python sprint_report.py
```
