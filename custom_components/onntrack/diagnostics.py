"""Diagnostics voor Onntrack integratie."""
from __future__ import annotations

from dataclasses import asdict
from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant

from . import OnntrackConfigEntry
from .const import CONF_IMEI

TO_REDACT = [
    CONF_PASSWORD,
    CONF_USERNAME,
    CONF_IMEI,
    "latitude",
    "longitude",
    "address",
]


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: OnntrackConfigEntry
) -> dict[str, Any]:
    """Geef diagnostische informatie voor een config entry."""
    coordinator = entry.runtime_data
    return {
        "entry_data": async_redact_data(dict(entry.data), TO_REDACT),
        "options": dict(entry.options),
        "last_update_success": coordinator.last_update_success,
        "data": async_redact_data(
            asdict(coordinator.data) if coordinator.data else {}, TO_REDACT
        ),
    }
