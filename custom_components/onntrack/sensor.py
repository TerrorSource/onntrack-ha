"""Sensoren voor Onntrack integratie."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, CONF_IMEI
from .coordinator import OnntrackCoordinator


@dataclass
class OnntrackSensorDescription(SensorEntityDescription):
    """Beschrijving van een Onntrack sensor."""
    data_key: str = ""


SENSOR_DESCRIPTIONS: tuple[OnntrackSensorDescription, ...] = (
    OnntrackSensorDescription(
        key="address",
        data_key="address",
        name="Locatie Adres",
        icon="mdi:map-marker",
    ),
    OnntrackSensorDescription(
        key="status",
        data_key="status",
        name="Status",
        icon="mdi:car-info",
    ),
    OnntrackSensorDescription(
        key="speed",
        data_key="speed",
        name="Snelheid",
        icon="mdi:speedometer",
        native_unit_of_measurement="km/h",
    ),
    OnntrackSensorDescription(
        key="latitude",
        data_key="latitude",
        name="Breedtegraad",
        icon="mdi:latitude",
        native_unit_of_measurement="°",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    OnntrackSensorDescription(
        key="longitude",
        data_key="longitude",
        name="Lengtegraad",
        icon="mdi:longitude",
        native_unit_of_measurement="°",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    OnntrackSensorDescription(
        key="satellites",
        data_key="satellites",
        name="Satellieten",
        icon="mdi:satellite-variant",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    OnntrackSensorDescription(
        key="signal",
        data_key="signal",
        name="Signaalsterkte",
        icon="mdi:signal",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    OnntrackSensorDescription(
        key="last_online",
        data_key="last_online",
        name="Laatste Online",
        icon="mdi:clock-outline",
        device_class=SensorDeviceClass.TIMESTAMP,
    ),
    OnntrackSensorDescription(
        key="today_mileage",
        data_key="today_mileage",
        name="Kilometer Vandaag",
        icon="mdi:map-marker-distance",
        native_unit_of_measurement="km",
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    OnntrackSensorDescription(
        key="total_mileage",
        data_key="total_mileage",
        name="Totale Kilometerstand",
        icon="mdi:counter",
    ),
    OnntrackSensorDescription(
        key="voltage",
        data_key="voltage",
        name="Spanning",
        icon="mdi:lightning-bolt",
        native_unit_of_measurement="V",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    OnntrackSensorDescription(
        key="positioning_type",
        data_key="positioning_type",
        name="Positionering Type",
        icon="mdi:crosshairs-gps",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Stel Onntrack sensoren in."""
    coordinator: OnntrackCoordinator = hass.data[DOMAIN][entry.entry_id]
    imei = entry.data[CONF_IMEI]

    async_add_entities(
        OnntrackSensor(coordinator, description, imei, entry.entry_id)
        for description in SENSOR_DESCRIPTIONS
    )


class OnntrackSensor(CoordinatorEntity[OnntrackCoordinator], SensorEntity):
    """Een Onntrack sensor."""

    entity_description: OnntrackSensorDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: OnntrackCoordinator,
        description: OnntrackSensorDescription,
        imei: str,
        entry_id: str,
    ) -> None:
        """Initialiseer de sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._imei = imei
        self._attr_unique_id = f"{imei}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, imei)},
            name=coordinator.data.get("device_name", f"Onntrack {imei[-5:]}") if coordinator.data else f"Onntrack {imei[-5:]}",
            manufacturer="Onntrack",
            model=coordinator.data.get("positioning_type", "GPS Tracker") if coordinator.data else "GPS Tracker",
        )

    @property
    def native_value(self) -> Any:
        """Geef de huidige waarde terug."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get(self.entity_description.data_key)