"""EHEIM WebSocket Client."""
import json
import websockets
from typing import Dict

from .const import LOGGER, DEVICE_VERSIONS, DEVICE_GROUPS, REQUEST_MESSAGES

class EheimDigitalWebSocketClientError(Exception):
    """Exception to indicate a general WebSocket error."""

class EheimDigitalWebSocketClientCommunicationError(EheimDigitalWebSocketClientError):
    """Exception to indicate a communication error."""

class EheimDevice:
    """EHEIM Device representation."""

    def __init__(self, data: dict) -> None:
        """EHEIM Device initialization."""
        self.title = data.get("title")
        self.from_mac = data.get("from")
        self.name = data.get("name")
        self.aq_name = data.get("aqName")
        self.mode = data.get("mode")
        self.version = data.get("version")
        self.language = data.get("language")
        self.timezone = data.get("timezone")
        self.tank_id = data.get("tID")
        self.dst = data.get("dst")
        self.tank_config = data.get("tankconfig")
        self.power = data.get("power")
        self.net_mode = data.get("netmode")
        self.host = data.get("host")
        self.group_id = data.get("groupID")
        self.meshing = data.get("meshing")
        self.first_start = data.get("firstStart")
        self.revision = data.get("revision")
        self.latest_available_revision = data.get("latestAvailableRevision")
        self.firmware_available = data.get("firmwareAvailable")
        self.email_address = data.get("emailAddr")
        self.live_time = data.get("liveTime")
        self.user_name = data.get("usrName")
        self.unit = data.get("unit")
        self.demo_use = data.get("demoUse")
        self.sys_led = data.get("sysLED")


    def __repr__(self):
        """String representation of the EheimDevice."""
        return f"EheimDevice(title={self.title}, name={self.name}, from_mac={self.from_mac})"

    def determine_device_type(self) -> str:
        """Determine the device type based on the version number."""
        if self.version in DEVICE_VERSIONS:
            return DEVICE_VERSIONS[self.version]
        return "UNKNOWN"

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
        LOGGER.debug('Called function connect_websocket from websocket.py')
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
        LOGGER.debug('Called function fetch_client_list from websocket.py')
        if self._websocket is None:
            await self.connect_websocket()

        # Sending a request message to get client list information (modify as needed)
        request_message = {"title": "GET_CLIENT_LIST", "from": "USER"}
        await self._websocket.send(json.dumps(request_message))

        # Waiting for the response
        response = await self._websocket.recv()
        messages = json.loads(response)
        LOGGER.debug("Fetch Cleint List Response: %s", messages)

        # Assuming that the client list is inside each message in the list
        client_list = []
        for message in messages:
            if isinstance(message, dict) and "clientList" in message:
                client_list.extend(message["clientList"])

        self._client_list = client_list
        LOGGER.debug("Client List From Fetch Function: %s", client_list)

        return client_list

    async def fetch_devices(self) -> list[EheimDevice]:
        """Fetch devices information and data from the WebSocket."""
        LOGGER.debug('Called function fetch_devices from websocket.py')

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
            LOGGER.debug("Sending Device Request Message: %s", request_message)
            await self._websocket.send(request_message)
            response = await self._websocket.recv()
            messages = json.loads(response)
            LOGGER.debug("Fetch Devices Response: %s", messages)

            # Process the response and extract the device information
            if isinstance(messages, list):
                for message in messages:
                    if message["title"] == "USRDTA":
                        device = EheimDevice(message)
                        devices.append(device)
            elif isinstance(messages, dict):
                if messages["title"] == "USRDTA":
                    device = EheimDevice(messages)
                    devices.append(device)

        # Log the extracted details (moved outside of the client loop)
        for device in devices:
            LOGGER.debug("Device Details: title=%s, from_mac=%s, name=%s, aq_name=%s, mode=%s, version=%s",
                        device.title, device.from_mac, device.name, device.aq_name, device.mode, device.version)

        self._devices = devices  # Store the devices list as an instance variable
        LOGGER.debug("Devices: %s", devices)

        return devices

    def determine_device_group(self) -> str:
        """Determine the device group based on the version number."""
        for group, versions in DEVICE_GROUPS.items():
            if self.version in versions:
                LOGGER.debug("Determine Device Group Function: %s", group)
                return group
        return "OTHER"


    async def get_device_data(self, device_type: str) -> Dict:
        """Get data for the specified device type."""
        request_messages = REQUEST_MESSAGES.get(device_type, [])
        if not request_messages:
            LOGGER.warning("No request messages found for device type: %s", device_type)
            return {}

        device_data = {}
        for message in request_messages:
            response = await self._query_device(message)
            if response:
                device_data[message] = response
        LOGGER.debug("Device Data: %s", device_data)
        return device_data

#Send Request/Command to Device
    async def _send_message(self, message):
        """Send a specific message to the device."""
        LOGGER.debug("Sending Message: %s", message)

        message_str = json.dumps(message)  # Convert dictionary to JSON string
        await self._websocket.send(message_str)  # Send the JSON string
        response = await self._websocket.recv()

        LOGGER.debug("Response: %s", response)

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