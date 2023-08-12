"""The EHEIM Digital integration."""
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_IP_ADDRESS

from .const import DOMAIN, LOGGER, PLATFORMS
from .websocket import EheimDigitalWebSocketClient
from .coordinator import EheimDigitalDataUpdateCoordinator

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the EHEIM Digital integration."""
    LOGGER.debug("INIT: Setting up EHEIM Digital integration")
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    websocket_client = EheimDigitalWebSocketClient(entry.data[CONF_IP_ADDRESS])

    # Fetch devices once on startup
    devices = await websocket_client.fetch_devices()

    # Create the coordinator with the fetched devices
    # Create the coordinator with the fetched devices
    coordinator = EheimDigitalDataUpdateCoordinator(hass, websocket_client, devices)
    await coordinator.async_config_entry_first_refresh()

    # Store the coordinator in hass.data
    if entry.entry_id not in hass.data[DOMAIN]:
        hass.data[DOMAIN][entry.entry_id] = {}

    hass.data[DOMAIN][entry.entry_id]["coordinator"] = coordinator


    if not coordinator.last_update_success:
        LOGGER.debug("INIT: Initial data fetch failed")
        return False

    # Access the devices from the coordinator
    devices = coordinator.devices

    # Set up other platforms based on device types
    for device in devices:
        mac_address = device.get("from")  # Assuming the MAC address is stored under the key "from"
        version = device.get("version")
        device_group = device.get("device_group")
        device_name = device.get("device_name")
        LOGGER.debug("INIT: Found device %s with version %s: Device Name: %s, Group: %s", mac_address, version, device_name, device_group)


    for platform in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, platform)
        )
    LOGGER.debug("INIT: Forwarding entry setup for %s platform", platform)



    LOGGER.debug("INIT: EHEIM Digital integration setup complete")
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    LOGGER.debug("INIT: Unloading EHEIM Digital integration")
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        # Disconnect the WebSocket
        LOGGER.debug("INIT: Disconnecting WebSocket")
        websocket_client = EheimDigitalWebSocketClient(entry.data[CONF_IP_ADDRESS])
        await websocket_client.disconnect_websocket()

        # Remove data from hass.data
        LOGGER.debug("INIT: Removing data from hass.data")
        hass.data[DOMAIN].pop(entry.entry_id)

    LOGGER.debug("INIT: EHEIM Digital integration unloaded")
    return unload_ok
