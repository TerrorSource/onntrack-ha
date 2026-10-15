"""Buttons voor Onntrack integratie."""
from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import OnntrackConfigEntry
from .coordinator import OnntrackCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: OnntrackConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Stel de Onntrack buttons in."""
    async_add_entities([OnntrackRefreshButton(entry.runtime_data)])


class OnntrackRefreshButton(CoordinatorEntity[OnntrackCoordinator], ButtonEntity):
    """Knop om direct nieuwe data op te halen."""

    _attr_has_entity_name = True
    _attr_translation_key = "refresh"

    def __init__(self, coordinator: OnntrackCoordinator) -> None:
        """Initialiseer de button."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.imei}_refresh"
        self._attr_device_info = coordinator.device_info

    async def async_press(self) -> None:
        """Vraag direct een verse update op."""
        await self.coordinator.async_request_refresh()
