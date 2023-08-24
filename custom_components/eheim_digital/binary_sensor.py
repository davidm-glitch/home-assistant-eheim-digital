"""Platform for BinarySensor integration"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import format_mac

from . import EheimDigitalDataUpdateCoordinator
from .devices import EheimDevice
from .const import LOGGER, DOMAIN


@dataclass
class EheimBinarySensorDescriptionMixin:
    """Mixin for Eheim binary sensor."""

    value_fn: Callable[[dict[str, Any]], StateType]


@dataclass
class EheimBinarySensorDescription(
    BinarySensorEntityDescription, EheimBinarySensorDescriptionMixin
):
    """Class describing Eheim binary sensor entities."""

    attr_fn: Callable[[dict[str, Any]], dict[str, StateType]] = lambda _: {}


BINARY_SENSOR_DESCRIPTIONS: tuple[EheimBinarySensorDescription, ...] = (
    # Heater Binary Sensors
    EheimBinarySensorDescription(
        key="heater_is_heating",
        device_class=BinarySensorDeviceClass.RUNNING,
        name="Heater Is Heating",
        entity_registry_enabled_default=True,
        value_fn=lambda data: data.get("isHeating"),
    ),
    EheimBinarySensorDescription(
        key="heater_alert",
        device_class=BinarySensorDeviceClass.PROBLEM,
        name="Heater Alert",
        entity_registry_enabled_default=True,
        value_fn=lambda data: data.get("alert_State"),
    ),
    EheimBinarySensorDescription(
        key="heater_is_active",
        device_class=BinarySensorDeviceClass.RUNNING,
        name="Heater State",
        entity_registry_enabled_default=True,
        value_fn=lambda data: data.get("active"),
    ),
    # PH Control Binary Sensors
    EheimBinarySensorDescription(
        key="ph_control_acclimatization",
        device_class=BinarySensorDeviceClass.RUNNING,
        name="PH Acclimatization",
        entity_registry_enabled_default=True,
        value_fn=lambda data: data.get("acclimatization"),
    ),
    EheimBinarySensorDescription(
        key="ph_control_is_active",
        device_class=BinarySensorDeviceClass.RUNNING,
        name="PH Is Active",
        entity_registry_enabled_default=True,
        value_fn=lambda data: data.get("active"),
    ),
    EheimBinarySensorDescription(
        key="ph_control_alert",
        device_class=BinarySensorDeviceClass.PROBLEM,
        name="PH Alert",
        entity_registry_enabled_default=True,
        value_fn=lambda data: data.get("alertState"),
    ),
    EheimBinarySensorDescription(
        key="ph_control_is_valve_active",
        device_class=BinarySensorDeviceClass.RUNNING,
        name="PH Valve Is Active",
        entity_registry_enabled_default=True,
        value_fn=lambda data: data.get("valveIsActive"),
    ),
    # Filter Binary Sensors
    EheimBinarySensorDescription(
        key="filter_is_active",
        device_class=BinarySensorDeviceClass.RUNNING,
        name="Filter State",
        entity_registry_enabled_default=True,
        value_fn=lambda data: data.get("FilterActive"),
    ),
)


BINARY_SENSOR_GROUPS = {
    # Define binary sensor groups similar to SENSOR_GROUPS
    "heater": ["heater_is_heating", "heater_alert", "heater_is_active"],
    "ph_control": [
        "ph_control_acclimatization",
        "ph_control_is_active",
        "ph_control_alert",
        "ph_control_is_valve_active",
        "ph_control_firmware_update",
    ],
    "filter": ["filter_is_active"],
}


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Add EheimDevice entities from a config_entry."""
    LOGGER.debug("Setting up Eheim Digital BinarySensor platform")

    coordinator: EheimDigitalDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    binary_sensors = []
    for device in coordinator.devices:
        device_group = device.device_group
        binary_sensor_keys_for_group = BINARY_SENSOR_GROUPS.get(device_group, [])

        device_data = _get_binary_sensor_data(coordinator.data, device.mac)

        for description in BINARY_SENSOR_DESCRIPTIONS:
            if description.key in binary_sensor_keys_for_group:
                binary_sensors.append(
                    EheimBinarySensor(coordinator, description, device, device_data)
                )

    async_add_entities(binary_sensors, True)


class EheimBinarySensor(
    CoordinatorEntity[EheimDigitalDataUpdateCoordinator], BinarySensorEntity
):
    "Define an Eheim BinarySensor Entity"

    _attr_has_entity_name = True
    entity_description: EheimBinarySensorDescription

    def __init__(
        self,
        coordinator: EheimDigitalDataUpdateCoordinator,
        description: EheimBinarySensorDescription,
        device: EheimDevice,
        device_data: dict[str, Any],
    ) -> None:
        """Initialize the BinarySensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._sensor_data = coordinator.data[device.mac]
        self._device = device
        LOGGER.debug(
            "Initializing Eheim BinarySensor for Device: %s Entity: %s",
            self._device.mac,
            self.entity_description.key,
        )

    @property
    def is_on(self) -> bool:
        """Return True if the binary sensor is on."""
        return bool(self.entity_description.value_fn(self._sensor_data))

    @property
    def unique_id(self) -> str:
        """Return the unique ID for this binary sensor."""
        return f"{self._device.model.lower().replace(' ', '_')}_{format_mac(self._device.mac).replace(':','_')}_{self.entity_description.key}"

    @callback
    def _handle_coordinator_update(self) -> None:
        "Handle updated data from the coordinator." ""
        self._sensor_data = self.coordinator.data[self._device.mac]
        self.async_write_ha_state()

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._device.mac)},
            "name": self._device.name,
            "manufacturer": "Eheim",
            "model": self._device.model,
        }


def _get_binary_sensor_data(sensors: dict[str, Any], mac_address: str) -> Any:
    """Get the binary sensor data for a sensor type."""
    if sensors is None:
        LOGGER.warning(
            "Binary sensor data is None when trying to fetch %s", mac_address
        )
        return None

    # Form the key using device_type and mac_address
    key = mac_address

    data = sensors.get(key)
    if data is None:
        LOGGER.warning("No data found for key: %s", key)
    else:
        LOGGER.debug("Received binary sensor data for %s: %s", key, data)
    return data
