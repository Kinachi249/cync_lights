from homeassistant.components.climate import ClimateEntity
from homeassistant.helpers.entity import DeviceInfo
from .const import DOMAIN
from typing import Any
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback
) -> None:
    hub = hass.data[DOMAIN][config_entry.entry_id]

    new_devices = []
    for thermostat in hub.cync_climate_control:
        if not hub.cync_climate_control[thermostat]._update_callback and thermostat in config_entry.options["climate_control"]:
            new_devices.append(CyncThermostatEntity(hub.cync_climate_control[thermostat]))

    if new_devices:
        async_add_entities(new_devices)


class CyncThermostatEntity(ClimateEntity):
    """Representation of a Cync Thermostat Entity."""

    should_poll = False

    def __init__(self, cync_switch) -> None:
        """Initialize the thermostat."""
        self.cync_switch = cync_switch

    async def async_added_to_hass(self) -> None:
        """Run when this Entity has been added to HA."""
        self.cync_switch.register(self.schedule_update_ha_state)

    async def async_will_remove_from_hass(self) -> None:
        """Entity being removed from hass."""
        self.cync_switch.reset()

    @property
    def device_info(self) -> DeviceInfo:
        """Return device registry information for this entity."""
        return DeviceInfo(
            identifiers = {(DOMAIN, f"{self.cync_switch.name} ({self.cync_switch.home_name})")},
            manufacturer = "Cync by Savant",
            name = f"{self.cync_switch.name} ({self.cync_switch.home_name})",
            suggested_area = f"{self.cync_switch.name}",
        )

    @property
    def unique_id(self) -> str:
        """Return Unique ID string."""
        return 'cync_switch_' + self.cync_switch.device_id
