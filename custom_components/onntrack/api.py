"""API-client voor het Onntrack platform."""
from __future__ import annotations

import asyncio
import hashlib
import logging

import aiohttp

from .const import (
    API_LOGIN,
    API_MONITOR,
    CODE_ALT_SUCCESS,
    CODE_SUCCESS,
    CODE_TOKEN_INVALID,
    CODE_TOKEN_MISSING,
)

_LOGGER = logging.getLogger(__name__)

REQUEST_TIMEOUT = 10


class OnntrackError(Exception):
    """Algemene Onntrack API-fout."""


class OnntrackAuthError(OnntrackError):
    """Authenticatie geweigerd door de Onntrack API."""


class OnntrackApi:
    """Dunne client rond de Onntrack HTTP API."""

    def __init__(
        self, session: aiohttp.ClientSession, username: str, password: str
    ) -> None:
        """Initialiseer de client met een gedeelde aiohttp-sessie."""
        self._session = session
        self._username = username
        self._password_md5 = hashlib.md5(password.encode()).hexdigest()
        self._token: str | None = None

    async def _post(self, url: str, body: dict, authorized: bool = True) -> dict:
        """Voer een POST uit en geef de JSON-respons terug."""
        headers = {"Content-Type": "application/json"}
        if authorized and self._token:
            headers["Authorization"] = self._token
        try:
            async with asyncio.timeout(REQUEST_TIMEOUT):
                resp = await self._session.post(url, json=body, headers=headers)
                status = resp.status
                data = await resp.json(content_type=None)
        except (aiohttp.ClientError, TimeoutError) as err:
            raise OnntrackError(f"Verbindingsfout: {err}") from err
        except ValueError as err:
            # Geen geldige JSON, bv. een HTML-storingspagina
            raise OnntrackError(f"Ongeldige API-respons (HTTP {resp.status})") from err
        if status >= 400:
            raise OnntrackError(f"HTTP-fout {status} van de Onntrack API")
        if not isinstance(data, dict):
            raise OnntrackError(f"Onverwachte API-respons: {data!r}")
        return data

    async def login(self) -> None:
        """Log in en bewaar het sessietoken."""
        data = await self._post(
            API_LOGIN,
            {
                "account": self._username,
                "password": self._password_md5,
                "language": "en",
                "validCode": "",
                "nodeId": "",
            },
            authorized=False,
        )
        code = data.get("code")
        if code not in (CODE_SUCCESS, CODE_ALT_SUCCESS):
            raise OnntrackAuthError(
                f"Inloggen mislukt (code {code}): {data.get('msg')}"
            )

        # Het token zit in data.token, maar sommige API-versies geven
        # het token direct als string terug in het data-veld.
        raw = data.get("data")
        if isinstance(raw, dict):
            token = raw.get("token")
        elif isinstance(raw, str) and len(raw) > 20:
            token = raw
        else:
            token = None

        if not token:
            raise OnntrackAuthError("Geen token ontvangen na inloggen")
        self._token = token
        _LOGGER.debug("Onntrack token vernieuwd")

    async def get_monitor_info(self, imei: str) -> list:
        """Haal monitordata op; logt opnieuw in bij verlopen token."""
        if self._token is None:
            await self.login()

        data = await self._post(API_MONITOR, {"imei": imei})
        if data.get("code") in (CODE_TOKEN_MISSING, CODE_TOKEN_INVALID):
            _LOGGER.info("Onntrack token verlopen, opnieuw inloggen...")
            await self.login()
            data = await self._post(API_MONITOR, {"imei": imei})

        code = data.get("code")
        if code not in (CODE_SUCCESS, CODE_ALT_SUCCESS):
            raise OnntrackError(f"API-fout (code {code}): {data.get('msg')}")
        return data.get("data") or []

