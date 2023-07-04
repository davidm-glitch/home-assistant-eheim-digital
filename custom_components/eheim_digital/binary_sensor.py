"""Binary sensor platform for integration_EheimDigital."""
from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.core import HomeAssistant

from .const import DOMAIN, LOGGER
from .coordinator import EheimDigitalDataUpdateCoordinator
from .entity import EheimDigitalEntity

ENTITY_DESCRIPTIONS = (
    BinarySensorEntityDescription(
        key="integration_EheimDigital",
        name="Integration EheimDigital Binary Sensor",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
    ),
)


async def async_setup_entry(hass: HomeAssistant, entry, async_add_devices):
    """Set up the binary_sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices(
        EheimDigitalBinarySensor(
            coordinator=coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class EheimDigitalBinarySensor(
    EheimDigitalEntity, BinarySensorEntity
):
    """eheim_digital binary_sensor class."""

    def __init__(
        self,
        coordinator: EheimDigitalDataUpdateCoordinator,
        entity_description: BinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary_sensor class."""
        super().__init__(coordinator)
        self.entity_description = entity_description

    @property
    def is_on(self):
        if self.coordinator.data and isinstance(self.coordinator.data[0], dict):
            return self.coordinator.data[0].get("title", "") == "foo"

        LOGGER.error("The coordinator data is not as expected")
        return False
