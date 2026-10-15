"""Config flow voor Onntrack integratie."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry, ConfigFlowResult
from homeassistant.const import CONF_PASSWORD, CONF_SCAN_INTERVAL, CONF_USERNAME
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    SelectSelector,
    SelectSelectorConfig,
)

from .api import OnntrackApi, OnntrackAuthError, OnntrackError
from .const import (
    CONF_IMEI,
    CONF_VEHICLE_TYPE,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_VEHICLE_TYPE,
    DOMAIN,
    VEHICLE_TYPES,
)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
        vol.Required(CONF_IMEI): str,
    }
)

STEP_REAUTH_DATA_SCHEMA = vol.Schema({vol.Required(CONF_PASSWORD): str})


class OnntrackConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Verwerk een config flow voor Onntrack."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> OnntrackOptionsFlow:
        """Geef de options flow terug."""
        return OnntrackOptionsFlow()

    async def _async_validate_login(self, username: str, password: str) -> str | None:
        """Probeer in te loggen; geeft een error-key terug of None bij succes."""
        api = OnntrackApi(async_get_clientsession(self.hass), username, password)
        try:
            await api.login()
        except OnntrackAuthError:
            return "invalid_auth"
        except OnntrackError:
            return "cannot_connect"
        except Exception:  # noqa: BLE001
            return "cannot_connect"
        return None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Verwerk de eerste stap."""
        errors: dict[str, str] = {}

        if user_input is not None:
            username = user_input[CONF_USERNAME].strip()
            password = user_input[CONF_PASSWORD]
            imei = user_input[CONF_IMEI].strip()

            await self.async_set_unique_id(imei)
            self._abort_if_unique_id_configured()

            error = await self._async_validate_login(username, password)
            if error:
                errors["base"] = error
            else:
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

    async def async_step_reauth(
        self, entry_data: dict[str, Any]
    ) -> ConfigFlowResult:
        """Start herauthenticatie bij verlopen of gewijzigde inloggegevens."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Vraag het nieuwe wachtwoord en werk de bestaande entry bij."""
        errors: dict[str, str] = {}
        entry = self._get_reauth_entry()

        if user_input is not None:
            password = user_input[CONF_PASSWORD]
            error = await self._async_validate_login(
                entry.data[CONF_USERNAME], password
            )
            if error:
                errors["base"] = error
            else:
                return self.async_update_reload_and_abort(
                    entry, data_updates={CONF_PASSWORD: password}
                )

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=STEP_REAUTH_DATA_SCHEMA,
            description_placeholders={"username": entry.data[CONF_USERNAME]},
            errors=errors,
        )


class OnntrackOptionsFlow(config_entries.OptionsFlow):
    """Opties voor een bestaande Onntrack entry."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Toon en verwerk het optieformulier."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options = self.config_entry.options
        schema = vol.Schema(
            {
                vol.Required(
                    CONF_SCAN_INTERVAL,
                    default=options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
                ): NumberSelector(
                    NumberSelectorConfig(
                        min=30,
                        max=600,
                        step=10,
                        unit_of_measurement="s",
                        mode=NumberSelectorMode.BOX,
                    )
                ),
                vol.Required(
                    CONF_VEHICLE_TYPE,
                    default=options.get(CONF_VEHICLE_TYPE, DEFAULT_VEHICLE_TYPE),
                ): SelectSelector(
                    SelectSelectorConfig(
                        options=VEHICLE_TYPES,
                        translation_key="vehicle_type",
                    )
                ),
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
