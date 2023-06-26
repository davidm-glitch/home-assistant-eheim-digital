from __future__ import annotations
import asyncio
import json
import logging
import aiohttp
import voluptuous as vol
import homeassistant.helpers.config_validation as cv

from .const import _LOGGER, DEFAULT_PORT, CONF_DEVICES, RESPONSE_TIMEOUT

from typing import Any, Callable, Dict, Optional
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import CONF_TYPE, CONF_HOST, CONF_MAC, CONF_PORT, CONF_NAME
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.typing import (
    ConfigType,
    DiscoveryInfoType,
    HomeAssistantType,
)


DEVICE_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_TYPE): cv.string,
        vol.Required(CONF_MAC): cv.string,
        vol.Required(CONF_NAME): cv.string,
    }
)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_DEVICES): vol.All(cv.ensure_list, [DEVICE_SCHEMA]),
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
    }
)

async def async_setup_platform(
    hass: HomeAssistantType,
    config: ConfigType,
    async_add_entities: Callable,
    discovery_info: Optional[DiscoveryInfoType] = None,
):
    """Set up the sensor platform."""
    sensors = [
        EHEIMDigitalSensor(device, config[CONF_HOST], config[CONF_PORT])
        for device in config[CONF_DEVICES]
    ]
    async_add_entities(sensors, update_before_add=True)

    return True

class EHEIMDigitalSensor(Entity):
    """Representation of an EHEIM sensor."""
    _LOGGER.debug("call EHEIMDigitalSensor class")
    def __init__(self, device, host, port):
        self._state = None
        self._available = True
        self._name = device["name"]
        self._mac = device["mac"]
        self._type = device["type"]
        self._host = host
        self._port = port
        self._websocket = None

    async def async_update(self):
        """Update the sensor data."""
        _LOGGER.debug("call async_update")
        try:
            if self._websocket is None or self._websocket.closed:
                await self._connect_websocket()
            await self._send_message(
                {
                    "title": "GET_FILTER_DATA",
                    "to": self._mac,
                    "from": "USER",
                }
            )
        except (aiohttp.ClientError, asyncio.TimeoutError) as error:
            _LOGGER.error("Error updating sensor: %s", error)

    async def _connect_websocket(self):
        """Connect to the WebSocket."""
        _LOGGER.debug("call _connect_websocket")
        url = f"ws://{self._host}:{self._port}/ws"
        self._websocket = await aiohttp.ClientSession().ws_connect(url)
        asyncio.ensure_future(self._receive_message())
        _LOGGER.debug("websocket connected")

    async def _receive_message(self):
        """Receive messages."""
        while True:
            try:
                message = await self._websocket.receive()
                if message.type == aiohttp.WSMsgType.TEXT:
                    _LOGGER.debug("call _receive_message")
                    await self._handle_message(message.data)
            except (aiohttp.ClientError, asyncio.TimeoutError) as error:
                _LOGGER.error("Error receiving message: %s", error)
                break

    async def _send_message(self, message):
        """Send a message through the WebSocket."""
        _LOGGER.debug("call _send_message: %s", message)
        if self._websocket is not None and not self._websocket.closed:
            await self._websocket.send_str(json.dumps(message))

    async def _handle_message(self, data):
        """Handle a received message."""
        #_LOGGER.debug("call _handle_message, data: %s", data)
        #_LOGGER.debug("data type: %s; length %s", type(data), len(data)) 

        json_data = json.loads(data)

        
        _LOGGER.debug("json_data length %s", len(json_data))

        if(isinstance(json_data, dict)):
            _LOGGER.debug("message is dict")
            for message in json_data:
                _LOGGER.debug("message title: %r", message['title'])
                #if(message.get('title') == "FILTER_DATA"):
                    #_LOGGER.debug("this was filter data")
                    #await self._update_sensor_entities(data)

        if(isinstance(json_data, str)):
            _LOGGER.debug("message is str")
            _LOGGER.debug("Message is a string: %s Type: %s", json_data, type(json_data))
            _LOGGER.debug("Title: %s", json_data['title'])

    async def _update_sensor_entities(self, data):
        """Update the sensor entities with received data."""
        for key, value in data.items():
            if key not in ("title", "from", "to"):
                entity = self.__class__(
                    {"name": key, "mac": self._mac, "type": self._type},
                    self._host,
                    self._port,
                )
                entity._state = value  # Set the state of the new entity
                async_add_entities([entity])


    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def available(self):
        """Return True if the sensor data is available."""
        return self._available

    @property
    def device_state_attributes(self):
        """Return the device-specific state attributes."""
        return {
            "mac": self._mac,
            "type": self._type,
        }

    async def async_added_to_hass(self):
        """Handle entity added to Home Assistant."""
        await super().async_added_to_hass()
        await self.async_update()

    async def async_will_remove_from_hass(self):
        """Handle entity removed from Home Assistant."""
        await super().async_will_remove_from_hass()
        if self._websocket is not None:
            await self._websocket.close()
