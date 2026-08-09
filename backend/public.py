"""Small, stable Python-facing API for embedding the Liuyao engine.

The web application remains the primary user interface, but maintainers and
integrators should not need to import FastAPI routes or private engine helpers.
"""

import datetime as dt
from functools import lru_cache
from typing import Any, Dict, Iterable, List, Optional

from .core.ganzhi import get_ganzhi_by_date
from .core.liuyao_engine import LiuyaoEngine


def _to_plain(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _to_plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_to_plain(item) for item in value]
    if hasattr(value, "model_dump"):
        return _to_plain(value.model_dump())
    if hasattr(value, "__dict__"):
        return {
            key: _to_plain(item)
            for key, item in vars(value).items()
            if not key.startswith("_")
        }
    return value


@lru_cache(maxsize=1)
def _engine() -> LiuyaoEngine:
    return LiuyaoEngine()


def calculate_ganzhi(
    year: int,
    month: int,
    day: int,
    hour: int = 0,
    minute: int = 0,
) -> Dict[str, Any]:
    """Return the project's deterministic Ganzhi result for a civil time."""
    return dict(get_ganzhi_by_date(year, month, day, hour, minute))


def paipan(
    yao_values: Iterable[int],
    *,
    changing_yao: Optional[Iterable[bool]] = None,
    year: int,
    month: int,
    day: int,
    hour: int = 0,
) -> Dict[str, Any]:
    """Run a deterministic six-line chart and return plain Python data.

    ``yao_values`` is bottom-to-top and must contain exactly six ``0``/``1``
    values. ``changing_yao`` uses the same order and defaults to six static
    lines. The REST API and this function share the same production engine.
    """
    values: List[int] = list(yao_values)
    changes: List[bool] = (
        [False] * 6 if changing_yao is None else list(changing_yao)
    )

    if len(values) != 6 or any(value not in (0, 1) for value in values):
        raise ValueError("yao_values must contain exactly six 0/1 values")
    if len(changes) != 6 or any(not isinstance(value, bool) for value in changes):
        raise ValueError("changing_yao must contain exactly six booleans")
    dt.datetime(year, month, day, hour)

    result = _engine().paipan(
        {
            "yao_list": values,
            "changing_yao": changes,
            "year": year,
            "month": month,
            "day": day,
            "hour": hour,
        }
    )
    return _to_plain(result)
