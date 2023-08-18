"""Platform for Sensor integration"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any
from datetime import datetime, timedelta


from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import format_mac
from homeassistant.util import dt as dt_util

from . import EheimDigitalDataUpdateCoordinator
from .devices import EheimDevice
from .const import LOGGER, DOMAIN


@dataclass
class EheimSensorDescriptionMixin:
    """Mixin for Eheim sensor."""

    value_fn: Callable[[dict[str, Any]], StateType]


@dataclass
class EheimSensorDescription(SensorEntityDescription, EheimSensorDescriptionMixin):
    """Class describing Eheim sensor entities."""

    attr_fn: Callable[[dict[str, Any]], dict[str, StateType]] = lambda _: {}


SENSOR_DESCRIPTIONS: tuple[EheimSensorDescription, ...] = (
    # Heater Sensors
    EheimSensorDescription(
        key="current_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        icon="mdi:thermometer",
        name="Current Temperature",
        entity_registry_enabled_default=True,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=lambda data: data.get("isTemp") / 10,
    ),
    EheimSensorDescription(
        key="target_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        icon="mdi:thermometer",
        name="Target Temperature",
        entity_registry_enabled_default=True,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=lambda data: data.get("sollTemp") / 10,
    ),
    # Filter Sensors
    EheimSensorDescription(
        key="operating_time",
        icon="mdi:timer",
        name="Operating Time",
        entity_registry_enabled_default=True,
        native_unit_of_measurement="days",
        value_fn=lambda data: int(data.get("actualTime") / 1440),
    ),
    EheimSensorDescription(
        key="night_mode_end_time",
        icon="mdi:clock-time-eight",
        name="Night Mode End Time",
        entity_registry_enabled_default=True,
        value_fn=lambda data: "{:02d}:{:02d}".format(
            *divmod(data.get("end_time_night_mode", 0), 60)
        ),
    ),
    EheimSensorDescription(
        key="night_mode_start_time",
        icon="mdi:clock-time-six",
        name="Night Mode Start Time",
        entity_registry_enabled_default=True,
        value_fn=lambda data: "{:02d}:{:02d}".format(
            *divmod(data.get("start_time_night_mode", 0), 60)
        ),
    ),
    EheimSensorDescription(
        key="current_speed",
        icon="mdi:speedometer",
        name="Current Speed",
        entity_registry_enabled_default=True,
        native_unit_of_measurement="%",
        value_fn=lambda data: int(
            data.get("freq") / data.get("maxFreqRglOff") * 100
            if data.get("maxFreqRglOff")
            else 0
        ),
    ),
    EheimSensorDescription(
        key="next_service",
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:wrench-clock",
        name="Next Service",
        entity_registry_enabled_default=True,
        value_fn=lambda data: (
            dt_util.utcnow() + timedelta(hours=data.get("serviceHour", 0))
        ),
    ),
    EheimSensorDescription(
        key="filter_turn_off_time",
        icon="mdi:timer",
        name="Filter Turn Off Time",
        entity_registry_enabled_default=True,
        native_unit_of_measurement="h",
        value_fn=lambda data: data.get("turnOffTime"),
    ),
    # LED Control Sensors
    EheimSensorDescription(
        key="ccv_brightness",
        icon="mdi:format-color-fill",
        name="Brightness",
        entity_registry_enabled_default=True,
        native_unit_of_measurement="%",
        value_fn=lambda data: sum(data["currentValues"]) / len(data["currentValues"]),
    ),
    EheimSensorDescription(
        key="ccv_brightness_white",
        icon="mdi:format-color-fill",
        name="White Brightness",
        entity_registry_enabled_default=True,
        native_unit_of_measurement="%",
        value_fn=lambda data: data.get("currentValues")[0],
    ),
    EheimSensorDescription(
        key="ccv_brightness_plants_gold",
        icon="mdi:format-color-fill",
        name="Plants Gold Brightness",
        entity_registry_enabled_default=True,
        native_unit_of_measurement="%",
        value_fn=lambda data: data.get("currentValues")[1],
    ),
    EheimSensorDescription(
        key="ccv_brightness_royal_blue",
        icon="mdi:format-color-fill",
        name="Royal Blue Brightness",
        entity_registry_enabled_default=True,
        native_unit_of_measurement="%",
        value_fn=lambda data: data.get("currentValues")[2],
    ),
    # PH Control Sensors
    EheimSensorDescription(
        key="ph_current_ph",
        icon="mdi:ph",
        name="Current PH",
        entity_registry_enabled_default=True,
        value_fn=lambda data: round((int(data["isPH"]) / 10), 1),
    ),
)

SENSOR_GROUPS = {
    "heater": ["current_temperature", "target_temperature"],
    "led_control": [
        "ccv_brightness",
        "ccv_brightness_white",
        "ccv_brightness_plants_gold",
        "ccv_brightness_royal_blue",
    ],
    "filter": [
        "operating_time",
        "night_mode_end_time",
        "night_mode_start_time",
        "current_speed",
        "next_service",
        "filter_turn_off_time",
        "filter_turn_off_time",
    ],
    "ph_control": ["ph_current_ph"],
    "other": [],
}


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Add EheimDevice entities from a config_entry."""
    LOGGER.debug("Setting up Eheim Digital Sensor platform")

    coordinator: EheimDigitalDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    sensors = []
    for device in coordinator.devices:
        device_group = device.device_group
        sensor_keys_for_group = SENSOR_GROUPS.get(device_group, [])

        device_data = _get_sensor_data(coordinator.data, device.mac)

        for description in SENSOR_DESCRIPTIONS:
            if description.key in sensor_keys_for_group:
                sensors.append(
                    EheimSensor(coordinator, description, device, device_data)
                )

    async_add_entities(sensors, True)


class EheimSensor(CoordinatorEntity[EheimDigitalDataUpdateCoordinator], SensorEntity):
    "Define an Eheim Sensor Entity"

    _attr_has_entity_name = True
    entity_description: EheimSensorDescription

    def __init__(
        self,
        coordinator: EheimDigitalDataUpdateCoordinator,
        description: EheimSensorDescription,
        device: EheimDevice,
        device_data: dict[str, Any],
    ) -> None:
        """Initialize the Sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._sensor_data = coordinator.data[device.mac]
        self._device = device
        LOGGER.debug(
            "Initializing Eheim Sensor for Device: %s Entity: %s",
            self._device.mac,
            self.entity_description.key,
        )

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        return self.entity_description.value_fn(self._sensor_data)

    @property
    def unique_id(self) -> str:
        """Return the unique ID for this sensor."""
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


def _get_sensor_data(sensors: dict[str, Any], mac_address: str) -> Any:
    """Get the sensor data for a sensor type."""
    if sensors is None:
        LOGGER.warning("Sensor data is None when trying to fetch %s", mac_address)
        return None

    # Form the key using device_type and mac_address
    key = mac_address

    data = sensors.get(key)
    if data is None:
        LOGGER.warning("No data found for key: %s", key)
    else:
        LOGGER.debug("Received sensor data for %s: %s", key, data)
    return data
