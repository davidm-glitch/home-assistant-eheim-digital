"""Data update coordinator for the EHEIM Digital integration."""
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .websocket import EheimDigitalWebSocketClientCommunicationError
from .const import LOGGER, UPDATE_INTERVAL, DEVICE_TYPES
from .devices import EheimDevice

class EheimDigitalDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the WebSocket."""
    def __init__(self, hass: HomeAssistant, websocket_client, devices)-> None:
        self._websocket_client = websocket_client
        self._devices = devices
        self._devices_data = {}

        super().__init__(
            hass,
            LOGGER,
            name="Eheim Digital Data Coordinator",
            update_method=self.async_update_data,
            update_interval=UPDATE_INTERVAL,
        )

    @property
    def devices(self):
        """Return the devices."""
        return self._devices


    async def async_get_device_data(self, mac_address: str) -> dict:
        """Fetch device-specific data for the specified MAC address."""
        try:
            device_data = await self._websocket_client.get_device_data(mac_address)
            return device_data
        except EheimDigitalWebSocketClientCommunicationError as err:
            LOGGER.error("Error communicating with WebSocket: %s", err)
            return {}



    async def async_update_data(self):
        """Fetch data from the WebSocket and update the data in Coordinator."""
        LOGGER.debug("COORDINATOR: Calling WebSocket to update data in Coordinator")

        try:
            # Initialize devices_data
            devices_data = {}

            # Iterate through known device types from constants
            for device_type in DEVICE_TYPES:
                # Fetching all devices for the given device type
                devices_response = await self._websocket_client.get_device_data(device_type)
                LOGGER.debug("COORDINATOR: Received response from WebSocket for %s: %s", device_type, devices_response)

                # Creating EheimDevice objects and adding them to the list
                devices_list = []
                for request_key, device_data in devices_response.items():
                    device = EheimDevice(device_data)
                    devices_list.append(device)

                devices_data[device_type] = devices_list

            self._devices = devices_data

        except EheimDigitalWebSocketClientCommunicationError as err:
            raise UpdateFailed(f"Error communicating with WebSocket: {err}") from err

        LOGGER.debug("COORDINATOR: Updated data In Coordinator from WebSocket: %s", devices_data)
        return devices_data



    async def turn_light_on(self, mac_address: str):
        """Turn the light on."""
        await self._websocket_client.turn_light_on(mac_address)
        LOGGER.debug("COORDINATOR:  Turned on light for MAC: %s", mac_address)

    async def turn_light_off(self, mac_address: str):
        """Turn the light off."""
        await self._websocket_client.turn_light_off(mac_address)
        LOGGER.debug("COORDINATOR: Turned off light for MAC: %s", mac_address)

    async def request_channel_values(self, mac_address: str):
        """Request current channel values for the specified MAC address."""
        await self._websocket_client.request_color_channel_values(mac_address)
        LOGGER.debug("COORDINATOR: Requested channel values for MAC: %s", mac_address)

    async def set_channel_values(self, mac_address: str, channel_values: list[int]):
        """Set channel values for the LED."""
        await self._websocket_client.set_color_channel_values(mac_address, channel_values)
        LOGGER.debug("Set channel values for MAC: %s", mac_address)

    async def request_moonlight_settings(self, mac_address: str):
        """Request moonlight settings for the specified MAC address."""
        await self._websocket_client.request_moonlight_settings(mac_address)
        LOGGER.debug("COORDINATOR: Requested moonlight settings for MAC: %s", mac_address)

    async def set_moonlight_settings(self, mac_address: str, moonlight_intensity: int, moonlight_duration: int, moonlight_active: bool):
        """Set moonlight settings for the LED."""
        await self._websocket_client.set_moonlight_settings(mac_address, moonlight_intensity, moonlight_duration, moonlight_active)
        LOGGER.debug("Set moonlight settings for MAC: %s", mac_address)

    async def request_cloud_settings(self, mac_address: str):
        """Request cloud settings for the specified MAC address."""
        await self._websocket_client.request_cloud_settings(mac_address)
        LOGGER.debug("COORDINATOR: Requested cloud settings for MAC: %s", mac_address)

    async def set_cloud_settings(self, mac_address: str, cloud_intensity: int, cloud_duration: int, cloud_active: bool):
        """Set cloud settings for the LED."""
        await self._websocket_client.set_cloud_settings(mac_address, cloud_intensity, cloud_duration, cloud_active)
        LOGGER.debug("Set cloud settings for MAC: %s", mac_address)

    async def request_acclimation_settings(self, mac_address: str):
        """Request acclimation settings for the LED."""
        await self._websocket_client.request_acclimation_settings(mac_address)

    async def set_acclimation_settings(self, mac_address: str, duration: int, intensity_reduction: int, current_accl_day: int, accl_active: bool, accl_pause: bool):
        """Set acclimation settings for the LED."""
        await self._websocket_client.set_acclimation_settings(mac_address, duration, intensity_reduction, current_accl_day, accl_active, accl_pause)
        LOGGER.debug("COORDINATOR: Set acclimation settings for MAC: %s", mac_address)

    async def request_dynamic_cycle_settings(self, mac_address: str):
        """Request dynamic cycle settings for the LED."""
        await self._websocket_client.request_dynamic_cycle_settings(mac_address)
        LOGGER.debug("COORDINATOR: Requested dynamic cycle settings for MAC: %s", mac_address)

    async def set_dynamic_cycle_settings(self, mac_address: str, dawn_start: str, sunrise_end: str, sunset_start: str, dusk_end: str):
        """Set dynamic cycle settings for the LED."""
        await self._websocket_client.set_dynamic_cycle_settings(mac_address, dawn_start, sunrise_end, sunset_start, dusk_end)
        LOGGER.debug("COORDINATOR: Set dynamic cycle settings for MAC: %s", mac_address)


