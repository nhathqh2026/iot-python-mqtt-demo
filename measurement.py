"""Small helpers to create and read the JSON light measurements."""

import json
from datetime import datetime


def create_measurement(area: int, lux: int) -> dict:
    """Generate one sensor measurement with a local, second-resolution timestamp."""
    if type(area) is not int or area < 1:
        raise ValueError("area must be a positive integer")
    if type(lux) is not int or lux < 0:
        raise ValueError("lux must be a non-negative integer")

    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "area": area,
        "lux": lux,
    }


def encode_measurement(measurement: dict) -> str:
    """Encode a Python dictionary as a compact JSON string."""
    return json.dumps(measurement, ensure_ascii=False, separators=(",", ":"))


def decode_measurement(payload: bytes) -> dict:
    """Decode a JSON payload and check the three expected fields."""
    data = json.loads(payload.decode("utf-8"))
    if not isinstance(data, dict):
        raise ValueError("expected a JSON object")

    timestamp = data.get("timestamp")
    area = data.get("area")
    lux = data.get("lux")
    if not isinstance(timestamp, str):
        raise ValueError("timestamp must be a string")
    datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
    if type(area) is not int or area < 1:
        raise ValueError("area must be a positive integer")
    if type(lux) is not int or lux < 0:
        raise ValueError("lux must be a non-negative integer")
    return {"timestamp": timestamp, "area": area, "lux": lux}
