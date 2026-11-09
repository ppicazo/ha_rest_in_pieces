# Rest In Pieces

Home Assistant integration that exposes selected entity states on secret REST URLs. Each endpoint gets a random token in the path; anyone who knows the URL can read those values — there is no separate API key.

Use one endpoint for all room temperatures, another for outdoor temp / humidity / lux, and so on.

## Install

Home Assistant 2025.1 or newer.

### HACS

1. In HACS, open **Custom repositories**.
2. Add `https://github.com/ppicazo/ha_rest_in_pieces` and set the type to **Integration**.
3. Search for **Rest In Pieces**, download, restart Home Assistant.
4. **Settings → Devices & services → Add integration → Rest In Pieces**.

### Manual

1. Copy `custom_components/rest_in_pieces` into `config/custom_components/rest_in_pieces`.
2. Restart Home Assistant.
3. Add the **Rest In Pieces** integration.

## Setup

Each config entry is one endpoint:

1. Give it a name (e.g. `Room temps`).
2. Select one or more entities.
3. Open **Configure** on the entry to copy the public URL (and to edit name / entities later).

Add the integration again to create another endpoint.

## API

```http
GET /api/rest_in_pieces/<token>
```

No Home Assistant auth. The token is the credential.

### Example response

```json
{
  "name": "Room temps",
  "entities": [
    {
      "entity_id": "sensor.living_room_temperature",
      "state": "21.4",
      "friendly_name": "Living room temperature",
      "unit_of_measurement": "°C",
      "last_changed": "2026-11-09T21:00:00+00:00",
      "last_updated": "2026-11-09T21:00:00+00:00",
      "attributes": {
        "friendly_name": "Living room temperature",
        "unit_of_measurement": "°C",
        "device_class": "temperature",
        "state_class": "measurement"
      },
      "available": true
    }
  ]
}
```

Missing entities still appear with `"available": false` and null state fields.

## Security

Treat each URL like a password. Prefer exposing only non-sensitive sensors. If a token leaks, delete the config entry and create a new endpoint.
