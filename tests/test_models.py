import pytest
from pydantic import ValidationError

from backend.models.gua import QiguaRequest, QiguaResponse


def test_qigua_request_accepts_six_binary_yao_values():
    request = QiguaRequest(
        method="specify",
        yao_values=[1, 0, 1, 0, 1, 0],
        changing_yao=[False, True, False, False, True, False],
    )
    assert request.yao_values == [1, 0, 1, 0, 1, 0]


def test_qigua_request_rejects_wrong_yao_length():
    with pytest.raises(ValidationError):
        QiguaRequest(method="specify", yao_values=[1, 0, 1, 0, 1])


def test_qigua_request_rejects_non_binary_yao_value():
    with pytest.raises(ValidationError):
        QiguaRequest(method="specify", yao_values=[1, 0, 1, 0, 1, 2])


def test_qigua_request_requires_complete_date():
    with pytest.raises(ValidationError):
        QiguaRequest(method="time", year=2026, month=8)


def test_qigua_request_rejects_invalid_calendar_date():
    with pytest.raises(ValidationError):
        QiguaRequest(method="time", year=2026, month=2, day=30, hour=12)


def test_hour_is_optional_in_request():
    request = QiguaRequest(method="time")
    assert request.hour is None


def test_qigua_response_rejects_invalid_timestamp():
    with pytest.raises(ValidationError):
        QiguaResponse(
            yao_list=[1, 1, 1, 1, 1, 1],
            changing_yao=[False] * 6,
            timestamp={"year": 2026, "month": 13, "day": 1, "hour": 0},
        )
