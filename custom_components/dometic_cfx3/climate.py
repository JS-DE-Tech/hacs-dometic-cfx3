from __future__ import annotations

from homeassistant.components.climate import ClimateEntity, ClimateEntityFeature, HVACMode
from homeassistant.const import UnitOfTemperature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_NAME, DOMAIN
from .coordinator import DometicCfx3Coordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    coordinator: DometicCfx3Coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([DometicCfx3Climate(coordinator, entry)])


class DometicCfx3Climate(CoordinatorEntity[DometicCfx3Coordinator], ClimateEntity):
    _attr_has_entity_name = True
    _attr_translation_key = "cooler"
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_min_temp = -22
    _attr_max_temp = 10
    _attr_target_temperature_step = 1
    _attr_hvac_modes = [HVACMode.OFF, HVACMode.COOL]
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.TURN_ON
        | ClimateEntityFeature.TURN_OFF
    )

    def __init__(self, coordinator: DometicCfx3Coordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self.entry = entry
        self._attr_unique_id = f"{entry.entry_id}_climate"

    @property
    def device_info(self) -> DeviceInfo:
        name = self.entry.data.get(CONF_NAME, "Dometic CFX3")
        return DeviceInfo(identifiers={(DOMAIN, name)}, name=name, manufacturer="Dometic", model="CFX3")

    @property
    def current_temperature(self):
        return getattr(self.coordinator.data, "current_temperature", None)

    @property
    def target_temperature(self):
        return getattr(self.coordinator.data, "target_temperature", None)

    @property
    def hvac_mode(self):
        if getattr(self.coordinator.data, "power", None) is False:
            return HVACMode.OFF
        return HVACMode.COOL

    async def async_set_temperature(self, **kwargs) -> None:
        temperature = kwargs.get("temperature")
        if temperature is not None:
            await self.coordinator.async_set_target_temperature(float(temperature))

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        await self.coordinator.async_set_power(hvac_mode != HVACMode.OFF)

    async def async_turn_on(self) -> None:
        await self.coordinator.async_set_power(True)

    async def async_turn_off(self) -> None:
        await self.coordinator.async_set_power(False)
