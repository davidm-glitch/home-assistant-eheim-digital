"""Adds config flow for eheim_digital."""
from __future__ import annotations
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_IP_ADDRESS
from .const import DOMAIN, LOGGER

from .websocket import (EheimDigitalWebSocketClient,EheimDigitalWebSocketClientCommunicationError)

class EheimDigitalFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for eheim_digital."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> config_entries.FlowResult:
        """Handle a flow initialized by the user."""
        LOGGER.debug("User step initiated")
        errors = {}
        if user_input is not None:
            LOGGER.debug("User input received: %s", user_input)
            try:
                await self._test_host_connection(
                    host=user_input[CONF_IP_ADDRESS]
                )
                LOGGER.debug("Connection successful, creating entry")
                return self.async_create_entry(
                    title=user_input[CONF_IP_ADDRESS],
                    data=user_input
                )
            except EheimDigitalWebSocketClientCommunicationError:
                LOGGER.warning("Communication error with host")
                errors["base"] = "communication_error"

        schema = vol.Schema(
            {
                vol.Required(CONF_IP_ADDRESS): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )

    async def _test_host_connection(self, host: str) -> None:
        """Test the connection to the given host."""
        LOGGER.debug("Testing host connection: %s", host)
        websocket_client = EheimDigitalWebSocketClient(host)
        await websocket_client.connect_websocket()
        LOGGER.debug("Connected to WebSocket, testing further if needed")
        # Perform other tests here if needed
        await websocket_client.disconnect_websocket()
        LOGGER.debug("Host connection test completed")
