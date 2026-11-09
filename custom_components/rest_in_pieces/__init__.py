"""Rest In Pieces — expose entity snapshots on secret REST URLs."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

from .const import CONF_ENTITIES, CONF_NAME, CONF_TOKEN, DOMAIN
from .http import async_register_http


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Rest In Pieces component."""

    hass.data.setdefault(DOMAIN, {"endpoints": {}, "http_registered": False})
    async_register_http(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Register one endpoint from a config entry."""

    hass.data.setdefault(DOMAIN, {"endpoints": {}, "http_registered": False})
    async_register_http(hass)
    _register_endpoint(hass, entry)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Remove an endpoint when its config entry is unloaded."""

    token = entry.data.get(CONF_TOKEN)
    if token:
        hass.data.get(DOMAIN, {}).get("endpoints", {}).pop(token, None)
    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Refresh the in-memory endpoint map after options changes."""

    _register_endpoint(hass, entry)


def _register_endpoint(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Publish this entry's token in the lookup map used by the HTTP view."""

    domain_data = hass.data.setdefault(
        DOMAIN, {"endpoints": {}, "http_registered": False}
    )
    endpoints: dict = domain_data.setdefault("endpoints", {})

    # Drop any previous token for this entry (token itself does not change,
    # but keep the map clean if data was rewritten).
    for existing_token, payload in list(endpoints.items()):
        if payload.get("entry_id") == entry.entry_id:
            endpoints.pop(existing_token, None)

    token = entry.data[CONF_TOKEN]
    endpoints[token] = {
        "entry_id": entry.entry_id,
        CONF_NAME: entry.data[CONF_NAME],
        CONF_ENTITIES: list(entry.data.get(CONF_ENTITIES, [])),
    }
