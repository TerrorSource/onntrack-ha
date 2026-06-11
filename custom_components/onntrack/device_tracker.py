"""Device tracker voor Onntrack integratie."""
from __future__ import annotations

from homeassistant.components.device_tracker import SourceType, TrackerEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import OnntrackConfigEntry
from .const import CONF_VEHICLE_TYPE, DEFAULT_VEHICLE_TYPE, VEHICLE_ICONS
from .coordinator import OnntrackCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: OnntrackConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Stel de Onntrack device tracker in."""
    vehicle_type = entry.options.get(CONF_VEHICLE_TYPE, DEFAULT_VEHICLE_TYPE)
    async_add_entities([OnntrackDeviceTracker(entry.runtime_data, vehicle_type)])


class OnntrackDeviceTracker(CoordinatorEntity[OnntrackCoordinator], TrackerEntity):
    """Onntrack GPS device tracker."""

    _attr_has_entity_name = True
    _attr_translation_key = "location"

    def __init__(self, coordinator: OnntrackCoordinator, vehicle_type: str) -> None:
        """Initialiseer de tracker."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.imei}_tracker"
        self._attr_device_info = coordinator.device_info
        self._attr_icon = VEHICLE_ICONS.get(
            vehicle_type, VEHICLE_ICONS[DEFAULT_VEHICLE_TYPE]
        )

    @property
    def latitude(self) -> float | None:
        """Geef de breedtegraad terug."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.latitude

    @property
    def longitude(self) -> float | None:
        """Geef de lengtegraad terug."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.longitude

    @property
    def source_type(self) -> SourceType:
        """Geef het type bron terug."""
        return SourceType.GPS

    @property
    def extra_state_attributes(self) -> dict:
        """Extra attributen voor de tracker.

        Bewust beperkt tot het IMEI: alle overige waarden bestaan al als
        eigen entiteiten en zouden hier alleen de recorder-database
        dubbel vullen.
        """
        return {"imei": self.coordinator.imei}
