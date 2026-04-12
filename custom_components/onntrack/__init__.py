"""Onntrack GPS Tracker integratie voor Home Assistant."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD, Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN, CONF_IMEI
from .coordinator import OnntrackCoordinator

PLATFORMS = [Platform.SENSOR, Platform.DEVICE_TRACKER]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Stel de Onntrack integratie in."""
    coordinator = OnntrackCoordinator(
        hass,
        username=entry.data[CONF_USERNAME],
        password=entry.data[CONF_PASSWORD],
        imei=entry.data[CONF_IMEI],
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Verwijder de Onntrack integratie."""
    coordinator: OnntrackCoordinator = hass.data[DOMAIN][entry.entry_id]
    await coordinator.async_shutdown()

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok