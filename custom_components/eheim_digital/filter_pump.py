"""Platform for filter integration"""

#from homeassistant.helpers.entity import Entity
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.core import HomeAssistant
from .coordinator import EheimDigitalDataUpdateCoordinator
from homeassistant.config_entries import ConfigEntry

from .const import LOGGER, DOMAIN
LOGGER.debug("Filter platform loaded")

class EheimFilterDevice(BinarySensorEntity):
    """Representation of an EHEIM filter"""

    def __init__(self, coordinator: EheimDigitalDataUpdateCoordinator, device) -> None:
        """Initialize the filter entity."""
        self.device = device
        self.mac = device.from_mac
        self.coordinator = coordinator
        self._state = False
        self._filter_state = None


        LOGGER.debug("FilterEntity with MAC %s initialized", self.mac)
        LOGGER.debug("MAC Address: %s", self.mac)
        LOGGER.debug("Name: %s", self.name)
        LOGGER.debug("EheimFILTERDevice with MAC %s initialized", self.mac)

    @property
    def name(self):
        """Return the name of the Filter."""
        return f"EHEIM Filter {self.mac}"

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self.mac

    @property
    def is_on(self):
        """Return the state of the Filter."""
        return self._state

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up the EHEIM Digital Filter platform from a config entry."""
    LOGGER.debug("Setting up EHEIM Digital Filter platform")

    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    devices = coordinator.devices

    entities = []
    for device in devices:
        device_mac = device.get("from")
        if device.device_group == "FILTER_PUMP":
            entities.append(EheimFilterDevice(coordinator, device))
            LOGGER.debug("Added EheimFilterDevice with MAC %s", device_mac)

    LOGGER.debug("Adding Filter entities to Home Assistant")
    async_add_entities(entities)