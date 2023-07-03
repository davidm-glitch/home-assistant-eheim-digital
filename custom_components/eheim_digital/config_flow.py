"""Adds config flow for eheim_digital."""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_IP_ADDRESS
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_create_clientsession

from .api import (
    IntegrationEheimDigitalApiClient,
    IntegrationEheimDigitalApiClientAuthenticationError,
    IntegrationEheimDigitalApiClientCommunicationError,
    IntegrationEheimDigitalApiClientError,
)
from .const import DOMAIN, LOGGER


class EheimDigitalFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for eheim_digital."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> config_entries.FlowResult:
        """Handle a flow initialized by the user."""
        _errors = {}
        if user_input is not None:
            try:
                await self._test_host_connection(
                    host=user_input[CONF_IP_ADDRESS],
                )
            except IntegrationEheimDigitalApiClientAuthenticationError as exception:
                LOGGER.warning(exception)
                _errors["base"] = "auth"
            except IntegrationEheimDigitalApiClientCommunicationError as exception:
                LOGGER.error(exception)
                _errors["base"] = "connection"
            except IntegrationEheimDigitalApiClientError as exception:
                LOGGER.exception(exception)
                _errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title=user_input[CONF_IP_ADDRESS],
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_IP_ADDRESS,
                        default=(user_input or {}).get(CONF_IP_ADDRESS),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT
                        ),
                    )
                }
            ),
            errors=_errors,
        )

    async def _test_host_connection(self, host: str) -> None:
        """Validate host connection."""
        client = IntegrationEheimDigitalApiClient(
            host=host,
            session=async_create_clientsession(self.hass),
        )
        await client.async_get_data()
