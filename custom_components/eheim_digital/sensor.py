"""Sensor platform for eheim_digital."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.core import HomeAssistant
from .const import DOMAIN, LOGGER
from .coordinator import EheimDigitalDataUpdateCoordinator
from .entity import IntegrationEheimDigitalEntity

ENTITY_DESCRIPTIONS = (
    SensorEntityDescription(
        key="eheim_digital",
        name="Integration Sensor",
        icon="mdi:format-quote-close",
    ),
    # Add more SensorEntityDescriptions here for each sensor
)

async def async_setup_entry(hass: HomeAssistant, entry, async_add_devices):
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    # Create an entity for each sensor in each device
    entities = []
    for device in coordinator.data:
        if device.get('name'):
            name = device['name']
        else:
            name = "Unnamed Device"

        device_type = device.get('title')  # Check if 'title' key exists
        if device_type:
            for entity_description in ENTITY_DESCRIPTIONS:
                if entity_description.key.startswith(device_type):
                    entities.append(
                        IntegrationEheimDigitalSensor(
                            coordinator=coordinator,
                            entity_description=entity_description,
                            device=device,
                            name=name,
                        )
                    )
        else:
            LOGGER.warning("Device does not have a 'title' key: %s", device)

    async_add_devices(entities)



class IntegrationEheimDigitalSensor(IntegrationEheimDigitalEntity, SensorEntity):
    """eheim_digital Sensor class."""

    def __init__(
        self,
        coordinator: EheimDigitalDataUpdateCoordinator,
        entity_description: SensorEntityDescription,
        device: dict,
        name: str,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self.device = device
        self._attr_name = name

    @property
    def native_value(self):
        # The sensor's state is the value of the device property that it represents
        return self.device.get(self.entity_description.key.split('_', 1)[1])
