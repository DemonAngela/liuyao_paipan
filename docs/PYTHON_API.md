# Python Integration API

The repository can be installed directly as a Python package for integrations that do not need to call the HTTP server.

```bash
pip install "git+https://github.com/DemonAngela/liuyao_paipan.git@v0.2.0"
```

For development from a checkout:

```bash
pip install -e .
```

## Ganzhi

```python
from backend import calculate_ganzhi

result = calculate_ganzhi(1986, 5, 29, 0, 0)
print(result)
```

`calculate_ganzhi` accepts `year, month, day, hour, minute`. The minute parameter exists so integrations and tests can reproduce exact solar-term boundary behavior.

## Paipan

```python
from backend import paipan

result = paipan(
    [1, 1, 1, 1, 1, 1],
    changing_yao=[False, False, False, False, False, False],
    year=2026,
    month=4,
    day=23,
    hour=10,
)
print(result["ben_gua_name"])
```

Line order is bottom-to-top. `yao_values` must contain six `0`/`1` values and `changing_yao` must contain six booleans. The function returns plain Python dictionaries/lists and uses the same production engine as the REST API.

## Stability

The public integration surface is intentionally small: `backend.calculate_ganzhi` and `backend.paipan`. Internal modules under `backend.core` may evolve as validation work continues. Pre-1.0 releases can still make breaking changes, but such changes should be documented in the changelog and release notes.
