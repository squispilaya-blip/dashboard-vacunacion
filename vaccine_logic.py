# -*- coding: utf-8 -*-
from datetime import date
from typing import Optional

# ─── Constantes de estado ────────────────────────────────────────────────────
APLICADA       = "APLICADA"
PENDIENTE      = "PENDIENTE"
FUERA_EDAD     = "FUERA DE EDAD"
NO_APLICA_AUN  = "NO APLICA AÚN"
NO_CORRESPONDE = "NO CORRESPONDE"
ERROR_DU       = "ERROR: DEBE SER DU"

# Íconos para la tabla del dashboard
STATUS_ICONS = {
    APLICADA:       "✅",
    PENDIENTE:      "⚠️",
    FUERA_EDAD:     "🚫",
    NO_APLICA_AUN:  "—",
    NO_CORRESPONDE: "N/A",
    ERROR_DU:       "🔴",
}

# Colores de fondo para Excel exportado (hex sin #)
STATUS_COLORS = {
    APLICADA:       "C6EFCE",   # verde claro
    PENDIENTE:      "FFEB9C",   # amarillo
    FUERA_EDAD:     "FFCC99",   # naranja
    NO_APLICA_AUN:  "FFFFFF",   # blanco
    NO_CORRESPONDE: "F2F2F2",   # gris claro
    ERROR_DU:       "FF0000",   # rojo
}

# ─── Umbrales de edad en días ─────────────────────────────────────────────────
M2  = 60;   M4  = 120;  M6  = 182;  M7  = 213;  M8  = 243
M12 = 365;  M15 = 456;  M18 = 547;  M23 = 700
Y2  = 730;  Y3  = 1095; Y4  = 1460; Y5  = 1825; Y7  = 2555

# ─── Esquema NTS N°196-MINSA/DGIESP-2022 ─────────────────────────────────────
# seq:      número de dosis (1-based)
# label:    etiqueta esperada según norma
# min_days: edad mínima en días para que se considere pendiente
# max_days: edad máxima en días (None = sin límite superior)
# is_du:    True si la vacuna es de dosis única (etiqueta correcta: "DU")
SCHEME = {
    "BCG": [
        {"seq": 1, "label": "DU",    "min_days": 0,       "max_days": M12,    "is_du": True},
    ],
    "HVB": [
        {"seq": 1, "label": "DU",    "min_days": 0,       "max_days": 7,      "is_du": True},
    ],
    "PENTAVALENTE": [
        {"seq": 1, "label": "1ra",   "min_days": M2,      "max_days": Y7,     "is_du": False},
        {"seq": 2, "label": "2da",   "min_days": M4,      "max_days": Y7,     "is_du": False},
        {"seq": 3, "label": "3ra",   "min_days": M6,      "max_days": Y7,     "is_du": False},
    ],
    "IPV": [
        {"seq": 1, "label": "1ra",   "min_days": M2,      "max_days": Y4,     "is_du": False},
        {"seq": 2, "label": "2da",   "min_days": M4,      "max_days": Y4,     "is_du": False},
        {"seq": 3, "label": "3ra",   "min_days": M6,      "max_days": Y4,     "is_du": False},
        {"seq": 4, "label": "DA",    "min_days": M18,     "max_days": None,   "is_du": False},
    ],
    "ROTAVIRUS": [
        {"seq": 1, "label": "1ra",   "min_days": M2,      "max_days": M8,     "is_du": False},
        {"seq": 2, "label": "2da",   "min_days": M4,      "max_days": M8,     "is_du": False},
    ],
    "NEUMOCOCO": [
        {"seq": 1, "label": "1ra",   "min_days": M2,      "max_days": Y4,     "is_du": False},
        {"seq": 2, "label": "2da",   "min_days": M4,      "max_days": M23,    "is_du": False},
        {"seq": 3, "label": "3ra",   "min_days": M12,     "max_days": None,   "is_du": False},
    ],
    "SPR": [
        {"seq": 1, "label": "1ra",   "min_days": M12,     "max_days": Y5,     "is_du": False},
        {"seq": 2, "label": "2da",   "min_days": M18,     "max_days": Y5,     "is_du": False},
    ],
    "VARICELA": [
        {"seq": 1, "label": "DU",    "min_days": M12,     "max_days": Y4,     "is_du": True},
    ],
    "HEPATITIS A": [
        {"seq": 1, "label": "DU",    "min_days": M15,     "max_days": Y5,     "is_du": True},
    ],
    "AMARILICA": [
        {"seq": 1, "label": "DU",    "min_days": M15,     "max_days": 59*365, "is_du": True},
    ],
    "DPT": [
        {"seq": 1, "label": "1er R", "min_days": M18,     "max_days": Y7,     "is_du": False},
        {"seq": 2, "label": "2do R", "min_days": Y4,      "max_days": Y7,     "is_du": False},
    ],
    "APO": [
        {"seq": 1, "label": "DA",    "min_days": Y4,      "max_days": Y5,     "is_du": False},
    ],
    "dT": [
        {"seq": 1, "label": "1ra",   "min_days": Y7,      "max_days": None,   "is_du": False},
        {"seq": 2, "label": "2da",   "min_days": Y7 + 60, "max_days": None,   "is_du": False},
        {"seq": 3, "label": "3ra",   "min_days": Y7 + 180,"max_days": None,   "is_du": False},
    ],
    "HiB": [
        {"seq": 1, "label": "1ra",   "min_days": M2,      "max_days": Y7,     "is_du": False},
        {"seq": 2, "label": "2da",   "min_days": M4,      "max_days": Y7,     "is_du": False},
        {"seq": 3, "label": "3ra",   "min_days": M6,      "max_days": Y7,     "is_du": False},
        {"seq": 4, "label": "DA",    "min_days": M18,     "max_days": Y7,     "is_du": False},
    ],
}


