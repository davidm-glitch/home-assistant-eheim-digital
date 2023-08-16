"""The EHEIM Digital integration."""
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_IP_ADDRESS

from homeassistant.helpers import device_registry as dr



from .const import DOMAIN, LOGGER, PLATFORMS, UPDATE_INTERVAL
from .websocket import EheimDigitalWebSocketClient
from .coordinator import EheimDigitalDataUpdateCoordinator

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the EHEIM Digital integration from a config entry."""
    LOGGER.debug("INIT: Setting up EHEIM Digital integration")

    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}


    websocket_client = EheimDigitalWebSocketClient(entry.data[CONF_IP_ADDRESS])
    devices = await websocket_client.fetch_devices()

    coordinator = EheimDigitalDataUpdateCoordinator(hass, entry, websocket_client)
    coordinator.devices = devices

    await coordinator.async_config_entry_first_refresh()

    # Register devices with Home Assistant's device registry
    device_registry = dr.async_get(hass)

    for device in devices:
        device_registry.async_get_or_create(
            config_entry_id=entry.entry_id,
            identifiers={(DOMAIN, device.mac)},
            name=device.name,
            manufacturer="EHEIM",
            model=device.model,
            sw_version=device.version,
        )
        #LOGGER.debug("INIT: Registered device Name: %s, MAC: %s, Type: %s, Version: %s",
        #             device.name, device.mac, device.device_type, device.version)

    entry.async_on_unload(entry.add_update_listener(update_listener))

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok

async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update listener."""
    await hass.config_entries.async_reload(entry.entry_id)

