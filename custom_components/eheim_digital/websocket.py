"""EHEIM WebSocket Client."""
import json
import websockets
import asyncio
from typing import Dict
from .devices import EheimDevice

from .const import LOGGER, DEVICE_GROUPS, REQUEST_MESSAGES

class EheimDigitalWebSocketClientError(Exception):
    """Exception to indicate a general WebSocket error."""

class EheimDigitalWebSocketClientCommunicationError(EheimDigitalWebSocketClientError):
    """Exception to indicate a communication error."""

class EheimDigitalWebSocketClient:
    """EHEIM WebSocket Client."""

    def __init__(self, host: str) -> None:
        """EHEIM WebSocket Client initialization."""
        self._host = host
        self._url = f"ws://{host}/ws"
        self._websocket = None
        self._devices = None
        self._client_list = None

    async def connect_websocket(self) -> None:
        """Connect to the WebSocket server."""
        LOGGER.debug('WEBSOCKET: Called function connect_websocket')
        try:
            self._websocket = await websockets.connect(self._url) #pylint: disable=all
        except Exception as ex:
            raise EheimDigitalWebSocketClientCommunicationError(f"Failed to connect to WebSocket: {ex}") from ex

    async def disconnect_websocket(self) -> None:
        """Disconnect from the WebSocket server."""
        if self._websocket:
            await self._websocket.close()
            self._websocket = None

    async def fetch_client_list(self) -> list[str]:
        """Fetch client list information from the WebSocket."""
        LOGGER.debug('WEBSOCKET: Called function fetch_client_liist')
        if self._websocket is None:
            await self.connect_websocket()

        # Sending a request message to get client list information (modify as needed)
        request_message = {"title": "GET_CLIENT_LIST", "from": "USER"}
        await self._websocket.send(json.dumps(request_message))
        LOGGER.debug("WEBSOCKET: Client List Request: %s", request_message)

        # Waiting for the response
        response = await self._websocket.recv()
        messages = json.loads(response)
        LOGGER.debug("WEBSOCKET: Client List Response: %s", messages)

        # Assuming that the client list is inside each message in the list
        client_list = []
        for message in messages:
            if isinstance(message, dict) and "clientList" in message:
                client_list.extend(message["clientList"])

        self._client_list = client_list
        LOGGER.debug("Client List filtered MACs: %s", client_list)

        return client_list

    async def fetch_devices(self) -> list[EheimDevice]:
        """Fetch devices information and data from the WebSocket."""
        LOGGER.debug('WEBSOCKET: Called function fetch_devices')

        # Connect to the WebSocket if not connected
        if self._websocket is None:
            await self.connect_websocket()

        # Fetch client list if not already fetched
        if self._client_list is None:
            await self.fetch_client_list()

        # Initialize devices as an empty list
        devices = []

        # Iterate through the clients and send requests for device information
        for client in self._client_list:
            request_message = f'{{"title": "GET_USRDTA","to": "{client}","from": "USER"}}'
            LOGGER.debug("WEBSOCKET: Sending Device Client: %s Request Message: %s, ", client, request_message)
            await self._websocket.send(request_message)
            response = await self._websocket.recv()
            messages = json.loads(response)
            LOGGER.debug("WEBSOCKET: Receiving Device Client: %s Response: %s", client, messages)

            # Process the response and extract the device information
            if isinstance(messages, list):
                for message in messages:
                    if message["title"] == "USRDTA":
                        device = EheimDevice(message)
                        devices.append(device)
            elif isinstance(messages, dict) and messages["title"] == "USRDTA":
                device = EheimDevice(messages)
                devices.append(device)
            LOGGER.debug("WEBSOCKET: Device: %s", devices)

        # Log the extracted details
        for device in devices:
            LOGGER.debug("WEBSOCKET: Device Details: title=%s, from_mac=%s, name=%s, aq_name=%s, mode=%s, version=%s",
                        device.title, device.from_mac, device.name, device.aq_name, device.mode, device.version)

        self._devices = devices  # Store the devices list as an instance variable
        return devices

    async def get_device_data(self, device_type: str) -> Dict:
        """Get data for the specified device type."""
        request_messages = REQUEST_MESSAGES.get(device_type, [])
        if not request_messages:
            LOGGER.warning("No request messages found for device type: %s", device_type)
            return {}

        device_data = {}
        for message in request_messages:
            response = await self._send_message(message)
            LOGGER.debug("WEBSOCKET: Message Response: %s", response)
            if response:
                try:
                    response_dict = json.loads(response)  # Parse the response into a dictionary
                    device_data[message] = response_dict
                except json.JSONDecodeError:
                    LOGGER.warning("Failed to parse JSON response for message: %s", message)
        LOGGER.debug("WEBSOCKET: Device Data: %s", device_data)
        return device_data

