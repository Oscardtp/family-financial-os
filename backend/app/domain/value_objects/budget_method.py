from enum import Enum


class BudgetMethodType(str, Enum):
    """FASE 6.2 — Preset budget allocation method types."""
    CUSTOM = "custom"


def _g(key: str, label: str, pct: int) -> dict:
    return {"key": key, "label": label, "pct": pct}


METHOD_PRESETS: tuple = (
    {
        "id": "50_30_20",
        "name": "50/30/20",
        "description": "El clásico: cubre lo esencial, disfruta y ahorra sin complicarte.",
        "groups": [_g("necesidades", "Necesidades", 50), _g("gustos", "Gustos", 30), _g("ahorro", "Ahorro", 20)],
    },
    {
        "id": "70_20_10",
        "name": "70/20/10",
        "description": "Para cuando el ahorro es prioridad pero sin dejar de vivir.",
        "groups": [_g("gastos", "Gastos", 70), _g("ahorro", "Ahorro", 20), _g("deuda_donacion", "Deuda/Donación", 10)],
    },
    {
        "id": "60_40",
        "name": "60/40",
        "description": "Gasta en lo necesario y guarda casi la mitad. Simple y potente.",
        "groups": [_g("gastos_fijos", "Gastos fijos", 60), _g("libre", "Libre", 40)],
    },
    {
        "id": "6_jarras",
        "name": "6 Jarras",
        "description": "El método de T. Harv Eker: seis destinos para cada peso que entra.",
        "groups": [
            _g("necesidades", "Necesidades", 55),
            _g("ahorro_largo", "Ahorro largo plazo", 10),
            _g("educacion", "Educación", 10),
            _g("diversion", "Diversión", 10),
            _g("libertad", "Libertad financiera", 10),
            _g("donacion", "Donación", 5),
        ],
    },
    {
        "id": "80_20",
        "name": "80/20",
        "description": "Págate a ti primero: aparta el 20% y vive con el resto.",
        "groups": [_g("gastos", "Gastos", 80), _g("ahorro", "Ahorro", 20)],
    },
    {
        "id": "30_30_30_10",
        "name": "30/30/30/10",
        "description": "Equilibrio con techo para vivienda: nada se come el presupuesto.",
        "groups": [
            _g("vivienda", "Vivienda", 30),
            _g("comida_transporte", "Comida/transporte", 30),
            _g("ahorro_deuda", "Ahorro/deuda", 30),
            _g("libre", "Libre", 10),
        ],
    },
    {
        "id": "75_15_10",
        "name": "75/15/10",
        "description": "Tres cuartos a lo esencial, un gusto medido y ahorro constante.",
        "groups": [_g("gastos", "Gastos", 75), _g("ahorro", "Ahorro", 15), _g("deuda", "Deuda", 10)],
    },
    {
        "id": "40_30_20_10",
        "name": "40/30/20/10",
        "description": "Reparte en cuatro: vivir, disfrutar, ahorrar e invertir.",
        "groups": [
            _g("necesidades", "Necesidades", 40),
            _g("gustos", "Gustos", 30),
            _g("ahorro", "Ahorro", 20),
            _g("donacion", "Donación", 10),
        ],
    },
    {
        "id": "50_50",
        "name": "50/50",
        "description": "Mitad y mitad: cubre tus gastos y construye futuro a la par.",
        "groups": [_g("fijos", "Fijos", 50), _g("variables", "Variables", 50)],
    },
    {
        "id": "70_30",
        "name": "70/30",
        "description": "Gasta con calma y ahorra casi un tercio sin darte cuenta.",
        "groups": [_g("gastos", "Gastos", 70), _g("ahorro", "Ahorro", 30)],
    },
    {
        "id": "33_33_33",
        "name": "33/33/33",
        "description": "Tres partes iguales: necesidades, ahorro y gustos en balance.",
        "groups": [_g("necesidades", "Necesidades", 34), _g("ahorro", "Ahorro", 33), _g("gustos", "Gustos", 33)],
    },
)


def list_presets() -> list:
    """FASE 6.3B — Static catalog. Never persisted as household financial data."""
    return [dict(p, groups=[dict(g) for g in p["groups"]]) for p in METHOD_PRESETS]


def get_preset(preset_id: str) -> dict | None:
    """FASE 6.3B — Find a preset by id, or None if unknown."""
    for preset in METHOD_PRESETS:
        if preset["id"] == preset_id:
            return dict(preset, groups=[dict(g) for g in preset["groups"]])
    return None
