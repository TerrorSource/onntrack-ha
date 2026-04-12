"""Data update coordinator voor Onntrack."""
from __future__ import annotations

import logging
from datetime import timedelta

import aiohttp
import async_timeout

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.exceptions import ConfigEntryAuthFailed

from .const import (
    DOMAIN,
    API_LOGIN,
    API_MONITOR,
    CODE_SUCCESS,
    CODE_ALT_SUCCESS,
    CODE_TOKEN_MISSING,
    CODE_TOKEN_INVALID,
    DEFAULT_SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)


class OnntrackCoordinator(DataUpdateCoordinator):
    """Coördineert data-updates van de Onntrack API."""

    def __init__(self, hass: HomeAssistant, username: str, password: str, imei: str) -> None:
        """Initialiseer de coördinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.username = username
        self.password = password
        self.imei = imei
        self._token: str | None = None
        self._session: aiohttp.ClientSession | None = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Geef een herbruikbare aiohttp sessie terug."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def async_login(self) -> str:
        """Log in bij Onntrack en retourneer een token."""
        session = await self._get_session()
        try:
            async with async_timeout.timeout(10):
                resp = await session.post(
                    API_LOGIN,
                    json={"account": self.username, "password": self.password},
                    headers={"Content-Type": "application/json"},
                )
                data = await resp.json(content_type=None)
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Verbindingsfout bij inloggen: {err}") from err

        code = data.get("code")
        if code not in (CODE_SUCCESS, CODE_ALT_SUCCESS):
            raise ConfigEntryAuthFailed(
                f"Inloggen mislukt (code {code}): {data.get('msg')}"
            )

        token = data.get("data", {}).get("token")
        if not token:
            raise ConfigEntryAuthFailed("Geen token ontvangen na inloggen")

        _LOGGER.debug("Onntrack token vernieuwd")
        return token

    async def _fetch_monitor_data(self) -> dict:
        """Haal monitordata op voor het opgegeven IMEI."""
        session = await self._get_session()
        try:
            async with async_timeout.timeout(10):
                resp = await session.post(
                    API_MONITOR,
                    json={"imei": self.imei},
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": self._token,
                    },
                )
                data = await resp.json(content_type=None)
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Verbindingsfout bij ophalen data: {err}") from err

        return data

    async def _async_update_data(self) -> dict:
        """Haal data op, vernieuw token indien nodig."""
        # Eerste keer of token verlopen: inloggen
        if self._token is None:
            self._token = await self.async_login()

        data = await self._fetch_monitor_data()
        code = data.get("code")

        # Token verlopen: opnieuw inloggen en retry
        if code in (CODE_TOKEN_MISSING, CODE_TOKEN_INVALID):
            _LOGGER.info("Onntrack token verlopen, opnieuw inloggen...")
            self._token = await self.async_login()
            data = await self._fetch_monitor_data()
            code = data.get("code")

        if code not in (CODE_SUCCESS, CODE_ALT_SUCCESS):
            raise UpdateFailed(f"API-fout (code {code}): {data.get('msg')}")

        return self._parse_monitor_data(data.get("data", []))

    def _parse_monitor_data(self, sections: list) -> dict:
        """Verwerk de geneste API-respons naar een plat dictionary."""
        result = {}

        for section in sections:
            model = section.get("modeleName", "")
            items = section.get("monitorBaseVOS", [])

            if model == "latestPosition":
                for item in items:
                    if item["key"] == "address":
                        result["address"] = item.get("value")
                    elif item["key"] == "latlng":
                        for sub in item.get("value", []):
                            if sub["key"] == "source_latlng":
                                parts = sub["value"].split(",")
                                if len(parts) == 2:
                                    result["latitude"] = float(parts[0])
                                    result["longitude"] = float(parts[1])

            elif model == "gpsDevice":
                for item in items:
                    if item["key"] == "lastOnlineTime":
                        result["last_online"] = item.get("value")
                    elif item["key"] == "positioningTime":
                        result["positioning_time"] = item.get("value")
                    elif item["key"] == "satellite":
                        result["satellites"] = item.get("value")
                    elif item["key"] == "signal":
                        result["signal"] = item.get("value")
                    elif item["key"] == "positioningType":
                        result["positioning_type"] = item.get("value")

            elif model == "basic":
                for item in items:
                    if item["key"] == "status":
                        for sub in item.get("value", []):
                            if sub["key"] == "status":
                                result["status"] = sub.get("value")
                            elif sub["key"] == "acc":
                                result["acc"] = sub.get("value") == "1"
                    elif item["key"] == "speed":
                        for sub in item.get("value", []):
                            if sub["key"] == "speed":
                                result["speed"] = sub.get("value")

            elif model == "header":
                for item in items:
                    if item["key"] == "mcTypeAlias":
                        result["device_name"] = item.get("value")
                    elif item["key"] == "imei":
                        result["imei"] = item.get("value")

            elif model == "todayActivity":
                for item in items:
                    if item["key"] == "todayMileage":
                        for sub in item.get("value", []):
                            if sub["key"] == "value":
                                result["today_mileage"] = sub.get("value")
                    elif item["key"] == "externalVoltage":
                        for sub in item.get("value", []):
                            if sub["key"] == "value":
                                result["voltage"] = sub.get("value")

            elif model == "vehicle":
                for item in items:
                    if item["key"] == "mileage":
                        result["total_mileage"] = item.get("value")

        return result

    async def async_shutdown(self) -> None:
        """Sluit de aiohttp sessie."""
        if self._session and not self._session.closed:
            await self._session.close()
        await super().async_shutdown()