import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date
import pytest
from vaccine_logic import get_vaccine_status, APLICADA, PENDIENTE, FUERA_EDAD, NO_APLICA_AUN, ERROR_DU, NO_CORRESPONDE


# --- BCG (DU, máx 365 días) ---

def test_bcg_aplicada_correctamente():
    doses = [("DU", date(2024, 12, 29))]
    result = get_vaccine_status("BCG", doses, 100)
    assert result[0]["status"] == APLICADA
    assert result[0]["applied_date"] == date(2024, 12, 29)


def test_bcg_error_du_dice_1ra():
    doses = [("1ra", date(2024, 12, 29))]
    result = get_vaccine_status("BCG", doses, 100)
    assert result[0]["status"] == ERROR_DU


def test_bcg_pendiente_menor_365():
    result = get_vaccine_status("BCG", [], 30)
    assert result[0]["status"] == PENDIENTE


def test_bcg_fuera_edad_mayor_365():
    result = get_vaccine_status("BCG", [], 400)
    assert result[0]["status"] == FUERA_EDAD


# --- HVB (DU, máx 7 días) ---

def test_hvb_fuera_edad():
    result = get_vaccine_status("HVB", [], 10)
    assert result[0]["status"] == FUERA_EDAD


def test_hvb_error_du():
    doses = [("1ra", date(2024, 12, 29))]
    result = get_vaccine_status("HVB", doses, 5)
    assert result[0]["status"] == ERROR_DU


def test_hvb_aplicada():
    doses = [("DU", date(2024, 12, 29))]
    result = get_vaccine_status("HVB", doses, 5)
    assert result[0]["status"] == APLICADA


# --- ROTAVIRUS (máx 243 días absoluto) ---

def test_rotavirus_fuera_edad_absoluto():
    result = get_vaccine_status("ROTAVIRUS", [], 250)
    assert all(d["status"] == FUERA_EDAD for d in result)


def test_rotavirus_1ra_aplicada_2da_pendiente():
    doses = [("1ra", date(2023, 5, 29))]
    result = get_vaccine_status("ROTAVIRUS", doses, 150)
    assert result[0]["status"] == APLICADA
    assert result[1]["status"] == PENDIENTE


def test_rotavirus_ambas_aplicadas():
    doses = [("1ra", date(2023, 5, 29)), ("2da", date(2023, 7, 30))]
    result = get_vaccine_status("ROTAVIRUS", doses, 200)
    assert all(d["status"] == APLICADA for d in result)


# --- PENTAVALENTE (3 dosis, máx 7 años) ---

def test_pentavalente_no_aplica_aun():
    result = get_vaccine_status("PENTAVALENTE", [], 30)
    assert result[0]["status"] == NO_APLICA_AUN


def test_pentavalente_2_aplicadas_1_pendiente():
    doses = [("1ra", date(2023, 5, 29)), ("2da", date(2023, 7, 30))]
    result = get_vaccine_status("PENTAVALENTE", doses, 200)
    assert result[0]["status"] == APLICADA
    assert result[1]["status"] == APLICADA
    assert result[2]["status"] == PENDIENTE


# --- VARICELA (DU, 12m-4a) ---

def test_varicela_error_du():
    doses = [("1ra", date(2023, 1, 1))]
    result = get_vaccine_status("VARICELA", doses, 400)
    assert result[0]["status"] == ERROR_DU


def test_varicela_fuera_edad():
    result = get_vaccine_status("VARICELA", [], 4*365 + 1)
    assert result[0]["status"] == FUERA_EDAD


def test_varicela_aplicada():
    doses = [("DU", date(2023, 6, 15))]
    result = get_vaccine_status("VARICELA", doses, 500)
    assert result[0]["status"] == APLICADA


# --- HEPATITIS A (DU) ---

def test_hepatitis_a_error_du():
    doses = [("1ra", date(2023, 1, 1))]
    result = get_vaccine_status("HEPATITIS A", doses, 500)
    assert result[0]["status"] == ERROR_DU


# --- AMARILICA (DU, fiebre amarilla) ---

def test_amarilica_error_du():
    doses = [("1ra", date(2023, 1, 1))]
    result = get_vaccine_status("AMARILICA", doses, 500)
    assert result[0]["status"] == ERROR_DU


# --- DPT (2 refuerzos) ---

def test_dpt_1er_refuerzo_pendiente():
    result = get_vaccine_status("DPT", [], 600)
    assert result[0]["status"] == PENDIENTE
    assert result[1]["status"] == NO_APLICA_AUN


def test_dpt_ambos_aplicados():
    doses = [("DA", date(2024, 6, 1)), ("DA", date(2026, 1, 1))]
    result = get_vaccine_status("DPT", doses, 4*365 + 10)
    assert result[0]["status"] == APLICADA
    assert result[1]["status"] == APLICADA


# --- HiB (4 dosis) ---

def test_hib_3_aplicadas_refuerzo_pendiente():
    doses = [
        ("1ra", date(2023, 5, 29)),
        ("2da", date(2023, 7, 30)),
        ("3ra", date(2023, 9, 26)),
    ]
    result = get_vaccine_status("HiB", doses, 600)
    assert result[0]["status"] == APLICADA
    assert result[1]["status"] == APLICADA
    assert result[2]["status"] == APLICADA
    assert result[3]["status"] == PENDIENTE


# --- Influenza Pediátrica ---

def test_influenza_ped_no_aplica_aun_menor_6m():
    result = get_vaccine_status("INFLUENZA PEDIATRICA", [], 100)
    assert result[0]["status"] == NO_APLICA_AUN


def test_influenza_ped_2_dosis_entre_6m_y_12m():
    result = get_vaccine_status("INFLUENZA PEDIATRICA", [], 200)
    assert len(result) == 2
    assert result[0]["status"] == PENDIENTE
    assert result[1]["status"] == PENDIENTE


def test_influenza_ped_no_corresponde_mayor_3a():
    result = get_vaccine_status("INFLUENZA PEDIATRICA", [], 1200)
    assert result[0]["status"] == NO_CORRESPONDE


# --- Influenza Adulto ---

def test_influenza_adulto_no_corresponde_menor_3a():
    result = get_vaccine_status("INFLUENZA ADULTO", [], 500)
    assert result[0]["status"] == NO_CORRESPONDE


def test_influenza_adulto_aplica_mayor_3a():
    result = get_vaccine_status("INFLUENZA ADULTO", [], 1200)
    assert len(result) == 1
    # status is PENDIENTE or APLICADA depending on current year doses
    assert result[0]["status"] in (PENDIENTE, APLICADA)
