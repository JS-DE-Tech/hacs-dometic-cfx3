from __future__ import annotations

from datetime import timedelta
import ipaddress
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import DometicCfx3Client, DometicCfx3ConnectionError, discover_devices
from .const import CONF_HOST, CONF_NAME, CONF_NETWORK, CONF_PORT, CONF_SCAN_INTERVAL, DEFAULT_PORT, DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class DometicCfx3Coordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.entry = entry
        self.host: str = entry.data[CONF_HOST]
        self.port: int = entry.data.get(CONF_PORT, DEFAULT_PORT)
        self.expected_name: str | None = entry.data.get(CONF_NAME)
        self.network: str | None = entry.data.get(CONF_NETWORK)
        self.client = DometicCfx3Client(self.host, self.port)
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{entry.entry_id}",
            update_interval=timedelta(seconds=int(entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL))),
        )

    async def _async_update_data(self):
        try:
            return await self.hass.async_add_executor_job(self.client.read_status)
        except DometicCfx3ConnectionError as err:
            if self.expected_name and self.network:
                rediscovered = await self.hass.async_add_executor_job(
                    self._rediscover_by_name,
                    self.expected_name,
                    self.network,
                )
                if rediscovered:
                    _LOGGER.info("Dometic CFX3 %s moved from %s to %s", self.expected_name, self.host, rediscovered)
                    self.host = rediscovered
                    self.client = DometicCfx3Client(self.host, self.port)
                    try:
                        return await self.hass.async_add_executor_job(self.client.read_status)
                    except DometicCfx3ConnectionError as second_err:
                        raise UpdateFailed(str(second_err)) from second_err
            raise UpdateFailed(str(err)) from err
        except Exception as err:
            raise UpdateFailed(str(err)) from err

    def _rediscover_by_name(self, expected_name: str, network: str) -> str | None:
        for item in discover_devices(network, self.port):
            if item.get("name") == expected_name:
                return item.get("host")
        return None

    async def async_set_power(self, enabled: bool) -> None:
        await self.hass.async_add_executor_job(self.client.set_power, enabled)
        await self.async_request_refresh()

    async def async_set_target_temperature(self, temperature: float) -> None:
        await self.hass.async_add_executor_job(self.client.set_target_temperature, temperature)
        await self.async_request_refresh()

    async def async_set_battery_protection(self, option: str) -> None:
        from .const import BATTERY_PROTECTION_TO_VALUE

        await self.hass.async_add_executor_job(
            self.client.set_battery_protection,
            BATTERY_PROTECTION_TO_VALUE[option],
        )
        await self.async_request_refresh()

    async def async_set_scan_interval(self, seconds: int) -> None:
        seconds = max(60, min(360, int(seconds)))
        options = dict(self.entry.options)
        options[CONF_SCAN_INTERVAL] = seconds
        self.hass.config_entries.async_update_entry(self.entry, options=options)
        self.update_interval = timedelta(seconds=seconds)
        await self.async_request_refresh()
