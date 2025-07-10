from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import FAN_OFF, ClimateEntityFeature, HVACAction, HVACMode
from homeassistant.helpers.entity import DeviceInfo
from .const import DOMAIN
from typing import Any
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.const import UnitOfTemperature

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback
) -> None:
    hub = hass.data[DOMAIN][config_entry.entry_id]

    new_devices = []
    for thermostat in hub.cync_thermostats:
        if not hub.cync_thermostats[thermostat]._update_callback and thermostat in config_entry.options["climate_control"]:
            new_devices.append(CyncThermostatEntity(hub.cync_thermostats[thermostat]))

    if new_devices:
        async_add_entities(new_devices)


class CyncThermostatEntity(ClimateEntity):
    """Representation of a Cync Thermostat Entity."""

    should_poll = False

    def __init__(self, thermostat) -> None:
        """Initialize ThermostatEntity."""
        self.cync_thermostat = thermostat
        self._device = thermostat
        self._device_info = self.device_info
        # The API "name" field is a unique device identifier.
        self._attr_unique_id = thermostat.name
        self._attr_device_info = self.device_info
        self._attr_temperature_unit = UnitOfTemperature.FAHRENHEIT
        self._attr_hvac_modes = []

    async def async_added_to_hass(self) -> None:
        """Run when this Entity has been added to HA."""
        self.cync_thermostat.register(self.schedule_update_ha_state)

    async def async_will_remove_from_hass(self) -> None:
        """Entity being removed from hass."""
        self.cync_thermostat.reset()

    @property
    def device_info(self) -> DeviceInfo:
        """Return device registry information for this entity."""
        return DeviceInfo(
            identifiers = {(DOMAIN, f"{self.cync_thermostat.name} ({self.cync_thermostat.home_name})")},
            manufacturer = "Cync by Savant",
            name = f"{self.cync_thermostat.name} ({self.cync_thermostat.home_name})",
            suggested_area = f"{self.cync_thermostat.name}",
        )

    @property
    def unique_id(self) -> str:
        """Return Unique ID string."""
        return 'cync_switch_' + self.cync_thermostat.device_id

    @property
    def available(self) -> bool:
        """Return device availability."""
        return True

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        # if TemperatureTrait.NAME not in self._device.traits:
        #     return None
        # trait: TemperatureTrait = self._device.traits[TemperatureTrait.NAME]
        return self.cync_thermostat.temperature

    @property
    def current_humidity(self) -> float | None:
        """Return the current humidity."""
        # if HumidityTrait.NAME not in self._device.traits:
        #     return None
        # trait: HumidityTrait = self._device.traits[HumidityTrait.NAME]
        return None

    @property
    def target_temperature(self) -> float | None:
        """Return the temperature currently set to be reached."""
        # if not (trait := self._target_temperature_trait):
        #     return None
        # if self.hvac_mode == HVACMode.HEAT:
        #     return trait.heat_celsius
        # if self.hvac_mode == HVACMode.COOL:
        #     return trait.cool_celsius
        return None

    @property
    def target_temperature_high(self) -> float | None:
        """Return the upper bound target temperature."""
        # if self.hvac_mode != HVACMode.HEAT_COOL:
        #     return None
        # if not (trait := self._target_temperature_trait):
        #     return None
        # return trait.cool_celsius
        return None

    @property
    def target_temperature_low(self) -> float | None:
        """Return the lower bound target temperature."""
        # if self.hvac_mode != HVACMode.HEAT_COOL:
        #     return None
        # if not (trait := self._target_temperature_trait):
        #     return None
        # return trait.heat_celsius
        return None

    @property
    def hvac_mode(self) -> HVACMode:
        """Return the current operation (e.g. heat, cool, idle). TODO."""
        hvac_mode = HVACMode.OFF
        # if ThermostatModeTrait.NAME in self._device.traits:
        #     trait = self._device.traits[ThermostatModeTrait.NAME]
        #     if trait.mode in THERMOSTAT_MODE_MAP:
        #         hvac_mode = THERMOSTAT_MODE_MAP[trait.mode]
        return hvac_mode

    @property
    def hvac_action(self) -> HVACAction | None:
        """Return the current HVAC action (heating, cooling). TODO."""
        # trait = self._device.traits[ThermostatHvacTrait.NAME]
        # if trait.status == "OFF" and self.hvac_mode != HVACMode.OFF:
        return HVACAction.IDLE
        # return THERMOSTAT_HVAC_STATUS_MAP.get(trait.status)

    @property
    def preset_mode(self) -> str:
        """TODO."""
        # if ThermostatEcoTrait.NAME in self._device.traits:
        #     trait = self._device.traits[ThermostatEcoTrait.NAME]
        #     return PRESET_MODE_MAP.get(trait.mode, PRESET_NONE)
        # return PRESET_NONE
        return ''

    @property
    def preset_modes(self) -> list[str]:
        """TODO."""
        # if ThermostatEcoTrait.NAME not in self._device.traits:
        #     return []
        # return [
        #     PRESET_MODE_MAP[mode]
        #     for mode in self._device.traits[ThermostatEcoTrait.NAME].available_modes
        #     if mode in PRESET_MODE_MAP
        # ]
        return []

    @property
    def fan_mode(self) -> str:
        """Return the current fan mode."""
        # if (
        #     self.supported_features & ClimateEntityFeature.FAN_MODE
        #     and FanTrait.NAME in self._device.traits
        # ):
        #     trait = self._device.traits[FanTrait.NAME]
        #     return FAN_MODE_MAP.get(trait.timer_mode, FAN_OFF)
        return FAN_OFF

    @property
    def fan_modes(self) -> list[str]:
        """Return the list of available fan modes."""
        # if (
        #     self.supported_features & ClimateEntityFeature.FAN_MODE
        #     and FanTrait.NAME in self._device.traits
        # ):
        #     return FAN_INV_MODES
        return []

    def _get_supported_features(self) -> ClimateEntityFeature:
        """Compute the bitmap of supported features from the current state."""
        features = ClimateEntityFeature.TURN_OFF | ClimateEntityFeature.TURN_ON
        if HVACMode.HEAT_COOL in self.hvac_modes:
            features |= ClimateEntityFeature.TARGET_TEMPERATURE_RANGE
        if HVACMode.HEAT in self.hvac_modes or HVACMode.COOL in self.hvac_modes:
            features |= ClimateEntityFeature.TARGET_TEMPERATURE
        # if ThermostatEcoTrait.NAME in self._device.traits:
        #     features |= ClimateEntityFeature.PRESET_MODE
        # if FanTrait.NAME in self._device.traits:
        #     # Fan trait may be present without actually support fan mode
        #     fan_trait = self._device.traits[FanTrait.NAME]
        #     if fan_trait.timer_mode is not None:
        #         features |= ClimateEntityFeature.FAN_MODE
        return features

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new target hvac mode."""
        # api_mode = THERMOSTAT_INV_MODE_MAP[hvac_mode]
        # trait = self._device.traits[ThermostatModeTrait.NAME]
        # try:
        #     await trait.set_mode(api_mode)
        # except ApiException as err:
        #     raise HomeAssistantError(
        #         f"Error setting {self.entity_id} HVAC mode to {hvac_mode}: {err}"
        #     ) from err

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """TODO."""
        # hvac_mode = self.hvac_mode
        # if kwargs.get(ATTR_HVAC_MODE) is not None:
        #     hvac_mode = kwargs[ATTR_HVAC_MODE]
        #     await self.async_set_hvac_mode(hvac_mode)
        # low_temp = kwargs.get(ATTR_TARGET_TEMP_LOW)
        # high_temp = kwargs.get(ATTR_TARGET_TEMP_HIGH)
        # temp = kwargs.get(ATTR_TEMPERATURE)
        # if ThermostatTemperatureSetpointTrait.NAME not in self._device.traits:
        #     raise HomeAssistantError(
        #         f"Error setting {self.entity_id} temperature to {kwargs}: "
        #         "Unable to find setpoint trait."
        #     )
        # trait = self._device.traits[ThermostatTemperatureSetpointTrait.NAME]
        # try:
        #     if self.preset_mode == PRESET_ECO or hvac_mode == HVACMode.HEAT_COOL:
        #         if low_temp and high_temp:
        #             if high_temp - low_temp < MIN_TEMP_RANGE:
        #                 # Ensure there is a minimum gap from the new temp. Pick
        #                 # the temp that is not changing as the one to move.
        #                 if abs(high_temp - self.target_temperature_high) < 0.01:
        #                     high_temp = low_temp + MIN_TEMP_RANGE
        #                 else:
        #                     low_temp = high_temp - MIN_TEMP_RANGE
        #             await trait.set_range(low_temp, high_temp)
        #     elif hvac_mode == HVACMode.COOL and temp:
        #         await trait.set_cool(temp)
        #     elif hvac_mode == HVACMode.HEAT and temp:
        #         await trait.set_heat(temp)
        # except ApiException as err:
        #     raise HomeAssistantError(
        #         f"Error setting {self.entity_id} temperature to {kwargs}: {err}"
        #     ) from err

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """TODO."""
        # if preset_mode not in self.preset_modes:
        #     raise ValueError(f"Unsupported preset_mode '{preset_mode}'")
        # if self.preset_mode == preset_mode:  # API doesn't like duplicate preset modes
        #     return
        # trait = self._device.traits[ThermostatEcoTrait.NAME]
        # try:
        #     await trait.set_mode(PRESET_INV_MODE_MAP[preset_mode])
        # except ApiException as err:
        #     raise HomeAssistantError(
        #         f"Error setting {self.entity_id} preset mode to {preset_mode}: {err}"
        #     ) from err

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        """TODO."""
        # if fan_mode not in self.fan_modes:
        #     raise ValueError(f"Unsupported fan_mode '{fan_mode}'")
        # if fan_mode == FAN_ON and self.hvac_mode == HVACMode.OFF:
        #     raise ValueError(
        #         "Cannot turn on fan, please set an HVAC mode (e.g. heat/cool) first"
        #     )
        # trait = self._device.traits[FanTrait.NAME]
        # duration = None
        # if fan_mode != FAN_OFF:
        #     duration = MAX_FAN_DURATION
        # try:
        #     await trait.set_timer(FAN_INV_MODE_MAP[fan_mode], duration=duration)
        # except ApiException as err:
        #     raise HomeAssistantError(
        #         f"Error setting {self.entity_id} fan mode to {fan_mode}: {err}"
        #     ) from err
