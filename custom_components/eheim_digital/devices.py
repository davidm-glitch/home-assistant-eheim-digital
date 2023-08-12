"""EHEIM Device representation."""
from .const import LOGGER, DEVICE_VERSIONS, DEVICE_GROUPS

class EheimDevice:
    """EHEIM Device representation."""

    def __init__(self, data: dict) -> None:
        """EHEIM Device initialization."""
        self._title = data.get("title")
        self._from_mac = data.get("from")
        self._name = data.get("name")
        self._aq_name = data.get("aqName")
        self._mode = data.get("mode")  # Optional
        self._version = data.get("version")
        self._language = data.get("language")
        self._timezone = data.get("timezone")
        self._tank_id = data.get("tID")
        self._dst = data.get("dst")
        self._tank_config = data.get("tankconfig")
        self._power = data.get("power")
        self._net_mode = data.get("netmode")
        self._host = data.get("host")
        self._group_id = data.get("groupID")
        self._meshing = data.get("meshing")
        self._first_start = data.get("firstStart")
        self._remote = data.get("remote")  # Optional
        self._revision = data.get("revision")
        self._latest_available_revision = data.get("latestAvailableRevision")
        self._firmware_available = data.get("firmwareAvailable")
        self._email_address = data.get("emailAddr")
        self._live_time = data.get("liveTime")
        self._user_name = data.get("usrName")
        self._unit = data.get("unit")
        self._demo_use = data.get("demoUse")
        self._sys_led = data.get("sysLED")  # Optional


        LOGGER.debug("DEVICES: EheimDevice %s: with MAC: %s initialized", self._name, self._from_mac)

    @property
    def name(self):
        """Return the name of the device."""
        return f"EHEIM {self._name} {self.from_mac}"

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self.from_mac

    @property
    def title(self) -> str:
        """Title of the device response."""
        return self._title

    @property
    def from_mac(self) -> str:
        """MAC address of the device."""
        return self._from_mac

    @property
    def device_name(self) -> str:
        """Name of the device."""
        return self._name

    @property
    def aq_name(self) -> str:
        """Name of the aquarium associated with the device."""
        return self._aq_name

    @property
    def mode(self) -> str:
        """Mode of the device (specific to LED Control)."""
        return self._mode

    @property
    def version(self) -> int:
        """Version information for the device."""
        return self._version

    @property
    def language(self) -> str:
        """Language setting of the device."""
        return self._language

    @property
    def timezone(self) -> int:
        """Timezone setting of the device."""
        return self._timezone

    @property
    def tank_id(self) -> int:
        """Tank ID of the device."""
        return self._tank_id

    @property
    def dst(self) -> int:
        """Daylight Saving Time setting of the device."""
        return self._dst

    @property
    def tank_config(self) -> str:
        """Tank configuration information."""
        return self._tank_config

    @property
    def power(self) -> str:
        """Power information for the device."""
        return self._power

    @property
    def net_mode(self) -> str:
        """Network mode of the device."""
        return self._net_mode

    @property
    def host(self) -> str:
        """Host information for the device."""
        return self._host

    @property
    def group_id(self) -> int:
        """Group ID of the device."""
        return self._group_id

    @property
    def meshing(self) -> int:
        """Meshing information for the device."""
        return self._meshing

    @property
    def first_start(self) -> int:
        """First start information for the device."""
        return self._first_start

    @property
    def remote(self) -> int:
        """Remote information for the device."""
        return self._remote

    @property
    def revision(self) -> list:
        """Revision information for the device."""
        return self._revision

    @property
    def latest_available_revision(self) -> list:
        """Latest available revision information for the device."""
        return self._latest_available_revision

    @property
    def firmware_available(self) -> int:
        """Firmware availability information for the device."""
        return self._firmware_available

    @property
    def email_address(self) -> str:
        """Email address information for the device."""
        return self._email_address

    @property
    def live_time(self) -> int:
        """Live time information for the device."""
        return self._live_time

    @property
    def user_name(self) -> str:
        """User name information for the device."""
        return self._user_name

    @property
    def unit(self) -> int:
        """Unit information for the device."""
        return self._unit

    @property
    def demo_use(self) -> int:
        """Demo use information for the device."""
        return self._demo_use

    @property
    def sys_led(self) -> int:
        """System LED status for the device (specific to LED Control)."""
        return self._sys_led

    @property
    def device_type(self) -> str:
        """Return the device type."""
        if self._version in DEVICE_VERSIONS:
            return DEVICE_VERSIONS[self._version]
        return "DEVICE VERSION UNKNOWN"

    @property
    def device_group(self) -> str:
        """Return the device group."""
        for group, versions in DEVICE_GROUPS.items():
            if self.device_type in versions:
                return group
        return "DEVICE GROUP NOT FOUND"

    def __repr__(self):
        """String representation of the EheimDevice."""
        return f"EheimDevice(title={self._title}, name={self.name}, from_mac={self._from_mac})"


