"""EHEIM API Client."""
from __future__ import annotations
import json
import aiohttp
import websockets

from .const import LOGGER

class EheimDigitalApiClientError(Exception):
    """Exception to indicate a general API error."""


class EheimDigitalApiClientCommunicationError(
    EheimDigitalApiClientError
):
    """Exception to indicate a communication error."""


class EheimDigitalApiClientAuthenticationError(
    EheimDigitalApiClientError
):
    """Exception to indicate an authentication error."""


class EheimDigitalApiClient:
    """EHEIM API Client."""

    def __init__(self, host: str, session: aiohttp.ClientSession) -> None:
        """EHEIM API Client."""
        self._host = host
        self._session = session
        self._url = f"ws://{host}/ws"
        self._websocket = None
        self._devices = None
        self._clientList = None

    async def connect_websocket(self):
        """Connect to the WebSocket server."""
        LOGGER.debug('called function connect_websocket')
        try:
            self._websocket = await websockets.connect(self._url)

        except websockets.exceptions.ConnectionClosed as exception:
            LOGGER.error("Websocket connection closed: %s", exception)
            self.connect_websocket()

    async def async_get_data(self) -> any:
        """Get data from the API."""
        LOGGER.debug('called function async_get_data')
        if self._websocket is None:
            await self.connect_websocket()


        LOGGER.debug('client list: %s', self._clientList)

        await self._websocket.send('{"title": "GET_MESH_NETWORK","to": "MASTER","from": "USER"}')
        response = await self._websocket.recv()
        data = json.loads(response)

        for item in data:
            LOGGER.info("Received API data: %s", item)

        if self._devices is None:
            await self.async_get_available_devices()

        return data

    async def async_get_client_list(self):
        """Get mac addres of all devices"""
        LOGGER.debug('called function async_get_client_list')
        if self._websocket is None:
            await self.connect_websocket()

        await self._websocket.send('{"title": "GET_MESH_NETWORK","to": "MASTER","from": "USER"}')
        response = await self._websocket.recv()
        data = json.loads(response)

        for item in data:
            if item["title"] == "MESH_NETWORK":
                client_list = item["clientList"]
                client_list_unique = []

                for client in client_list:
                    if client not in client_list_unique:
                        client_list_unique.append(client)

        self._clientList = client_list_unique

    async def async_get_available_devices(self) -> any:
        """Get all devices inclunding the devices connected to master"""
        LOGGER.debug('called function async_get_available_devices')
        if self._websocket is None:
            await self.connect_websocket()




    async def async_set_title(self, title: str) -> None:
        """Set the title in the API."""
        if self._websocket is None:
            await self.connect_websocket()

        await self._websocket.send(f'{{"title": "{title}","to": "MASTER","from": "USER"}}')

