"""HTTP views for Rest In Pieces endpoints."""

from __future__ import annotations

from aiohttp import web
from homeassistant.components.http import HomeAssistantView
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.network import NoURLAvailableError, get_url
from homeassistant.util import dt as dt_util

from .const import (
    API_PATH_PREFIX,
    ATTR_FRIENDLY_NAME,
    ATTR_UNIT_OF_MEASUREMENT,
    CONF_ENTITIES,
    CONF_NAME,
    DOMAIN,
)


def endpoint_path(token: str) -> str:
    """Return the relative API path for a token."""

    return f"{API_PATH_PREFIX}/{token}"


def endpoint_url(hass: HomeAssistant, token: str) -> str:
    """Return an absolute URL for a token when the base URL is known."""

    path = endpoint_path(token)
    try:
        return f"{get_url(hass, prefer_external=True)}{path}"
    except NoURLAvailableError:
        return path


@callback
def async_register_http(hass: HomeAssistant) -> None:
    """Register the shared HTTP view once."""

    if hass.data.setdefault(DOMAIN, {}).get("http_registered"):
        return
    hass.http.register_view(RestInPiecesView())
    hass.data[DOMAIN]["http_registered"] = True


def _serialize_entity(hass: HomeAssistant, entity_id: str) -> dict:
    """Build the public JSON payload for one entity."""

    state = hass.states.get(entity_id)
    if state is None:
        return {
            "entity_id": entity_id,
            "state": None,
            "friendly_name": None,
            "unit_of_measurement": None,
            "last_changed": None,
            "last_updated": None,
            "attributes": {},
            "available": False,
        }

    attributes = dict(state.attributes)
    return {
        "entity_id": entity_id,
        "state": state.state,
        "friendly_name": attributes.get(ATTR_FRIENDLY_NAME),
        "unit_of_measurement": attributes.get(ATTR_UNIT_OF_MEASUREMENT),
        "last_changed": dt_util.as_utc(state.last_changed).isoformat(),
        "last_updated": dt_util.as_utc(state.last_updated).isoformat(),
        "attributes": attributes,
        "available": True,
    }


class RestInPiecesView(HomeAssistantView):
    """Serve configured entity snapshots at a secret token URL."""

    url = API_PATH_PREFIX + "/{token}"
    name = "api:rest_in_pieces"
    requires_auth = False

    async def get(self, request: web.Request, token: str) -> web.Response:
        """Return JSON for the endpoint matching token."""

        hass: HomeAssistant = request.app["hass"]
        entries = hass.data.get(DOMAIN, {}).get("endpoints", {})
        entry_data = entries.get(token)
        if entry_data is None:
            raise web.HTTPNotFound(text="Unknown endpoint")

        entities = [
            _serialize_entity(hass, entity_id)
            for entity_id in entry_data[CONF_ENTITIES]
        ]
        return self.json(
            {
                "name": entry_data[CONF_NAME],
                "entities": entities,
            }
        )
