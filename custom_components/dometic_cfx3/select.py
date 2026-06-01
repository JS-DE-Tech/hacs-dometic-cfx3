from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import BATTERY_PROTECTION_OPTIONS, CONF_NAME, DOMAIN
from .coordinator import DometicCfx3Coordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    coordinator: DometicCfx3Coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([DometicBatteryProtectionSelect(coordinator, entry)])


class DometicBatteryProtectionSelect(CoordinatorEntity[DometicCfx3Coordinator], SelectEntity):
    _attr_has_entity_name = True
    _attr_translation_key = "battery_protection"
    _attr_icon = "mdi:car-battery"
    _attr_options = BATTERY_PROTECTION_OPTIONS

    def __init__(self, coordinator: DometicCfx3Coordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self.entry = entry
        self._attr_unique_id = f"{entry.entry_id}_battery_protection"

    @property
    def device_info(self) -> DeviceInfo:
        name = self.entry.data.get(CONF_NAME, "Dometic CFX3")
        return DeviceInfo(identifiers={(DOMAIN, name)}, name=name, manufacturer="Dometic", model="CFX3")

    @property
    def current_option(self):
        return getattr(self.coordinator.data, "battery_protection", None)

    async def async_select_option(self, option: str) -> None:
        await self.coordinator.async_set_battery_protection(option)
