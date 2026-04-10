import streamlit as st
import pandas as pd
from vaccine_logic import format_dose_cell, STATUS_ICONS, PENDIENTE, ERROR_DU, FUERA_EDAD, patient_has_pending
from parser import VACCINE_COLUMNS


def build_display_df(processed_patients: list) -> pd.DataFrame:
    """
    Convierte la lista de pacientes procesados en un DataFrame para mostrar.
    """
    rows = []
    for p in processed_patients:
        row = {
            "DNI":          p["DNI"],
            "Nombres":      p["Nombres"],
            "Sexo":         p["Sexo"],
            "F.Nacimiento": p["F_Nacimiento"],
            "Edad":         p["Edad"],
            "Grupo":        p["Grupo"],
            "Red":          p["Red"],
            "Microred":     p["Microred"],
            "EESS":         p["EESS"],
        }
        for col in VACCINE_COLUMNS:
            dose_results = p["vaccines"].get(col, [])
            row[col] = format_dose_cell(dose_results)
        rows.append(row)
    return pd.DataFrame(rows)


def render_summary(processed_patients: list) -> None:
    """Muestra contadores resumen encima de la tabla."""
    total      = len(processed_patients)
    pendientes = sum(1 for p in processed_patients if patient_has_pending(p["vaccines"]))
    completos  = total - pendientes

    col1, col2, col3 = st.columns(3)
    col1.metric("Total filtrados", total)
    col2.metric(
        "Con pendientes / errores",
        pendientes,
        delta=f"{pendientes/total*100:.1f}%" if total else "0%",
    )
    col3.metric(
        "Completos",
        completos,
        delta=f"{completos/total*100:.1f}%" if total else "0%",
    )


def render_patient_table(processed_patients: list) -> None:
    """Renderiza la tabla completa de pacientes con estados de vacunas."""
    if not processed_patients:
        st.warning("No hay pacientes con los filtros aplicados.")
        return

    render_summary(processed_patients)
    st.divider()

    display_df = build_display_df(processed_patients)
    st.dataframe(
        display_df,
        use_container_width=True,
        height=600,
        column_config={
            "DNI":          st.column_config.TextColumn("DNI",        width="small"),
            "Nombres":      st.column_config.TextColumn("Nombres",    width="medium"),
            "F.Nacimiento": st.column_config.TextColumn("F.Nac.",     width="small"),
            "Edad":         st.column_config.TextColumn("Edad",       width="small"),
            "Grupo":        st.column_config.TextColumn("Grupo",      width="small"),
        },
        hide_index=True,
    )
