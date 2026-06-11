"""Tests voor de pure Onntrack parser (geen Home Assistant nodig).

Draaien met:  pytest tests/  -of-  python3 tests/test_parser.py
"""
from __future__ import annotations

import importlib.util
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

_PARSER_PATH = (
    Path(__file__).resolve().parent.parent
    / "custom_components"
    / "onntrack"
    / "parser.py"
)
_spec = importlib.util.spec_from_file_location("onntrack_parser", _PARSER_PATH)
parser = importlib.util.module_from_spec(_spec)
sys.modules["onntrack_parser"] = parser
_spec.loader.exec_module(parser)

TZ = timezone(timedelta(hours=2))

SECTIONS = [
    {
        "modeleName": "header",
        "monitorBaseVOS": [
            {"key": "mcTypeAlias", "value": "Onntrack 400 inbouw"},
            {"key": "imei", "value": "123456789082798"},
        ],
    },
    {
        "modeleName": "latestPosition",
        "monitorBaseVOS": [
            {"key": "address", "value": "Kasteelstraat 6, Gruitrode"},
            {
                "key": "latlng",
                "value": [{"key": "source_latlng", "value": "51.093409,5.597642"}],
            },
        ],
    },
    {
        "modeleName": "gpsDevice",
        "monitorBaseVOS": [
            {"key": "lastOnlineTime", "value": "2026-05-18 23:01:45"},
            {"key": "positioningTime", "value": "2026-05-18 23:00:12"},
            {"key": "satellite", "value": "15"},
            {"key": "signal", "value": "4"},
            {"key": "positioningType", "value": "GPS"},
        ],
    },
    {
        "modeleName": "basic",
        "monitorBaseVOS": [
            {
                "key": "status",
                "value": [
                    {"key": "status", "value": "STATIC"},
                    {"key": "acc", "value": "0"},
                ],
            },
            {"key": "speed", "value": [{"key": "speed", "value": "233"}]},
        ],
    },
    {
        "modeleName": "todayActivity",
        "monitorBaseVOS": [
            {"key": "todayMileage", "value": [{"key": "value", "value": "12.4km"}]},
            {"key": "externalVoltage", "value": [{"key": "value", "value": "12.6V"}]},
        ],
    },
    {
        "modeleName": "vehicle",
        "monitorBaseVOS": [{"key": "mileage", "value": "113.65km"}],
    },
]


def test_parse_full_response():
    data = parser.parse_monitor_data(SECTIONS, TZ)
    assert data.device_name == "Onntrack 400 inbouw"
    assert data.imei == "123456789082798"
    assert data.address == "Kasteelstraat 6, Gruitrode"
    assert data.latitude == 51.093409
    assert data.longitude == 5.597642
    assert data.satellites == 15
    assert data.signal == 4
    assert data.positioning_type == "GPS"
    assert data.status == "STATIC"
    assert data.acc is False
    assert data.speed == 233.0
    assert data.today_mileage == 12.4
    assert data.voltage == 12.6
    assert data.total_mileage == 113.65


def test_timestamps_are_timezone_aware():
    data = parser.parse_monitor_data(SECTIONS, TZ)
    assert data.last_online == datetime(2026, 5, 18, 23, 1, 45, tzinfo=TZ)
    assert data.positioning_time == datetime(2026, 5, 18, 23, 0, 12, tzinfo=TZ)


def test_unit_stripping_and_decimal_comma():
    assert parser.to_float("113.65km") == 113.65
    assert parser.to_float("113,65km") == 113.65
    assert parser.to_float("233") == 233.0
    assert parser.to_float(15) == 15.0
    assert parser.to_float("geen getal") is None
    assert parser.to_float(None) is None
    assert parser.to_int("15 sats") == 15


def test_malformed_response_does_not_crash():
    rommel = [
        None,
        "tekst",
        {"geen": "model"},
        {"modeleName": "basic", "monitorBaseVOS": [{"zonder": "key"}, "rommel", None]},
        {"modeleName": "latestPosition", "monitorBaseVOS": [
            {"key": "latlng", "value": [{"key": "source_latlng", "value": "kapot"}]},
        ]},
    ]
    data = parser.parse_monitor_data(rommel, TZ)
    assert data.latitude is None
    assert data.longitude is None
    assert data.status is None


def test_acc_true():
    sections = [
        {"modeleName": "basic", "monitorBaseVOS": [
            {"key": "status", "value": [{"key": "acc", "value": "1"}]},
        ]},
    ]
    assert parser.parse_monitor_data(sections, TZ).acc is True


def test_merge_keeps_last_known_values():
    old = parser.parse_monitor_data(SECTIONS, TZ)
    nieuw = parser.OnntrackData(speed=0.0)  # API gaf alleen snelheid terug
    merged = parser.merge_data(old, nieuw)
    assert merged.speed == 0.0  # nieuwe waarde wint
    assert merged.latitude == 51.093409  # ontbrekend veld: laatst bekende blijft
    assert merged.address == "Kasteelstraat 6, Gruitrode"


def test_merge_without_old_data():
    nieuw = parser.OnntrackData(speed=10.0)
    assert parser.merge_data(None, nieuw) is nieuw


if __name__ == "__main__":
    fouten = 0
    for naam, fn in sorted(globals().items()):
        if naam.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"OK   {naam}")
            except AssertionError as err:
                fouten += 1
                print(f"FAIL {naam}: {err}")
    raise SystemExit(fouten)
