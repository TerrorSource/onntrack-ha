"""Device tracker voor Onntrack integratie."""
from __future__ import annotations

from homeassistant.components.device_tracker import SourceType, TrackerEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, CONF_IMEI
from .coordinator import OnntrackCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Stel de Onntrack device tracker in."""
    coordinator: OnntrackCoordinator = hass.data[DOMAIN][entry.entry_id]
    imei = entry.data[CONF_IMEI]
    async_add_entities([OnntrackDeviceTracker(coordinator, imei, entry.entry_id)])


class OnntrackDeviceTracker(CoordinatorEntity[OnntrackCoordinator], TrackerEntity):
    """Onntrack GPS device tracker."""

    _attr_has_entity_name = True
    _attr_name = "Locatie"

    def __init__(
        self,
        coordinator: OnntrackCoordinator,
        imei: str,
        entry_id: str,
    ) -> None:
        """Initialiseer de tracker."""
        super().__init__(coordinator)
        self._imei = imei
        self._attr_unique_id = f"{imei}_tracker"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, imei)},
            name=coordinator.data.get("device_name", f"Onntrack {imei[-5:]}") if coordinator.data else f"Onntrack {imei[-5:]}",
            manufacturer="Onntrack",
            model="GPS Tracker",
        )

    @property
    def latitude(self) -> float | None:
        """Geef de breedtegraad terug."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("latitude")

    @property
    def longitude(self) -> float | None:
        """Geef de lengtegraad terug."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("longitude")

    @property
    def source_type(self) -> SourceType:
        """Geef het type bron terug."""
        return SourceType.GPS

    @property
    def icon(self) -> str:
        """Geef het icoon terug op basis van status."""
        if self.coordinator.data:
            status = self.coordinator.data.get("status", "")
            if status == "MOVE":
                return "mdi:motorbike"
            return "mdi:motorbike-off"
        return "mdi:motorbike"

    @property
    def extra_state_attributes(self) -> dict:
        """Extra attributen voor de tracker."""
        if self.coordinator.data is None:
            return {}
        data = self.coordinator.data
        return {
            "imei": self._imei,
            "address": data.get("address"),
            "status": data.get("status"),
            "speed": data.get("speed"),
            "satellites": data.get("satellites"),
            "signal": data.get("signal"),
            "last_online": data.get("last_online"),
            "acc": data.get("acc"),
            "voltage": data.get("voltage"),
        }