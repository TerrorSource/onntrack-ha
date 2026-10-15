"""Pure parsing van de Onntrack API-respons.

Bewust zonder Home Assistant-imports gehouden, zodat de parser los met
pytest te testen is (zie tests/test_parser.py).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, fields
from datetime import datetime, tzinfo
from typing import Any

# Vangt "113.65", "113,65" en "-4" op in waarden als "113.65km" of "4 km/h"
_NUMBER_RE = re.compile(r"-?\d+(?:[.,]\d+)?")


def to_float(value: Any) -> float | None:
    """Haal een getal uit een API-waarde als '113.65km', '233' of 15."""
    if isinstance(value, (int, float)):
        return float(value)
    if value is None:
        return None
    match = _NUMBER_RE.search(str(value))
    if match is None:
        return None
    return float(match.group().replace(",", "."))


def to_int(value: Any) -> int | None:
    """Haal een geheel getal uit een API-waarde."""
    number = to_float(value)
    return None if number is None else int(number)


def to_datetime(value: Any, tz: tzinfo) -> datetime | None:
    """Converteer een API-tijdstring naar een timezone-aware datetime."""
    if isinstance(value, datetime):
        parsed = value
    else:
        try:
            parsed = datetime.fromisoformat(str(value))
        except (ValueError, TypeError):
            return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=tz)
    return parsed


@dataclass
class OnntrackData:
    """Geparste toestand van één Onntrack apparaat."""

    address: str | None = None
    status: str | None = None
    acc: bool | None = None
    speed: float | None = None
    latitude: float | None = None
    longitude: float | None = None
    satellites: int | None = None
    signal: int | None = None
    positioning_type: str | None = None
    last_online: datetime | None = None
    positioning_time: datetime | None = None
    today_mileage: float | None = None
    total_mileage: float | None = None
    voltage: float | None = None
    device_name: str | None = None
    imei: str | None = None


# (model, key) -> (attribuut, converter)
_SIMPLE_FIELDS: dict[tuple[str, str], tuple[str, str]] = {
    ("latestPosition", "address"): ("address", "str"),
    ("gpsDevice", "lastOnlineTime"): ("last_online", "datetime"),
    ("gpsDevice", "positioningTime"): ("positioning_time", "datetime"),
    ("gpsDevice", "satellite"): ("satellites", "int"),
    ("gpsDevice", "signal"): ("signal", "int"),
    ("gpsDevice", "positioningType"): ("positioning_type", "str"),
    ("header", "mcTypeAlias"): ("device_name", "str"),
    ("header", "imei"): ("imei", "str"),
    ("vehicle", "mileage"): ("total_mileage", "float"),
}

# (model, key, sub-key) -> (attribuut, converter)
_NESTED_FIELDS: dict[tuple[str, str, str], tuple[str, str]] = {
    ("basic", "status", "status"): ("status", "str"),
    ("basic", "status", "acc"): ("acc", "acc"),
    ("basic", "speed", "speed"): ("speed", "float"),
    ("todayActivity", "todayMileage", "value"): ("today_mileage", "float"),
    ("todayActivity", "externalVoltage", "value"): ("voltage", "float"),
    ("latestPosition", "latlng", "source_latlng"): ("_latlng", "latlng"),
}


def parse_monitor_data(sections: list | None, tz: tzinfo) -> OnntrackData:
    """Verwerk de geneste API-respons naar een OnntrackData object."""
    result = OnntrackData()
    converters = {
        "str": lambda v: None if v is None else str(v),
        "int": to_int,
        "float": to_float,
        "datetime": lambda v: to_datetime(v, tz),
        "acc": lambda v: None if v is None else str(v) == "1",
    }

    for section in sections or []:
        if not isinstance(section, dict):
            continue
        model = section.get("modeleName", "")
        for item in section.get("monitorBaseVOS") or []:
            if not isinstance(item, dict):
                continue
            key = item.get("key")
            value = item.get("value")

            simple = _SIMPLE_FIELDS.get((model, key))
            if simple is not None:
                attr, conv = simple
                setattr(result, attr, converters[conv](value))
                continue

            if not isinstance(value, list):
                continue
            for sub in value:
                if not isinstance(sub, dict):
                    continue
                nested = _NESTED_FIELDS.get((model, key, sub.get("key")))
                if nested is None:
                    continue
                attr, conv = nested
                if attr == "_latlng":
                    _set_latlng(result, sub.get("value"))
                else:
                    setattr(result, attr, converters[conv](sub.get("value")))

    return result


def _set_latlng(result: OnntrackData, raw: Any) -> None:
    """Parse 'lat,lon' string naar twee floats; alleen samen geldig."""
    parts = str(raw or "").split(",")
    if len(parts) != 2:
        return
    lat = to_float(parts[0])
    lon = to_float(parts[1])
    if lat is None or lon is None:
        return
    # 0,0 is de "geen GPS-fix" marker van veel trackers, geen echte positie
    if lat == 0.0 and lon == 0.0:
        return
    result.latitude = lat
    result.longitude = lon


def merge_data(old: OnntrackData | None, new: OnntrackData) -> OnntrackData:
    """Vul velden die deze poll ontbreken aan met de laatst bekende waarde.

    Zo springt een sensor niet op 'onbekend' als de API een sectie
    een keer weglaat.
    """
    if old is None:
        return new
    for field in fields(OnntrackData):
        if getattr(new, field.name) is None:
            setattr(new, field.name, getattr(old, field.name))
    return new
