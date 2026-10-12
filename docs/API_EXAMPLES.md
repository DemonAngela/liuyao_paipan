# API Examples

These examples target a local server at `http://127.0.0.1:8000`.

## Automatic six-line generation

```bash
curl -s -X POST http://127.0.0.1:8000/api/qigua/auto
```

The response contains six `yao_list` values, six `changing_yao` flags, and a timestamp.

## Specify a hexagram

```bash
curl -s -X POST http://127.0.0.1:8000/api/qigua/specify \
  -H 'Content-Type: application/json' \
  -d '{
    "method": "specify",
    "yao_values": [1, 1, 1, 1, 1, 1],
    "changing_yao": [false, false, false, false, false, false],
    "year": 2026,
    "month": 8,
    "day": 9,
    "hour": 12
  }'
```

## Paipan from a validated qigua response

```bash
curl -s -X POST http://127.0.0.1:8000/api/paipan/ \
  -H 'Content-Type: application/json' \
  -d '{
    "yao_list": [1, 1, 1, 1, 1, 1],
    "changing_yao": [false, false, false, false, false, false],
    "timestamp": {"year": 2026, "month": 8, "day": 9, "hour": 12}
  }'
```

## Python client example

```python
import requests

base = "http://127.0.0.1:8000"
qigua = requests.post(f"{base}/api/qigua/auto", timeout=10).json()
paipan = requests.post(f"{base}/api/paipan/", json=qigua, timeout=10)
paipan.raise_for_status()
print(paipan.json()["ben_gua_name"])
```

## Integration guidance

- Treat `/api/qigua/time` as experimental until issue #2 is resolved.
- Send exactly six binary yin/yang values and six changing-line flags when specifying a result.
- Use explicit timestamps when reproducibility matters.
- Preserve the raw request when reporting rule-accuracy bugs so maintainers can turn it into a regression fixture.
