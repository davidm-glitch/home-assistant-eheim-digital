"""Eheim Digital DataUpdateCoordinator."""
from __future__ import annotations
from datetime import timedelta
from typing import Any
from async_timeout import timeout

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, LOGGER, UPDATE_INTERVAL
from .websocket import EheimDigitalWebSocketClient


class EheimDigitalDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching EHEIM Digital data."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        websocket_client: EheimDigitalWebSocketClient,
    ) -> None:
        """Initialize."""
        self.websocket_client = websocket_client
        self.entry = entry
        update_interval = timedelta(seconds=UPDATE_INTERVAL)
        self.devices = []

        super().__init__(hass, LOGGER, name=DOMAIN, update_interval=update_interval)
        # hass.async_create_task(self._async_update_data())

    async def _async_update_data(self) -> dict[str, Any]:
        """Update data via Websocket."""
        all_device_data = {}
        LOGGER.debug("COORDINATOR: Starting data update")
        num_devices = len(self.devices)
        LOGGER.debug("COORDINATOR: Number of devices: %s", num_devices)
        try:
            LOGGER.debug("COORDINATOR: Calling WebSocket to update data in Coordinator")
            for device in self.devices:
                LOGGER.debug("COORDINATOR: Device: %s", device)
                device_data = await self.websocket_client.get_device_data(device)
                all_device_data[device.mac] = device_data
                # device_data = await self.websocket_client.get_device_data(device)
                # all_device_data[device.device_type, device.mac] = device_data
                LOGGER.debug(
                    "COORDINATOR: Device %s data in Coordinator: %s",
                    device,
                    device_data,
                )

        except Exception as error:
            raise UpdateFailed(error) from error
        LOGGER.debug(
            "COORDINATOR: Final aggregated data in Coordinator: %s", all_device_data
        )
        return all_device_data
