"""Switch platform for eheim_digital."""
from __future__ import annotations
from homeassistant.core import HomeAssistant
from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription

from .const import DOMAIN, LOGGER
from .coordinator import EheimDigitalDataUpdateCoordinator
from .entity import IntegrationEheimDigitalEntity

ENTITY_DESCRIPTIONS = (
    SwitchEntityDescription(
        key="eheim_digital",
        name="Integration Switch",
        icon="mdi:format-quote-close",
    ),
)


async def async_setup_entry(hass:HomeAssistant, entry, async_add_devices):
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices(
        IntegrationEheimDigitalSwitch(
            coordinator=coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class IntegrationEheimDigitalSwitch(IntegrationEheimDigitalEntity, SwitchEntity):
    """eheim_digital switch class."""

    def __init__(
        self,
        coordinator: EheimDigitalDataUpdateCoordinator,
        entity_description: SwitchEntityDescription,
    ) -> None:
        """Initialize the switch class."""
        super().__init__(coordinator)
        self.entity_description = entity_description

    @property
    def is_on(self):
        if self.coordinator.data and isinstance(self.coordinator.data[0], dict):
            return self.coordinator.data[0].get("title", "") == "foo"
        else:
            LOGGER.error("The coordinator data is not as expected")
            return False



    async def async_turn_on(self, **_: any) -> None:
        """Turn on the switch."""
        await self.coordinator.api.async_set_title("bar")
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **_: any) -> None:
        """Turn off the switch."""
        await self.coordinator.api.async_set_title("foo")
        await self.coordinator.async_request_refresh()

    async def async_setup_entry(self, hass:HomeAssistant, entry, async_add_devices):
        """Set up the switch platform."""
        coordinator = hass.data[DOMAIN][entry.entry_id]
        async_add_devices(
            IntegrationEheimDigitalSwitch(
                coordinator=coordinator,
                entity_description=entity_description,
            )
            for entity_description in ENTITY_DESCRIPTIONS
        )
