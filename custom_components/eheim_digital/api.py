"""EHEIM API Client."""
from __future__ import annotations
import aiohttp
import websockets
import json

from .const import LOGGER

class IntegrationEheimDigitalApiClientError(Exception):
    """Exception to indicate a general API error."""


class IntegrationEheimDigitalApiClientCommunicationError(
    IntegrationEheimDigitalApiClientError
):
    """Exception to indicate a communication error."""


class IntegrationEheimDigitalApiClientAuthenticationError(
    IntegrationEheimDigitalApiClientError
):
    """Exception to indicate an authentication error."""


class IntegrationEheimDigitalApiClient:
    """EHEIM API Client."""

    def __init__(self, host: str, session: aiohttp.ClientSession) -> None:
        """EHEIM API Client."""
        self._host = host
        self._session = session
        self._url = f"ws://{host}/ws"
        self._websocket = None

    async def connect(self):
        """Connect to the WebSocket server."""
        try:
            # pylint: disable=no-member
            self._websocket = await websockets.connect(self._url)
        except ConnectionError as exception:
            LOGGER.error("Error: %s", exception)
            raise IntegrationEheimDigitalApiClientCommunicationError("Unable to connect") from exception

    async def async_get_data(self) -> any:
        """Get data from the API."""
        if self._websocket is None:
            await self.connect()

        await self._websocket.send('{"title": "GET_MESH_NETWORK","to": "MASTER","from": "USER"}')
        response = await self._websocket.recv()
        data = json.loads(response)

        # log each dictionary in the data list
        for item in data:
            LOGGER.info("Received API data: %s", item)

        return data


    async def async_set_title(self, title: str) -> None:
        """Set the title in the API."""
        if self._websocket is None:
            await self.connect()

        await self._websocket.send(f'{{"title": "{title}","to": "MASTER","from": "USER"}}')