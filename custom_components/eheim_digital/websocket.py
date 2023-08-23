"""EHEIM WebSocket Client."""
import json
import websockets
import asyncio
from typing import Dict
from .devices import EheimDevice

from .const import LOGGER


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
        self._lock = asyncio.Lock()

    async def connect_websocket(self) -> None:
        """Connect to the WebSocket server and process initial messages."""
        LOGGER.debug("WEBSOCKET: Called function connect_websocket")
        try:
            self._websocket = await websockets.connect(self._url)  # pylint: disable=all

            # Process the first two initial messages
            for _ in range(2):
                initial_response = await self._websocket.recv()
                messages = json.loads(initial_response)
                LOGGER.debug("WEBSOCKET: Initial WebSocket Response: %s", messages)

                # Extracting and storing the client list
                for message in messages:
                    if "clientList" in message:
                        self._client_list = list(set(message["clientList"]))
                        break

                LOGGER.debug("WEBSOCKET: Client List: %s", self._client_list)
        except Exception as ex:
            raise EheimDigitalWebSocketClientCommunicationError(
                f"Failed to connect to WebSocket: {ex}"
            ) from ex

    async def disconnect_websocket(self) -> None:
        """Disconnect from the WebSocket server."""
        if self._websocket:
            await self._websocket.close()
            self._websocket = None

    async def fetch_devices(self) -> list[EheimDevice]:
        """Fetch devices information and data from the WebSocket."""
        LOGGER.debug("WEBSOCKET: Called function fetch_devices")

        # Connect to the WebSocket if not connected
        if self._websocket is None:
            await self.connect_websocket()

        # Initialize devices as an empty list
        devices = []

        # Iterate through the unique clients and send requests for device information
        for client in self._client_list:
            request_message = (
                f'{{"title": "GET_USRDTA","to": "{client}","from": "USER"}}'
            )
            LOGGER.debug(
                "WEBSOCKET: Sending Device Client: %s Request Message: %s, ",
                client,
                request_message,
            )
            await self._websocket.send(request_message)
            response = await self._websocket.recv()

            # Log the raw response before processing
            # LOGGER.debug("WEBSOCKET: Raw Response for Device Client: %s : %s", client, response)

            messages = json.loads(response)
            LOGGER.debug(
                "WEBSOCKET: Receiving Device Client: %s Response: %s", client, messages
            )

            # Process the response and extract the device information
            if isinstance(messages, list):
                for message in messages:
                    if message["title"] == "USRDTA":
                        device = EheimDevice(message)
                        devices.append(device)
            elif isinstance(messages, dict) and messages["title"] == "USRDTA":
                device = EheimDevice(messages)
                devices.append(device)
            LOGGER.debug("WEBSOCKET: Devices: %s", devices)

        # Log the extracted details
        for device in devices:
            LOGGER.debug(
                "WEBSOCKET: Device Details: title=%s, mac=%s, name=%s, aq_name=%s, mode=%s, version=%s",
                device.title,
                device.mac,
                device.name,
                device.aq_name,
                device.mode,
                device.version,
            )

        self._devices = devices
        return devices

    # Send Request/Command to Device
    async def _send_message(self, message):
        """Send a specific message to the device and wait for its response."""

        async with self._lock:  # Ensure only one request is active at a time
            if self._websocket is None:
                await self.connect_websocket()

            message_str = json.dumps(message)
            await self._websocket.send(message_str)
            LOGGER.debug("WEBSOCKET: Sent message: %s", message_str)

            while True:
                response = await self._websocket.recv()
                response_dict = json.loads(response)

                if response_dict.get("title") in ["REQ_KEEP_ALIVE", "KEEP_ALIVE"]:
                    LOGGER.debug(
                        "WEBSOCKET: Received keep-alive. Continuing to wait for actual response."
                    )
                    continue  # Ignore keep-alives and continue waiting for the actual response

                LOGGER.debug("WEBSOCKET: Received response: %s", response)
                return response

    # LED Specific Functions
    async def turn_light_on(self, mac_address: str):
        """Turn the light on."""
        data = {
            "title": "CCV-SW",
            "to": mac_address,
            "currentValues": [100, 100, 100],
            "from": "USER",
        }
        await self._send_message(data)

    async def turn_light_off(self, mac_address: str):
        """Turn the light off."""
        data = {
            "title": "CCV-SW",
            "to": mac_address,
            "currentValues": [0, 0, 0],
            "from": "USER",
        }
        await self._send_message(data)

    # Acclimation Specific Functions
    async def get_acclimation_settings(self, mac_address: str):
        """Request acclimation settings for the LED."""
        data = {"title": "GET_ACCL", "to": mac_address, "from": "USER"}
        response = await self._send_message(data)
        return response

    async def set_acclimation_settings(
        self,
        mac_address: str,
        duration: int,
        intensity_reduction: int,
        current_accl_day: int,
        accl_active: bool,
        accl_pause: bool,
    ):
        """Set acclimation settings for the LED."""
        data = {
            "title": "ACCLIMATE",
            "to": mac_address,
            "duration": duration,
            "intensityReduction": intensity_reduction,
            "currentAcclDay": current_accl_day,
            "acclActive": accl_active,
            "Pause": accl_pause,
            "from": "USER",
        }
        response = await self._send_message(data)
        return response

    # Dynamic Cycle Specific Functions
    async def get_dynamic_cycle_settings(self, mac_address: str):
        """Request dynamic cycle settings for the LED."""
        data = {"title": "GET_DYCL", "to": mac_address, "from": "USER"}
        response = await self._send_message(data)
        return response

    # Color Channel Specific Functions
    async def get_color_channel_values(self, mac_address: str):
        """Request color channel values for the LED."""
        data = {"title": "REQ_CCV", "to": mac_address, "from": "USER"}
        response = await self._send_message(data)
        return response

    async def set_color_channel_values(self, mac_address: str, current_values: list):
        """Set color channel values for the LED."""
        data = {
            "title": "CCV-SW",
            "to": mac_address,
            "currentValues": current_values,
            "from": "USER",
        }
        response = await self._send_message(data)
        return response

    # Moon Phase Specific Functions
    async def get_moon_phase(self, mac_address: str):
        """Request moon phase settings for the LED."""
        data = {"title": "GET_MOON", "to": mac_address, "from": "USER"}
        response = await self._send_message(data)
        return response

    async def set_moon_phase(self, mac_address: str, moon_phase: int):
        """Set moon phase settings for the LED."""
        data = {
            "title": "SET_MOON",
            "to": mac_address,
            "moonPhase": moon_phase,
            "from": "USER",
        }
        response = await self._send_message(data)
        return response

    # Cloud Specific Functions
    async def get_cloud_settings(self, mac_address: str):
        """Request cloud settings for the LED."""
        data = {"title": "GET_CLOUD", "to": mac_address, "from": "USER"}
        response = await self._send_message(data)
        return response

    # Description Specific Functions
    async def get_description(self, mac_address: str):
        """Request description for the LED."""
        data = {"title": "GET_DSCRPTN", "to": mac_address, "from": "USER"}
        response = await self._send_message(data)
        return response

    # Filter Specific Functions
    async def get_filter_data(self, mac_address: str):
        """Request filter data for the LED."""
        data = {"title": "GET_FILTER_DATA", "to": mac_address, "from": "USER"}
        response = await self._send_message(data)
        return response

    # Heater Specific Functions
    async def get_heater_data(self, mac_address: str):
        """Request heater data for the LED."""
        data = {"title": "GET_EHEATER_DATA", "to": mac_address, "from": "USER"}
        response = await self._send_message(data)
        return response

    # PH Specific Functions
    async def get_ph_data(self, mac_address: str):
        """Request ph data for the LED."""
        data = {"title": "GET_PH_DATA", "to": mac_address, "from": "USER"}
        response = await self._send_message(data)
        return response

    DEVICE_DATA_FUNCTIONS = {
        "filter": [get_filter_data],
        "heater": [get_heater_data],
        "led_control": [
            get_color_channel_values,
            get_acclimation_settings,
            get_dynamic_cycle_settings,
            get_moon_phase,
            get_cloud_settings,
            get_description,
        ],
        "ph_control": [get_ph_data],
    }

    async def get_device_data(self, device: EheimDevice) -> Dict:
        """Get data for all devices."""
        device_type = device.device_type
        device_group = device.device_group
        functions = self.DEVICE_DATA_FUNCTIONS.get(device_group, [])

        if not functions:
            LOGGER.warning(
                "No request functions found for device type: %s", device_type
            )
            return {}

        device_data = {}
        for function in functions:
            response = await function(self, device.mac)
            response_dict = json.loads(response)
            device_data.update(response_dict)
        # LOGGER.debug("WEBSOCKET: All Device Data: %s", device_data)
        return device_data
