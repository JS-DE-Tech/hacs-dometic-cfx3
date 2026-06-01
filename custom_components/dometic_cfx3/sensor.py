from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfElectricPotential, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_NAME, DOMAIN
from .coordinator import DometicCfx3Coordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    coordinator: DometicCfx3Coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        DometicCurrentTemperatureSensor(coordinator, entry),
        DometicTargetTemperatureSensor(coordinator, entry),
        DometicPowerSourceSensor(coordinator, entry),
        DometicBatteryVoltageSensor(coordinator, entry),
        DometicDeviceNameSensor(coordinator, entry),
        DometicIpAddressSensor(coordinator, entry),
        DometicLastCommunicationSensor(coordinator, entry),
    ])


class _BaseSensor(CoordinatorEntity[DometicCfx3Coordinator], SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator: DometicCfx3Coordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self.entry = entry

    @property
    def device_info(self) -> DeviceInfo:
        name = self.entry.data.get(CONF_NAME, "Dometic CFX3")
        return DeviceInfo(identifiers={(DOMAIN, name)}, name=name, manufacturer="Dometic", model="CFX3")


class DometicCurrentTemperatureSensor(_BaseSensor):
    _attr_translation_key = "current_temperature"
    _attr_icon = "mdi:thermometer"
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 0

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_current_temperature"

    @property
    def native_value(self):
        value = getattr(self.coordinator.data, "current_temperature", None)
        return None if value is None else round(value)


class DometicTargetTemperatureSensor(_BaseSensor):
    _attr_translation_key = "target_temperature"
    _attr_icon = "mdi:thermometer-check"
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 0

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_target_temperature"

    @property
    def native_value(self):
        value = getattr(self.coordinator.data, "target_temperature", None)
        return None if value is None else round(value)


class DometicBatteryVoltageSensor(_BaseSensor):
    _attr_translation_key = "battery_voltage"
    _attr_suggested_display_precision = 1
    _attr_device_class = SensorDeviceClass.VOLTAGE
    _attr_native_unit_of_measurement = UnitOfElectricPotential.VOLT
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_battery_voltage"

    @property
    def native_value(self):
        return getattr(self.coordinator.data, "battery_voltage", None)


class DometicPowerSourceSensor(_BaseSensor):
    _attr_translation_key = "power_source"
    _attr_icon = "mdi:power-plug"

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_power_source"

    @property
    def native_value(self):
        return getattr(self.coordinator.data, "power_source", None)


class DometicDeviceNameSensor(_BaseSensor):
    _attr_translation_key = "device_name"
    _attr_icon = "mdi:label-outline"

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_device_name"

    @property
    def native_value(self):
        return getattr(self.coordinator.data, "name", None)


class DometicIpAddressSensor(_BaseSensor):
    _attr_translation_key = "ip_address"
    _attr_icon = "mdi:ip-network"

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_ip_address"

    @property
    def native_value(self):
        return getattr(self.coordinator.data, "host", None)


class DometicLastCommunicationSensor(_BaseSensor):
    _attr_translation_key = "last_communication"
    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_icon = "mdi:clock-check-outline"

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_last_communication"

    @property
    def native_value(self):
        return getattr(self.coordinator.data, "last_communication", None)