def _dose_status(dose_def: dict, parsed_doses: list, age_days: int) -> dict:
    """Calcula el estado de una sola dosis esperada."""
    seq = dose_def["seq"]
    base = {
        "seq": seq,
        "label": dose_def["label"],
        "applied_date": None,
        "applied_label": None,
    }

    if len(parsed_doses) >= seq:
        applied_label, applied_date = parsed_doses[seq - 1]
        if dose_def["is_du"] and applied_label.upper() != "DU":
            return {**base, "status": ERROR_DU,
                    "applied_date": applied_date, "applied_label": applied_label}
        return {**base, "status": APLICADA,
                "applied_date": applied_date, "applied_label": applied_label}

    if age_days < dose_def["min_days"]:
        return {**base, "status": NO_APLICA_AUN}

    max_d = dose_def.get("max_days")
    if max_d is not None and age_days > max_d:
        return {**base, "status": FUERA_EDAD}

    return {**base, "status": PENDIENTE}


def _influenza_status(column: str, parsed_doses: list, age_days: int) -> list:
    """Lógica especial para influenza pediátrica y adulto."""
    current_year = date.today().year
    applied_years = {d.year for _, d in parsed_doses}
    has_current = current_year in applied_years

    def _annual_entry():
        dt  = next((d for _, d in parsed_doses if d.year == current_year), None)
        lbl = next((l for l, d in parsed_doses if d.year == current_year), None)
        st_ = APLICADA if has_current else PENDIENTE
        return {"seq": 1, "label": "DA anual", "status": st_,
                "applied_date": dt, "applied_label": lbl}

    _na = {"seq": 1, "label": "—", "status": NO_APLICA_AUN,
           "applied_date": None, "applied_label": None}
    _nc = {"seq": 1, "label": "—", "status": NO_CORRESPONDE,
           "applied_date": None, "applied_label": None}

    if column == "INFLUENZA PEDIATRICA":
        if age_days < M6:
            return [_na]
        elif age_days < M12:          # 6–11 meses: necesita 2 dosis
            results = []
            for seq, lbl in [(1, "1ra"), (2, "2da")]:
                if len(parsed_doses) >= seq:
                    al, ad = parsed_doses[seq - 1]
                    results.append({"seq": seq, "label": lbl, "status": APLICADA,
                                    "applied_date": ad, "applied_label": al})
                else:
                    results.append({"seq": seq, "label": lbl, "status": PENDIENTE,
                                    "applied_date": None, "applied_label": None})
            return results
        elif age_days < Y3:           # 1 año – 2 años 11m: dosis anual
            return [_annual_entry()]
        else:                         # ≥ 3 años → corresponde Influenza Adulto
            return [_nc]

    elif column == "INFLUENZA ADULTO":
        if age_days < Y3:             # < 3 años → corresponde Influenza Pediátrica
            return [_nc]
        else:                         # ≥ 3 años: dosis anual
            return [_annual_entry()]

    return []


