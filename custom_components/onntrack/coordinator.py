"""Data update coordinator voor Onntrack."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_SCAN_INTERVAL, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .api import OnntrackApi, OnntrackAuthError, OnntrackError
from .const import CONF_IMEI, DEFAULT_SCAN_INTERVAL, DOMAIN
from .parser import OnntrackData, merge_data, parse_monitor_data

_LOGGER = logging.getLogger(__name__)


class OnntrackCoordinator(DataUpdateCoordinator[OnntrackData]):
    """Coördineert data-updates van de Onntrack API."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialiseer de coördinator vanuit een config entry."""
        scan_interval = entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )
        self.imei: str = entry.data[CONF_IMEI]
        self.api = OnntrackApi(
            async_get_clientsession(hass),
            entry.data[CONF_USERNAME],
            entry.data[CONF_PASSWORD],
        )

    @property
    def device_info(self) -> DeviceInfo:
        """Gedeelde apparaatinfo voor alle entiteiten."""
        name = f"Onntrack {self.imei[-5:]}"
        if self.data and self.data.device_name:
            name = self.data.device_name
        return DeviceInfo(
            identifiers={(DOMAIN, self.imei)},
            name=name,
            manufacturer="Onntrack",
            model="GPS Tracker",
            serial_number=self.imei,
            configuration_url="https://platform.onntrack.nl",
        )

    async def _async_update_data(self) -> OnntrackData:
        """Haal data op en vertaal API-fouten naar HA-excepties."""
        try:
            sections = await self.api.get_monitor_info(self.imei)
        except OnntrackAuthError as err:
            raise ConfigEntryAuthFailed(str(err)) from err
        except OnntrackError as err:
            raise UpdateFailed(str(err)) from err

        result = merge_data(
            self.data, parse_monitor_data(sections, dt_util.DEFAULT_TIME_ZONE)
        )

        # TIJDELIJKE DEBUG-LOGGING (issue #1: kaart updatet niet).
        # Alleen actief met logger op debug; haalt dan ook queryEquipmentList
        # op zodat we kunnen zien of dat endpoint een verse positie levert.
        if _LOGGER.isEnabledFor(logging.DEBUG):
            _LOGGER.debug("Onntrack monitor geparsed: %s", result)
            _LOGGER.debug("Onntrack ruwe monitor data: %s", sections)
            try:
                equipment = await self.api.get_equipment_list(self.imei)
                _LOGGER.debug("Onntrack queryEquipmentList: %s", equipment)
            except OnntrackError as err:
                _LOGGER.debug("Onntrack queryEquipmentList mislukt: %s", err)

        return result
