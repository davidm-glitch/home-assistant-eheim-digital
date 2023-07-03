"""EHEIM API Client."""
from __future__ import annotations

import asyncio
import socket

import aiohttp
import async_timeout

import websockets


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

    def __init__(
        self,
        host: str,
        session: aiohttp.ClientSession,
    ) -> None:
        """EHEIM API Client."""
        self._host = host
        self._session = session
        self._url = f"ws://{host}/ws"
        self._websocket = self.websocket_connect()

    async def websocket_connect(self):
        try:
            websocket = websockets.sync.client.connect(self._url)
            return websocket

        except Exception as exception:
            LOGGER.error(exception)

    async def async_get_data(self) -> any:
        """Get data from the API."""
        await self._websocket.send(
            '{"title": "GET_MESH_NETWORK","to": "MASTER","from": "USER"}'
        )
        await self._websocket.send("WAAAAAAAAAH")
        return await self._websocket.recv()
