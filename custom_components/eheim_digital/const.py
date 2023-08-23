"""Constants for eheim_digital."""
from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

NAME = "EHEIM Digital"
DOMAIN = "eheim_digital"
VERSION = "0.0.1"
UPDATE_INTERVAL = 30
PLATFORMS = ["sensor"]  # ["sensor", "binary_sensor", "light"]

DEVICE_TYPES = {
    "filter": {"name": "Filter", "icon": "mdi:filter"},
    "heater": {"name": "Heater", "icon": "mdi:thermometer"},
    "led_control": {"name": "LED Control", "icon": "mdi:led-strip-variant"},
    "ph_control": {"name": "pH Control", "icon": "mdi:water"},
}

DEVICE_VERSIONS = {
    0: "UNDEFINED",
    1: "HC",
    2: "HC_PLUS",
    3: "EHEIM_LIGHT",
    4: "EHEIM_EXT_FILTER",
    5: "EHEIM_EXT_HEATER",
    6: "EHEIM_FEEDER",
    7: "EHEIM_CHILLER",
    8: "EHEIM_LIGHT_AQUAKIDS",
    9: "EHEIM_PH_CONTROL",
    10: "EHEIM_STREAM_CONTROL",
    11: "EHEIM_REEFLEX",
    12: "EHEIM_80_FILTER_WITH_HEAT",
    13: "EHEIM_80_FILTER_WITHOUT_HEAT",
    14: "EHEIM_DOSING_PUMP",
    15: "EHEIM_LED_CTRL_PLUS_E",
    16: "EHEIM_RGB_CTRL_PLUS_E",
    17: "EHEIM_CLASSIC_LED_CTRL_PLUS_E",
    18: "EHEIM_CLASSIC_VARIO",
}
DEVICE_GROUPS = {
    "filter": [
        DEVICE_VERSIONS[1],
        DEVICE_VERSIONS[2],
        DEVICE_VERSIONS[4],
        DEVICE_VERSIONS[11],
    ],
    "led_control": [
        DEVICE_VERSIONS[3],
        DEVICE_VERSIONS[8],
        DEVICE_VERSIONS[15],
        DEVICE_VERSIONS[16],
        DEVICE_VERSIONS[17],
    ],
    "heater": [DEVICE_VERSIONS[5], DEVICE_VERSIONS[12], DEVICE_VERSIONS[13]],
    "ph_control": [DEVICE_VERSIONS[9]],
    "other": [
        DEVICE_VERSIONS[0],
        DEVICE_VERSIONS[6],
        DEVICE_VERSIONS[7],
        DEVICE_VERSIONS[10],
        DEVICE_VERSIONS[14],
        DEVICE_VERSIONS[18],
    ],
}

DEVICE_MODES = {
    "filter": FILTER_PUMP_MODES,
}

# Cansiter filter pump modes
FILTER_PUMP_MODES = {
    "PM_NORMAL": 1,
    "PM_AUTOOFF": 2,
    "PM_NACHT": 4,
    "PM_PULS": 8,
    "PM_REGLOFF": 16,
    "PM_PROGMODE": 32,
    "PM_EXTERNAL": 16,
    "PM_HIDE_DSP": 128,
    "PM_ROTOR_ERR": 512,
    "PM_AIR_ERR": 768,
    "PM_TEMP_ERR": 1280,
    "PM_CAL_RECALC": 8192,
    "PM_CALIBRATION": 16384,
    "PM_RESET": 32768,
}