def get_vaccine_status(column: str, parsed_doses: list, age_days: int) -> list:
    """
    Retorna lista de dicts con el estado de cada dosis esperada.

    Cada dict: {seq, label, status, applied_date, applied_label}
    """
    if column in ("INFLUENZA PEDIATRICA", "INFLUENZA ADULTO"):
        return _influenza_status(column, parsed_doses, age_days)

    scheme = SCHEME.get(column, [])
    return [_dose_status(d, parsed_doses, age_days) for d in scheme]


def format_dose_cell(dose_results: list) -> str:
    """Convierte lista de resultados de dosis en texto para mostrar en tabla."""
    if not dose_results:
        return "—"
    lines = []
    for r in dose_results:
        icon = STATUS_ICONS.get(r["status"], "?")
        if r["status"] == APLICADA:
            lines.append(f"{icon} {r['applied_label']}: {r['applied_date'].strftime('%d/%m/%Y')}")
        elif r["status"] == ERROR_DU:
            lines.append(
                f"{icon} ERROR '{r['applied_label']}' → DEBE SER DU "
                f"({r['applied_date'].strftime('%d/%m/%Y')})"
            )
        else:
            lines.append(f"{icon} {r['status']}")
    return "\n".join(lines)


_NEEDS_ATTENTION = {PENDIENTE, ERROR_DU}


def patient_has_pending(vaccine_results: dict) -> bool:
    """True si el paciente tiene al menos una dosis PENDIENTE o ERROR_DU.
    ERROR_DU requiere atención clínica igual que PENDIENTE."""
    return any(
        r["status"] in _NEEDS_ATTENTION
        for results in vaccine_results.values()
        for r in results
    )


def patient_pending_list(vaccine_results: dict) -> str:
    """Retorna nombres de vacunas con dosis PENDIENTE o ERROR_DU separados por coma."""
    pending = [
        col for col, results in vaccine_results.items()
        if any(r["status"] in _NEEDS_ATTENTION for r in results)
    ]
    return ", ".join(pending) if pending else ""


def worst_status_color(dose_results: list) -> str:
    """
    Retorna el color hex para la celda según el peor estado de las dosis.
    Orden de prioridad: ERROR_DU > FUERA_EDAD > PENDIENTE > APLICADA > NO_CORRESPONDE > NO_APLICA_AUN
    """
    if not dose_results:
        return STATUS_COLORS[NO_APLICA_AUN]
    statuses = [r["status"] for r in dose_results]
    for priority_status in (ERROR_DU, FUERA_EDAD, PENDIENTE):
        if priority_status in statuses:
            return STATUS_COLORS[priority_status]
    if all(s == APLICADA for s in statuses):
        return STATUS_COLORS[APLICADA]
    if all(s == NO_CORRESPONDE for s in statuses):
        return STATUS_COLORS[NO_CORRESPONDE]
    return STATUS_COLORS[NO_APLICA_AUN]
