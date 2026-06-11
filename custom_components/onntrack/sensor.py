"""Sensoren voor Onntrack integratie."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import OnntrackConfigEntry
from .coordinator import OnntrackCoordinator
from .parser import OnntrackData


@dataclass(frozen=True, kw_only=True)
class OnntrackSensorDescription(SensorEntityDescription):
    """Beschrijving van een Onntrack sensor."""

    value_fn: Callable[[OnntrackData], Any]


SENSOR_DESCRIPTIONS: tuple[OnntrackSensorDescription, ...] = (
    OnntrackSensorDescription(
        key="address",
        translation_key="address",
        icon="mdi:map-marker",
        value_fn=lambda data: data.address,
    ),
    OnntrackSensorDescription(
        key="status",
        translation_key="status",
        icon="mdi:car-info",
        device_class=SensorDeviceClass.ENUM,
        options=["STATIC", "MOVE", "OFFLINE"],
        value_fn=lambda data: data.status,
    ),
    OnntrackSensorDescription(
        key="speed",
        translation_key="speed",
        icon="mdi:speedometer",
        native_unit_of_measurement="km/h",
        device_class=SensorDeviceClass.SPEED,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        value_fn=lambda data: data.speed,
    ),
    OnntrackSensorDescription(
        key="latitude",
        translation_key="latitude",
        icon="mdi:latitude",
        native_unit_of_measurement="°",
        suggested_display_precision=6,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.latitude,
    ),
    OnntrackSensorDescription(
        key="longitude",
        translation_key="longitude",
        icon="mdi:longitude",
        native_unit_of_measurement="°",
        suggested_display_precision=6,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.longitude,
    ),
    OnntrackSensorDescription(
        key="satellites",
        translation_key="satellites",
        icon="mdi:satellite-variant",
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.satellites,
    ),
    OnntrackSensorDescription(
        key="signal",
        translation_key="signal",
        icon="mdi:signal",
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.signal,
    ),
    OnntrackSensorDescription(
        key="last_online",
        translation_key="last_online",
        icon="mdi:clock-outline",
        device_class=SensorDeviceClass.TIMESTAMP,
        value_fn=lambda data: data.last_online,
    ),
    OnntrackSensorDescription(
        key="positioning_time",
        translation_key="positioning_time",
        icon="mdi:crosshairs-gps",
        device_class=SensorDeviceClass.TIMESTAMP,
        value_fn=lambda data: data.positioning_time,
    ),
    OnntrackSensorDescription(
        key="today_mileage",
        translation_key="today_mileage",
        icon="mdi:map-marker-distance",
        native_unit_of_measurement="km",
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: data.today_mileage,
    ),
    OnntrackSensorDescription(
        key="total_mileage",
        translation_key="total_mileage",
        icon="mdi:counter",
        native_unit_of_measurement="km",
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: data.total_mileage,
    ),
    OnntrackSensorDescription(
        key="voltage",
        translation_key="voltage",
        icon="mdi:lightning-bolt",
        native_unit_of_measurement="V",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.voltage,
    ),
    OnntrackSensorDescription(
        key="positioning_type",
        translation_key="positioning_type",
        icon="mdi:crosshairs-gps",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.positioning_type,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: OnntrackConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Stel Onntrack sensoren in."""
    coordinator = entry.runtime_data

    async_add_entities(
        OnntrackSensor(coordinator, description)
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
    ) -> None:
        """Initialiseer de sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.imei}_{description.key}"
        self._attr_device_info = coordinator.device_info

    @property
    def native_value(self) -> Any:
        """Geef de huidige waarde terug."""
        data = self.coordinator.data
        if data is None:
            return None
        value = self.entity_description.value_fn(data)

        # Onbekende enum-waarden van de API dynamisch toestaan, zodat een
        # nieuwe statuswaarde de sensor niet laat crashen.
        if (
            value is not None
            and self.entity_description.device_class == SensorDeviceClass.ENUM
        ):
            value = str(value)
            options = list(self.options or [])
            if value not in options:
                options.append(value)
                self._attr_options = options

        return value
