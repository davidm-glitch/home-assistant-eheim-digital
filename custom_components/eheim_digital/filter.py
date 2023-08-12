"""Platform for filter integration"""
from homeassistant.helpers.entity import Entity
from homeassistant.core import HomeAssistant
from .coordinator import EheimDigitalDataUpdateCoordinator
from homeassistant.config_entries import ConfigEntry

from .const import LOGGER, DOMAIN
LOGGER.debug("Filter platform loaded")

class EheimFilterDevice(Entity):
    """Representation of an EHEIM filter"""

    def __init__(self, coordinator: EheimDigitalDataUpdateCoordinator, device) -> None:
        """Initialize the filter entity."""
        self._name = device.name
        self.mac = device.from_mac
        self.coordinator = coordinator
        self._state = False
        self._filter_state = None

        LOGGER.debug("FilterEntity with MAC %s initialized", self.mac)

    @property
    def name(self):
        """Return the name of the Filter."""
        return f"EHEIM Filter {self._name}"

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self.mac

    @property
    def is_on(self):
        """Return the state of the Filter."""
        return self._state

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up the EHEIM Digital filter platform."""
    LOGGER.debug("Setting up EHEIM Digital filter platform")
    coordinator = hass.data[DOMAIN][entry.entry_id]
    devices = coordinator.data

    # Create filter entities based on the devices
    entities = [EheimFilterDevice(coordinator, device) for device in devices if device.group == "FILTER"]
    LOGGER.debug ("FILTER Devices: %s", devices)
    LOGGER.debug("Adding %s filter entities", len(entities))
    async_add_entities(entities)