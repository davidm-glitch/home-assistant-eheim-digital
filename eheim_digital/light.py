"""Platform for light integration."""
from dataclasses import dataclass
from collections.abc import Callable
from typing import Any
from homeassistant.components.light import LightEntity, LightEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import CoordinatorEntity


from .coordinator import EheimDigitalDataUpdateCoordinator
from .devices import EheimDevice
from .const import LOGGER, DOMAIN


@dataclass
class EheimLightDescriptionMixin:
    """Mixin for Eheim light."""

    value_fn: Callable[[dict[str, Any]], Any]


@dataclass
class EheimLightDescription(LightEntity):
    """Class describing Eheim light entities."""

    key: str
    name: str
    attr_fn: Callable[[dict[str, Any]], dict[str, Any]] = lambda _: {}


# Placeholder for light descriptions


class EheimLedDevice(CoordinatorEntity, LightEntity):
    "Define an Eheim Light Entity"

    entity_description: EheimLightDescription

    def __init__(
        self,
        coordinator: EheimDigitalDataUpdateCoordinator,
        description: EheimLightDescription,
        device: EheimDevice,
    ) -> None:
        """Initialize the Light."""
        super().__init__(coordinator)
        self.entity_description = description
        self._device = device

    # Override necessary properties and methods for the light


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Add EheimDevice entities from a config_entry."""
    coordinator: EheimDigitalDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    lights = []
    for device in coordinator.devices:
        device_group = device.device_group
        # Placeholder for light group definitions
        light_keys_for_group = (
            []
        )  # Define a LIGHT_GROUPS similar to SENSOR_GROUPS if needed

        for description in LIGHT_DESCRIPTIONS:
            if description.key in light_keys_for_group:
                lights.append(EheimLedDevice(coordinator, description, device))

    async_add_entities(lights, True)