#Send Request/Command to Device
    async def _send_message(self, message):
        """Send a specific message to the device."""
        LOGGER.debug("WEBSOCKET: Called function _send_message")
        LOGGER.debug("WEBSOCKET: Sending Message: %s", message)

        if self._websocket is None:
            await self.connect_websocket()

        message_str = json.dumps(message)  # Convert dictionary to JSON string
        await self._websocket.send(message_str)  # Send the JSON string
        response = await self._websocket.recv()

        LOGGER.debug("WEBSOCKET: Message Response: %s", response)

        return response
# LED Specific Functions
    async def turn_light_on(self, mac_address: str):
        """Turn the light on."""
        data = {
            "title": "CCV-SW",
            "to": mac_address,
            "currentValues": [100, 100, 100],
            "from": "USER"
        }
        await self._send_message(data)

    async def turn_light_off(self, mac_address: str):
        """Turn the light off."""
        data = {
            "title": "CCV-SW",
            "to": mac_address,
            "currentValues": [0, 0, 0],
            "from": "USER"
        }
        await self._send_message(data)

#Acclimation Specific Functions
    async def request_acclimation_settings(self, mac_address: str):
        """Request acclimation settings for the LED."""
        data = {
            "title": "REQ_ACCL",
            "to": mac_address,
            "from": "USER"
        }
        response = await self._send_message(data)
        return response

    async def set_acclimation_settings(self, mac_address: str, duration: int, intensity_reduction: int, current_accl_day: int, accl_active: bool, accl_pause: bool):
        """Set acclimation settings for the LED."""
        data = {
            "title": "SET_ACCL",
            "to": mac_address,
            "duration": duration,
            "intensityReduction": intensity_reduction,
            "currentAcclDay": current_accl_day,
            "acclActive": accl_active,
            "acclPause": accl_pause,
            "from": "USER"
        }
        response = await self._send_message(data)
        return response

#Dynamic Cycle Specific Functions
    async def request_dynamic_cycle_settings(self, mac_address: str):
        """Request dynamic cycle settings for the LED."""
        data = {
            "title": "REQ_DYCL",
            "to": mac_address,
            "from": "USER"
        }
        response = await self._send_message(data)
        return response

    async def set_dynamic_cycle_settings(self, mac_address: str, dawn_start: str, sunrise_end: str, sunset_start: str, dusk_end: str):
        """Set dynamic cycle settings for the LED."""
        data = {
            "title": "SET_DYCL",
            "to": mac_address,
            "dawnStart": dawn_start,
            "sunriseEnd": sunrise_end,
            "sunsetStart": sunset_start,
            "duskEnd": dusk_end,
            "from": "USER"
        }
        response = await self._send_message(data)
        return response

#Color Channel Specific Functions
    async def request_color_channel_values(self, mac_address: str):
        """Request color channel values for the LED."""
        data = {
            "title": "REQ_CCV",
            "to": mac_address,
            "from": "USER"
        }
        response = await self._send_message(data)
        return response

    async def set_color_channel_values(self, mac_address: str, current_values: list):
        """Set color channel values for the LED."""
        data = {
            "title": "CCV-SW",
            "to": mac_address,
            "currentValues": current_values,
            "from": "USER"
        }
        response = await self._send_message(data)
        return response

#Moon Phase Specific Functions
    async def request_moon_phase(self, mac_address: str):
        """Request moon phase settings for the LED."""
        data = {
            "title": "GET_MOON",
            "to": mac_address,
            "from": "USER"
        }
        response = await self._send_message(data)
        return response

    async def set_moon_phase(self, mac_address: str, moon_phase: int):
        """Set moon phase settings for the LED."""
        data = {
            "title": "SET_MOON",
            "to": mac_address,
            "moonPhase": moon_phase,
            "from": "USER"
        }
        response = await self._send_message(data)
        return response

#Cloud Specific Functions
    async def request_cloud_settings(self, mac_address: str):
        """Request cloud settings for the LED."""
        data = {
            "title": "GET_CLOUD",
            "to": mac_address,
            "from": "USER"
        }
        response = await self._send_message(data)
        return response

#Description Specific Functions
    async def request_description(self, mac_address: str):
        """Request description for the LED."""
        data = {
            "title": "GET_DSCRPTN",
            "to": mac_address,
            "from": "USER"
        }
        response = await self._send_message(data)
        return response