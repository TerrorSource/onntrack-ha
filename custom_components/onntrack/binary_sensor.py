"""Binary sensors voor Onntrack integratie."""
from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
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
    """Stel de Onntrack binary sensors in."""
    async_add_entities([OnntrackIgnitionSensor(entry.runtime_data)])


class OnntrackIgnitionSensor(
    CoordinatorEntity[OnntrackCoordinator], BinarySensorEntity
):
    """Ontsteking (ACC) van het voertuig."""

    _attr_has_entity_name = True
    _attr_translation_key = "ignition"
    _attr_device_class = BinarySensorDeviceClass.POWER
    _attr_icon = "mdi:engine"

    def __init__(self, coordinator: OnntrackCoordinator) -> None:
        """Initialiseer de sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.imei}_ignition"
        self._attr_device_info = coordinator.device_info

    @property
    def is_on(self) -> bool | None:
        """Geef aan of de ontsteking aan staat."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.acc
