"""Platform for filter integration"""

from homeassistant.helpers.entity import Entity as FilterEntity
from homeassistant.core import HomeAssistant
from .coordinator import EheimDigitalDataUpdateCoordinator
from homeassistant.config_entries import ConfigEntry

from .const import LOGGER, DOMAIN, DEVICE_GROUPS, DEVICE_VERSIONS
LOGGER.debug("Filter platform loaded")

class EheimFilterDevice(Entity):
    """Representation of an EHEIM filter"""

    def __init__(self, coordinator: EheimDigitalDataUpdateCoordinator, device) -> None:
        """Initialize the filter entity."""
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

def get_device_group_for_version(version: int) -> str:
    """Map version number to device group."""
    for group, versions in DEVICE_GROUPS.items():
        if DEVICE_VERSIONS[version] in versions:
            return group
    return None

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up the EHEIM Digital Filter platform from a config entry."""
    LOGGER.debug("Setting up EHEIM Digital Filter platform")

    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    devices = coordinator.devices

    entities = []
    for mac_address, device in devices.items():
        if get_device_group_for_version(device.version) == "FILTER":
            entities.append(EheimFilterDevice(coordinator, device))
            LOGGER.debug("Added EheimFilterDevice with MAC %s", mac_address)

    LOGGER.debug("Adding Filter entities to Home Assistant")
    async_add_entities(entities)