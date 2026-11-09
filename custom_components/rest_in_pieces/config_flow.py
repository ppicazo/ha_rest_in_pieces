"""Config and options flow for Rest In Pieces."""

from __future__ import annotations

import secrets
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import CONF_ENTITIES, CONF_NAME, CONF_TOKEN, DOMAIN
from .http import endpoint_path, endpoint_url

ENTITY_SELECTOR = selector.EntitySelector(
    selector.EntitySelectorConfig(multiple=True)
)


def _user_schema(defaults: dict[str, Any] | None = None) -> vol.Schema:
    suggested = defaults or {}
    return vol.Schema(
        {
            vol.Required(CONF_NAME, default=suggested.get(CONF_NAME, "")): str,
            vol.Required(
                CONF_ENTITIES, default=suggested.get(CONF_ENTITIES, [])
            ): ENTITY_SELECTOR,
        }
    )


class RestInPiecesConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Rest In Pieces."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> Any:
        """Create a new endpoint (one config entry per endpoint)."""

        errors: dict[str, str] = {}
        if user_input is not None:
            name = user_input[CONF_NAME].strip()
            entities = list(user_input[CONF_ENTITIES])
            if not name:
                errors[CONF_NAME] = "name_required"
            elif not entities:
                errors[CONF_ENTITIES] = "entities_required"
            else:
                token = secrets.token_urlsafe(24)
                await self.async_set_unique_id(token)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=name,
                    data={
                        CONF_NAME: name,
                        CONF_TOKEN: token,
                        CONF_ENTITIES: entities,
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=_user_schema(user_input),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        """Return the options flow handler."""

        return RestInPiecesOptionsFlow()


class RestInPiecesOptionsFlow(OptionsFlow):
    """Edit name and entities; token stays put."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> Any:
        """Manage endpoint contents and show the public URL."""

        errors: dict[str, str] = {}
        entry = self.config_entry
        data = entry.data
        token = data[CONF_TOKEN]
        path = endpoint_path(token)
        url = endpoint_url(self.hass, token)

        if user_input is not None:
            name = user_input[CONF_NAME].strip()
            entities = list(user_input[CONF_ENTITIES])
            if not name:
                errors[CONF_NAME] = "name_required"
            elif not entities:
                errors[CONF_ENTITIES] = "entities_required"
            else:
                self.hass.config_entries.async_update_entry(
                    entry,
                    title=name,
                    data={
                        CONF_NAME: name,
                        CONF_TOKEN: token,
                        CONF_ENTITIES: entities,
                    },
                )
                return self.async_create_entry(title="", data={})

        defaults = {
            CONF_NAME: data.get(CONF_NAME, ""),
            CONF_ENTITIES: list(data.get(CONF_ENTITIES, [])),
        }
        return self.async_show_form(
            step_id="init",
            data_schema=_user_schema(defaults),
            errors=errors,
            description_placeholders={"path": path, "url": url},
        )
