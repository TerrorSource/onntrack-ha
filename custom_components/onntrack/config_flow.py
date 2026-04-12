"""Config flow voor Onntrack integratie."""
from __future__ import annotations

import voluptuous as vol
import aiohttp

from homeassistant import config_entries
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import ConfigEntryAuthFailed

from .const import DOMAIN, CONF_IMEI
from .coordinator import OnntrackCoordinator

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME, description={"suggested_value": ""}): str,
        vol.Required(CONF_PASSWORD): str,
        vol.Required(CONF_IMEI, description={"suggested_value": ""}): str,
    }
)


class OnntrackConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Verwerk een config flow voor Onntrack."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict | None = None
    ) -> FlowResult:
        """Verwerk de eerste stap."""
        errors: dict[str, str] = {}

        if user_input is not None:
            username = user_input[CONF_USERNAME]
            password = user_input[CONF_PASSWORD]
            imei = user_input[CONF_IMEI].strip()

            try:
                coordinator = OnntrackCoordinator(
                    self.hass, username, password, imei
                )
                await coordinator.async_login()
                await coordinator.async_shutdown()
            except ConfigEntryAuthFailed:
                errors["base"] = "invalid_auth"
            except Exception:  # noqa: BLE001
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(imei)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=f"Onntrack {imei[-5:]}",
                    data={
                        CONF_USERNAME: username,
                        CONF_PASSWORD: password,
                        CONF_IMEI: imei,
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    async def async_step_reauth(self, entry_data: dict) -> FlowResult:
        """Herauth bij verlopen sessie."""
        return await self.async_step_user()
