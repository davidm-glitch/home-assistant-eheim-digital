"""Platform for light integration."""
from homeassistant.components.light import LightEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from .coordinator import EheimDigitalDataUpdateCoordinator
from .const import LOGGER, DOMAIN

class EheimLedDevice(LightEntity):
    """Representation of an EHEIM LED Control."""

    def __init__(self, coordinator: EheimDigitalDataUpdateCoordinator, device) -> None:
        """Initialize the LED control entity."""
        self.device = device
        self.mac = device.from_mac
        self.ccv_current_brightness = None
        self.max_moon_light = None
        self.min_moon_light = None
        self.moonlight_active = None
        self.moonlight_cycle = 0
        self.cloud_probability = 0
        self.cloud_max_amount = 0
        self.cloud_min_intensity = 0
        self.cloud_max_intensity = 0
        self.cloud_min_duration = 0
        self.cloud_max_duration = 0
        self.cloud_active = False
        self.acclimate_duration = 0
        self.acclimate_intensity_reduction = 0
        self.acclimate_current_accl_day = 0
        self.acclimate_active = False
        self.acclimate_pause = False
        self.coordinator = coordinator
        self._state = False

        LOGGER.debug("LIGHT: EheimLEDDevice with MAC %s initialized", self.mac)

    @property
    def name(self):
        """Return the name of the LED Device."""
        return self.device.name

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self.device.from_mac

    @property
    def is_on(self):
        """Return the state of the light."""
        return self._state

    async def async_turn_on(self, **kwargs):
        """Turn the light on."""
        await self.coordinator.turn_light_on(self.mac)

    async def async_turn_off(self, **kwargs):
        """Turn the light off."""
        await self.coordinator.turn_light_off(self.mac)

    async def set_moonlight_settings(self, min_moonlight, max_moonlight, moonlight_active, moonlight_cycle, moon_color):
        """Set moonlight settings."""
        data = {
            "title": "MOON",
            "to": self.mac,
            "minmoonlight": min_moonlight,
            "maxmoonlight": max_moonlight,
            "moonlightActive": moonlight_active,
            "moonlightCycle": moonlight_cycle,
            "moonColor": moon_color,
            "from": "USER"
        }
        await self.coordinator.set_moonlight_settings(data)
        # Update entity attributes based on the new settings
        self.min_moon_light = min_moonlight
        self.max_moon_light = max_moonlight
        self.moonlight_active = self.convert_boolean_to_string(moonlight_active)
        self.moonlight_cycle = self.convert_boolean_to_string(moonlight_cycle)

    async def set_cloud_settings(self, cloud_probability, cloud_max_amount, cloud_min_intensity, cloud_max_intensity, cloud_min_duration, cloud_max_duration, cloud_active):
        """Set cloud settings."""
        data = {
            "title": "CLOUD",
            "to": self.mac,
            "probability": cloud_probability,
            "maxAmount": cloud_max_amount,
            "minIntensity": cloud_min_intensity,
            "maxIntensity": cloud_max_intensity,
            "minDuration": cloud_min_duration,
            "maxDuration": cloud_max_duration,
            "cloudActive": cloud_active,
            "mode": 2,
            "from": "USER"
        }
        await self.coordinator.set_cloud_settings(data)
        # Update entity attributes based on the new settings
        self.cloud_probability = cloud_probability
        self.cloud_max_amount = cloud_max_amount
        self.cloud_min_intensity = cloud_min_intensity
        self.cloud_max_intensity = cloud_max_intensity
        self.cloud_min_duration = cloud_min_duration
        self.cloud_max_duration = cloud_max_duration
        self.cloud_active = self.convert_boolean_to_string(cloud_active)

    async def async_update(self):
        """Update the entity with data from the WebSocket."""
        # LOGGER.debug("Updating EheimLEDDevice for MAC: %s", self.mac)

        # Use the coordinator's method to fetch device-specific data
        device_data = await self.coordinator.async_get_device_data(self.mac)
        if device_data:
            # Process and update the entity attributes based on the fetched device data
            self.process_device_data(device_data)

        # LOGGER.debug("EheimLedDevice updated: %s", self.__dict__)

    async def request_channel_values(self):
        """Request current channel values for the LED."""
        response = await self.coordinator.request_channel_values({"to": self.mac, "title": "REQ_CCV", "from": "USER"})
        if response:
            self.process_device_data(response)

    async def set_channel_values(self, channel_values: list[int]):
        """Set current channel values for the LED."""
        response = await self.coordinator.set_channel_values(self.mac, channel_values)
        if response:
            self.process_device_data(response)

    async def request_acclimation_settings(self):
        """Request acclimation settings for the LED."""
        response = await self.coordinator.request_acclimation_settings(self.mac)
        if response:
            self.process_device_data(response)


    async def set_acclimation_settings(self, duration, intensity_reduction, current_accl_day, accl_active, accl_pause):
        """Set acclimation settings for the LED."""
        response = await self.coordinator.set_acclimation_settings(self.mac, duration, intensity_reduction, current_accl_day, accl_active, accl_pause)
        if response:
            self.process_device_data(response)

    async def request_dynamic_cycle_settings(self):
        """Request dynamic cycle settings for the LED."""
        response = await self.coordinator.request_dynamic_cycle_settings(self.mac)
        if response:
            self.process_device_data(response)

    async def set_dynamic_cycle_settings(self, dawn_start, sunrise_end, sunset_start, dusk_end):
        """Set dynamic cycle settings for the LED."""
        response = await self.coordinator.set_dynamic_cycle_settings(self.mac, dawn_start, sunrise_end, sunset_start, dusk_end)
        if response:
            self.process_device_data(response)


    def process_device_data(self, device_data: dict) -> None:
        """Process device-specific data and update entity attributes."""
        title = device_data.get("title")

        # Handle channel values
        if title == "REQ_CCV":
            self.ccv_current_brightness = device_data.get('currentValues')

        # Handle moonlight settings
        elif title == "GET_MOON":
            self.max_moon_light = device_data.get('maxmoonlight')
            self.min_moon_light = device_data.get('minmoonlight')
            self.moonlight_active = self.convert_boolean_to_string(device_data.get('moonlightActive'))
            self.moonlight_cycle = self.convert_boolean_to_string(device_data.get('moonlightCycle'))

        # Handle cloud settings
        elif title == "GET_CLOUD":
            self.cloud_probability = device_data.get('probability')
            self.cloud_max_amount = device_data.get('maxAmount')
            self.cloud_min_intensity = device_data.get('minIntensity')
            self.cloud_max_intensity = device_data.get('maxIntensity')
            self.cloud_min_duration = device_data.get('minDuration')
            self.cloud_max_duration = device_data.get('maxDuration')
            self.cloud_active = self.convert_boolean_to_string(device_data.get('cloudActive'))

        # Handle acclimation settings
        elif title == "GET_ACCL":
            self.acclimate_duration = device_data.get('duration')
            self.acclimate_intensity_reduction = device_data.get('intensityReduction')
            self.acclimate_current_accl_day = device_data.get('currentAcclDay')
            self.acclimate_active = self.convert_boolean_to_string(device_data.get('acclActive'))
            self.acclimate_pause = self.convert_boolean_to_string(device_data.get('acclPause'))

    @staticmethod
    def convert_boolean_to_string(boolean) -> str:
        """Convert a boolean value to a string."""
        return 'ON' if boolean else 'OFF'


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up the EHEIM Digital light platform from a config entry."""
    LOGGER.debug("LIGHT: Setting up EHEIM Digital light platform")
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    devices = coordinator.devices

    entities = []
    for device in devices:
        device_mac = device.get("from")
        if device.device_group == "LIGHTING":
            entities.append(EheimLedDevice(coordinator, device))
            LOGGER.debug("LIGHT: Added EheimLedDevice with MAC %s", device_mac)

    LOGGER.debug("LIGHT: Devices in coordinator: %s", devices)
    LOGGER.debug("LIGHT: Adding Light entities to Home Assistant")
    async_add_entities(entities)



