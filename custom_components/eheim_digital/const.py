"""Constants for eheim_digital."""
from logging import Logger, getLogger
LOGGER: Logger = getLogger(__package__)

NAME = "EHEIM Digital"
DOMAIN = "eheim_digital"
VERSION = "0.0.1"
UPDATE_INTERVAL = 900
PLATFORMS = ["light", "filter_pump"] #["sensor", "binary_sensor", "light"]

REQUEST_MESSAGES = {
    #"filter_pump": {"GET_FILTER_DATA"},
    #"heater": {"GET_EHEATER_DATA"},
    "led_control": {"REQ_CCV"} #"GET_ACCL", "GET_DYCL", "GET_MOON", "GET_CLOUD", "GET_DSCRPTN"},
    # "led_control": {"REQ_CCV", "GET_ACCL", "GET_DYCL", "GET_MOON", "GET_CLOUD", "GET_DSCRPTN"},
    #"ph_control": {"GET_PH_DATA"}
}

DEVICE_TYPES = {
    "filter_pump": {"name": "Filter", "icon": "mdi:filter"},
    "heater": {"name": "Heater", "icon": "mdi:thermometer"},
    "led_control": {"name": "LED Control", "icon": "mdi:led-strip-variant"},
    "ph_control": {"name": "pH Control", "icon": "mdi:water"}
}

DEVICE_VERSIONS = {
    0: "VERSION_UNDEFINED",
    1: "VERSION_HC",
    2: "VERSION_HC_PLUS",
    3: "VERSION_EHEIM_LIGHT",
    4: "VERSION_EHEIM_EXT_FILTER",
    5: "VERSION_EHEIM_EXT_HEATER",
    6: "VERSION_EHEIM_FEEDER",
    7: "VERSION_EHEIM_CHILLER",
    8: "VERSION_EHEIM_LIGHT_AQUAKIDS",
    9: "VERSION_EHEIM_PH_CONTROL",
    10: "VERSION_EHEIM_STREAM_CONTROL",
    11: "VERSION_EHEIM_REEFLEX",
    12: "VERSION_EHEIM_80_FILTER_WITH_HEAT",
    13: "VERSION_EHEIM_80_FILTER_WITHOUT_HEAT",
    14: "VERSION_EHEIM_DOSING_PUMP",
    15: "VERSION_EHEIM_LED_CTRL_PLUS_E",
    16: "VERSION_EHEIM_RGB_CTRL_PLUS_E",
    17: "VERSION_EHEIM_CLASSIC_LED_CTRL_PLUS_E",
    18: "VERSION_EHEIM_CLASSIC_VARIO",
}
DEVICE_GROUPS = {
    "FILTER_PUMP": [DEVICE_VERSIONS[1], DEVICE_VERSIONS[2], DEVICE_VERSIONS[4], DEVICE_VERSIONS[11]],
    "LIGHTING": [DEVICE_VERSIONS[3], DEVICE_VERSIONS[8], DEVICE_VERSIONS[15], DEVICE_VERSIONS[16], DEVICE_VERSIONS[17]],
    "HEATING": [DEVICE_VERSIONS[5], DEVICE_VERSIONS[12], DEVICE_VERSIONS[13]],
    "OTHER": [DEVICE_VERSIONS[0], DEVICE_VERSIONS[6], DEVICE_VERSIONS[7], DEVICE_VERSIONS[9], DEVICE_VERSIONS[10], DEVICE_VERSIONS[14], DEVICE_VERSIONS[18]]
}

# Cansiter filter pump modes
FILTER_PUMP_MODES = {
    "PM_NORMAL": 1,
    "PM_AUTOOFF": 2,
    "PM_NACHT": 4,
    "PM_PULS": 8,
    "PM_REGLOFF":  16,
    "PM_PROGMODE": 32,
    "PM_EXTERNAL": 16,
    "PM_HIDE_DSP": 128,
    "PM_ROTOR_ERR": 512,
    "PM_AIR_ERR": 768,
    "PM_TEMP_ERR": 1280,
    "PM_CAL_RECALC": 8192,
    "PM_CALIBRATION": 16384,
    "PM_RESET": 32768
}