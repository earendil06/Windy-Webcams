import logging
from typing import LiteralString

from homeassistant.components.image import ImageEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import (
    extract_image_full_url,
    extract_image_last_updated,
    extract_image_preview_url,
    extract_webcam_title,
    get_image_bytes,
    get_webcam_json_data,
)
from .const import CONF_IDS

_LOGGER = logging.getLogger(__name__)

class WebcamImageEntity(ImageEntity):
    def __init__(
        self, hass: HomeAssistant, api: LiteralString, webcam_id: LiteralString
    ) -> None:
        """Initialize the Webcam image sensor."""
        super().__init__(hass)
        self._attr_unique_id = webcam_id
        self.webcam_id = webcam_id
        self.api = api

    def _get_webcam_data_json(self):
        return get_webcam_json_data(self.webcam_id, self.api)

    def _get_image(self, json) -> bytes | None:
        url = extract_image_preview_url(json)
        full_url = extract_image_full_url(json)
        if url is None and full_url is None:
            return None
        full_image = get_image_bytes(full_url)
        if full_image is not None:
            return full_image
        preview_image = get_image_bytes(url)
        if preview_image is not None:
            return preview_image
        _LOGGER.warning('Image could not be downloaded %s', self.webcam_id)
        return None

    async def async_image(self) -> bytes | None:
        """Return bytes of image."""
        json = await self.hass.async_add_executor_job(self._get_webcam_data_json)
        data = await self.hass.async_add_executor_job(self._get_image, json)
        self.image_last_updated = extract_image_last_updated(json)
        self.async_write_ha_state()
        return data

    async def async_added_to_hass(self):
        """Run when the entity is added to Home Assistant."""
        json = await self.hass.async_add_executor_job(self._get_webcam_data_json)
        webcam_name = extract_webcam_title(json)

        if (webcam_name):
            self._attr_name = webcam_name


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Windy Platform from config_flow."""
    options = entry.as_dict()["options"]
    api = options[CONF_API_KEY]
    ids = [
        w_id.strip() for w_id in options[CONF_IDS].split(",")
    ]
    async_add_entities([WebcamImageEntity(hass, api, w_id) for w_id in ids])
