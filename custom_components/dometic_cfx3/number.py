from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_NAME, CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL, DOMAIN, ENTITY_PICTURE
from .coordinator import DometicCfx3Coordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    coordinator: DometicCfx3Coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([DometicScanIntervalNumber(coordinator, entry)])


class DometicScanIntervalNumber(CoordinatorEntity[DometicCfx3Coordinator], NumberEntity):
    _attr_has_entity_name = True
    _attr_name = "Abfrageintervall"
    _attr_icon = "mdi:timer-sync-outline"
    _attr_native_min_value = 60
    _attr_native_max_value = 360
    _attr_native_step = 10
    _attr_native_unit_of_measurement = UnitOfTime.SECONDS
    _attr_mode = NumberMode.BOX
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, coordinator: DometicCfx3Coordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self.entry = entry
        self._attr_unique_id = f"{entry.entry_id}_scan_interval"

    @property
    def device_info(self) -> DeviceInfo:
        name = self.entry.data.get(CONF_NAME, "Dometic CFX3")
        return DeviceInfo(identifiers={(DOMAIN, name)}, name=name, manufacturer="Dometic", model="CFX3")

    @property
    def entity_picture(self):
        return ENTITY_PICTURE

    @property
    def native_value(self):
        return int(self.entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL))

    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator.async_set_scan_interval(int(value))
