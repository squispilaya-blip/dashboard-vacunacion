import streamlit as st
import pandas as pd


def render_filters(df: pd.DataFrame) -> dict:
    """
    Renderiza filtros en el sidebar.
    Retorna dict con los valores seleccionados.
    """
    st.sidebar.header("🔍 Filtros")

    redes      = sorted(df["RED"].dropna().unique().tolist())
    microredes = sorted(df["MICRORED"].dropna().unique().tolist())
    eess_list  = sorted(df["EESS_ATN"].dropna().unique().tolist())
    sexos      = sorted(df["SEXO"].dropna().unique().tolist())
    grupos     = ["< 1 año", "1 año", "2 años", "3 años", "4 años"]

    red_sel      = st.sidebar.multiselect("Red", redes)
    microred_sel = st.sidebar.multiselect("Microred", microredes)
    eess_sel     = st.sidebar.multiselect("EESS", eess_list)
    grupo_sel    = st.sidebar.multiselect("Grupo etario", grupos)
    sexo_sel     = st.sidebar.multiselect("Sexo", sexos)
    dni_txt      = st.sidebar.text_input("DNI (búsqueda exacta)")
    nombre_txt   = st.sidebar.text_input("Nombre (búsqueda parcial)")
    solo_pend    = st.sidebar.checkbox("Solo con vacunas pendientes", value=False)

    return {
        "red": red_sel,
        "microred": microred_sel,
        "eess": eess_sel,
        "grupo": grupo_sel,
        "sexo": sexo_sel,
        "dni": dni_txt.strip(),
        "nombre": nombre_txt.strip().lower(),
        "solo_pendientes": solo_pend,
    }


def apply_filters(df: pd.DataFrame, filters: dict, age_groups: pd.Series) -> pd.DataFrame:
    """
    Aplica los filtros al DataFrame.
    age_groups: Serie con el grupo etario de cada fila (mismo índice que df).
    """
    mask = pd.Series([True] * len(df), index=df.index)

    if filters["red"]:
        mask &= df["RED"].isin(filters["red"])
    if filters["microred"]:
        mask &= df["MICRORED"].isin(filters["microred"])
    if filters["eess"]:
        mask &= df["EESS_ATN"].isin(filters["eess"])
    if filters["grupo"]:
        mask &= age_groups.isin(filters["grupo"])
    if filters["sexo"]:
        mask &= df["SEXO"].isin(filters["sexo"])
    if filters["dni"]:
        mask &= df["DNI"].astype(str).str.contains(filters["dni"], na=False)
    if filters["nombre"]:
        mask &= df["NOMBRES"].str.lower().str.contains(filters["nombre"], na=False)

    return df[mask].copy()
