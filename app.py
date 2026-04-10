# -*- coding: utf-8 -*-
"""Dashboard de vacunación — NTS N° 196-MINSA/DGIESP-2022"""

import streamlit as st
import pandas as pd

from auth import require_auth
from parser import (
    load_excel, parse_doses, format_age_from_birth,
    age_days_from_birth, get_age_group, VACCINE_COLUMNS,
)
from vaccine_logic import get_vaccine_status, patient_has_pending
from ui_filters import render_filters, apply_filters
from ui_table import render_patient_table
from exporter import generate_excel

st.set_page_config(
    page_title="Sistema de Vacunación",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

require_auth()

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🏥 Dashboard de Vacunación")
st.caption("NTS N° 196-MINSA/DGIESP-2022 | RM 884-2022-MINSA")

# ── Botón de cierre de sesión ─────────────────────────────────────────────────
with st.sidebar:
    if st.button("🚪 Cerrar sesión"):
        st.session_state.clear()
        st.rerun()

# ── Carga de archivo ──────────────────────────────────────────────────────────
uploaded = st.file_uploader(
    "📂 Cargar padrón Excel (reporte..xlsx)",
    type=["xlsx"],
    help="Arrastra el archivo o haz clic para seleccionarlo.",
)

if not uploaded:
    st.info("Carga el padrón Excel para comenzar.")
    st.stop()

# ── Procesamiento del archivo (cacheado por contenido) ────────────────────────
@st.cache_data(show_spinner="Cargando padrón...")
def cached_load(file_bytes: bytes) -> pd.DataFrame:
    return load_excel(file_bytes)

file_bytes = uploaded.read()
try:
    df = cached_load(file_bytes)
except ValueError as e:
    st.error(str(e))
    st.stop()

fecha_corte = df["FECHA_CORTE_PADRON_N"].iloc[0] if "FECHA_CORTE_PADRON_N" in df.columns else "—"
st.sidebar.markdown(f"**Fecha de corte:** {fecha_corte}")
st.sidebar.markdown(f"**Total en padrón:** {len(df):,} pacientes")

# ── Calcular columnas derivadas ───────────────────────────────────────────────
df["_edad_str"]  = df["NINO_FECNAC"].apply(format_age_from_birth)
df["_edad_days"] = df["NINO_FECNAC"].apply(age_days_from_birth)
df["_grupo"]     = df["NINO_FECNAC"].apply(get_age_group)

# ── Filtros ───────────────────────────────────────────────────────────────────
filters     = render_filters(df)
filtered_df = apply_filters(df, filters, df["_grupo"])

# ── Procesamiento de vacunas ──────────────────────────────────────────────────
def build_processed(fdf: pd.DataFrame) -> list:
    result = []
    for _, row in fdf.iterrows():
        age_d = int(row["_edad_days"])
        vaccines = {}
        for col in VACCINE_COLUMNS:
            doses = parse_doses(row.get(col))
            vaccines[col] = get_vaccine_status(col, doses, age_d)
        result.append({
            "DNI":         str(row["DNI"]),
            "Nombres":     str(row["NOMBRES"]),
            "Sexo":        str(row["SEXO"]),
            "F_Nacimiento": row["NINO_FECNAC"].strftime("%d/%m/%Y"),
            "Edad":        row["_edad_str"],
            "Grupo":       row["_grupo"],
            "Red":         str(row["RED"]),
            "Microred":    str(row["MICRORED"]),
            "EESS":        str(row["EESS_ATN"]),
            "vaccines":    vaccines,
        })
    return result

with st.spinner("Procesando datos de vacunación..."):
    processed = build_processed(filtered_df)

# ── Filtro adicional: solo pendientes/errores ─────────────────────────────────
if filters["solo_pendientes"]:
    processed = [p for p in processed if patient_has_pending(p["vaccines"])]

# ── Tabla ─────────────────────────────────────────────────────────────────────
render_patient_table(processed)

# ── Exportar ──────────────────────────────────────────────────────────────────
st.divider()
col_exp, col_info = st.columns([1, 3])
with col_exp:
    if st.button("📥 Generar reporte Excel", use_container_width=True):
        with st.spinner("Generando Excel..."):
            excel_bytes = generate_excel(processed)
        st.download_button(
            label="⬇️ Descargar reporte",
            data=excel_bytes,
            file_name=f"reporte_vacunas_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
with col_info:
    st.caption(
        f"El reporte incluye {len(processed):,} pacientes en 2 hojas: "
        f"'Completo' y 'Pendientes'. La edad se calcula al día de hoy."
    )
