from typing import LiteralString

from homeassistant.components.image import ImageEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import (
    get_image_bytes,
    get_image_last_updated,
    get_image_url,
    get_webcam_json_data,
)
from .const import CONF_IDS


class WebcamImageEntity(ImageEntity):
    def __init__(
        self, hass: HomeAssistant, api: LiteralString, webcam_id: LiteralString
    ) -> None:
        """Initialize the Workday sensor."""
        super().__init__(hass)
        self._attr_unique_id = webcam_id
        self.webcam_id = webcam_id
        self.api = api

    def _get_image(self) -> bytes:
        json = get_webcam_json_data(self.webcam_id, self.api)
        url = get_image_url(json)
        data = get_image_bytes(url)
        return data

    def _get_updated(self) -> bytes:
        json = get_webcam_json_data(self.webcam_id, self.api)
        return get_image_last_updated(json)

    async def async_image(self) -> bytes | None:
        """Return bytes of image."""
        data = await self.hass.async_add_executor_job(self._get_image)
        updated = await self.hass.async_add_executor_job(self._get_updated)
        self.image_last_updated = updated
        self.async_write_ha_state()
        print("update")
        return data


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Windy Platform from config_flow."""
    api = entry.as_dict()["options"][CONF_API_KEY]
    ids = [
        w_id.strip() for w_id in entry.as_dict()["options"][CONF_IDS].split(",")
    ]
    async_add_entities([WebcamImageEntity(hass, api, w_id) for w_id in ids])
