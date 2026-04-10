import sys
import os

# Ensure project root is on path so our parser.py takes priority over stdlib parser
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date
import pytest
import parser as vac_parser
from parser import parse_doses, format_age, age_days_from_birth, get_age_group


def test_parse_doses_dosis_unica():
    result = parse_doses("DU (29/12/2024)")
    assert result == [("DU", date(2024, 12, 29))]


def test_parse_doses_multiples():
    result = parse_doses("1ra (29/05/2023), 2da (30/07/2023), 3ra (26/09/2023)")
    assert result == [
        ("1ra", date(2023, 5, 29)),
        ("2da", date(2023, 7, 30)),
        ("3ra", date(2023, 9, 26)),
    ]


def test_parse_doses_da():
    result = parse_doses("DA (27/09/2024)")
    assert result == [("DA", date(2024, 9, 27))]


def test_parse_doses_none():
    assert parse_doses(None) == []


def test_parse_doses_nan():
    assert parse_doses(float("nan")) == []


def test_parse_doses_empty():
    assert parse_doses("") == []


def test_parse_doses_multiples_du():
    result = parse_doses("DU (27/01/2023), DU (20/06/2023)")
    assert len(result) == 2
    assert result[0] == ("DU", date(2023, 1, 27))
    assert result[1] == ("DU", date(2023, 6, 20))


def test_format_age():
    assert format_age(3, 2, 15) == "3a 2m 15d"
    assert format_age(0, 6, 0) == "0a 6m 0d"


def test_age_days_from_birth():
    from datetime import timedelta
    birth = date.today() - timedelta(days=365)
    assert age_days_from_birth(birth) == 365


def test_get_age_group():
    from datetime import timedelta
    assert get_age_group(date.today() - timedelta(days=200)) == "< 1 año"
    assert get_age_group(date.today() - timedelta(days=400)) == "1 año"
    assert get_age_group(date.today() - timedelta(days=800)) == "2 años"
    assert get_age_group(date.today() - timedelta(days=1200)) == "3 años"
    assert get_age_group(date.today() - timedelta(days=1600)) == "4 años"
