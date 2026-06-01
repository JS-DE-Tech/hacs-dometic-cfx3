from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_NAME, DOMAIN
from .coordinator import DometicCfx3Coordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    coordinator: DometicCfx3Coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        DometicPowerBinarySensor(coordinator, entry),
        DometicCompressorBinarySensor(coordinator, entry),
    ])


class _BaseBinarySensor(CoordinatorEntity[DometicCfx3Coordinator], BinarySensorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator: DometicCfx3Coordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self.entry = entry

    @property
    def device_info(self) -> DeviceInfo:
        name = self.entry.data.get(CONF_NAME, "Dometic CFX3")
        return DeviceInfo(identifiers={(DOMAIN, name)}, name=name, manufacturer="Dometic", model="CFX3")


class DometicPowerBinarySensor(_BaseBinarySensor):
    _attr_translation_key = "power"
    _attr_device_class = BinarySensorDeviceClass.POWER

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_power"

    @property
    def is_on(self):
        return getattr(self.coordinator.data, "power", None)


class DometicCompressorBinarySensor(_BaseBinarySensor):
    _attr_translation_key = "compressor"
    _attr_device_class = BinarySensorDeviceClass.RUNNING

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_compressor"

    @property
    def is_on(self):
        return getattr(self.coordinator.data, "compressor", None)
