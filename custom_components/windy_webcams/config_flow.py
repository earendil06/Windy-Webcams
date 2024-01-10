"""Adds config flow for Windy Webcams integration."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    OptionsFlowWithConfigEntry,
)
from homeassistant.const import CONF_API_KEY
from homeassistant.core import callback
from homeassistant.data_entry_flow import AbortFlow, FlowResult
from homeassistant.helpers.selector import TextSelector

from .const import CONF_IDS, DEFAULT_CONF_API_KEY, DEFAULT_CONF_IDS, DOMAIN

DATA_SCHEMA_SETUP = vol.Schema(
    {
        vol.Required(CONF_API_KEY, default=DEFAULT_CONF_API_KEY): TextSelector(),
        vol.Required(CONF_IDS, default=DEFAULT_CONF_IDS): TextSelector(),
    }
)


class WorkdayConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Windy Webcams integration."""

    VERSION = 1

    data: dict[str, Any] = {}

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> WindyWebcamsOptionsFlowHandler:
        """Get the options flow for this handler."""
        return WindyWebcamsOptionsFlowHandler(config_entry)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the user initial step."""
        return self.async_show_form(
            step_id="options",
            data_schema=DATA_SCHEMA_SETUP,
            errors={},
        )

    async def async_step_options(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle remaining flow."""
        errors: dict[str, str] = {}
        if user_input is not None:
            combined_input: dict[str, Any] = {**self.data, **user_input}

            abort_match = {
                CONF_IDS: combined_input[CONF_IDS],
            }
            self._async_abort_entries_match(abort_match)
            if not errors:
                return self.async_create_entry(
                    title="Windy Webcams",
                    data={},
                    options=combined_input,
                )

        return self.async_show_form(
            step_id="options",
            data_schema=DATA_SCHEMA_SETUP,
            errors=errors,
            description_placeholders={
                CONF_API_KEY: self.data[CONF_API_KEY],
            },
        )


class WindyWebcamsOptionsFlowHandler(OptionsFlowWithConfigEntry):
    """Handle Windy Webcams options."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage Windy Webcams options."""
        errors: dict[str, str] = {}

        if user_input is not None:
            combined_input: dict[str, Any] = {**self.options, **user_input}

            try:
                self._async_abort_entries_match(
                    {
                        CONF_IDS: combined_input[CONF_IDS],
                    }
                )
            except AbortFlow as err:
                errors = {"base": err.reason}
            else:
                return self.async_create_entry(data=combined_input)

        new_schema = self.add_suggested_values_to_schema(
            DATA_SCHEMA_SETUP, user_input or self.options
        )
        return self.async_show_form(
            step_id="init",
            data_schema=new_schema,
            errors=errors,
            description_placeholders={
                CONF_API_KEY: self.options[CONF_API_KEY],
            },
        )
