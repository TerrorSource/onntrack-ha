"""Onntrack GPS Tracker integratie voor Home Assistant."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .coordinator import OnntrackCoordinator

PLATFORMS = [
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
    Platform.DEVICE_TRACKER,
    Platform.SENSOR,
]

OnntrackConfigEntry = ConfigEntry[OnntrackCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: OnntrackConfigEntry) -> bool:
    """Stel de Onntrack integratie in."""
    coordinator = OnntrackCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def _async_update_listener(
    hass: HomeAssistant, entry: OnntrackConfigEntry
) -> None:
    """Herlaad de integratie als de opties wijzigen."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: OnntrackConfigEntry) -> bool:
    """Verwijder de Onntrack integratie."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        await entry.runtime_data.async_shutdown()
    return unload_ok
