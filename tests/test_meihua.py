import datetime as dt

import pytest

from backend.core.meihua import qigua_by_datetime, qigua_from_numbers


def test_original_text_numeric_example():
    yao_list, changing = qigua_from_numbers(5, 12, 17, 9)

    assert yao_list == [1, 0, 1, 1, 1, 0]
    assert changing == [True, False, False, False, False, False]


def test_lunar_new_year_datetime_conversion():
    yao_list, changing = qigua_by_datetime(dt.datetime(2024, 2, 10, 0, 0, 0))

    assert yao_list == [0, 0, 0, 0, 0, 1]
    assert changing == [False, True, False, False, False, False]


@pytest.mark.parametrize(
    "values",
    [
        (0, 1, 1, 1),
        (1, -1, 1, 1),
        (1, 1.5, 1, 1),
    ],
)
def test_numeric_inputs_must_be_positive_integers(values):
    with pytest.raises(ValueError, match="正整数"):
        qigua_from_numbers(*values)

