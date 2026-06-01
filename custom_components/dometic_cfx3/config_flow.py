from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback

from .api import DometicCfx3Client, DometicCfx3Error, discover_devices, probe_host
from .const import (
    CONF_HOST,
    CONF_NAME,
    CONF_NETWORK,
    CONF_PORT,
    CONF_USE_SCAN,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_SCAN_NETWORK,
    CONF_SCAN_INTERVAL,
    DOMAIN,
)


class DometicCfx3ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return DometicCfx3OptionsFlow(config_entry)

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            use_scan = user_input.get(CONF_USE_SCAN, True)
            network = user_input.get(CONF_NETWORK, DEFAULT_SCAN_NETWORK).strip()
            host = user_input.get(CONF_HOST, "").strip()
            port = int(user_input.get(CONF_PORT, DEFAULT_PORT))

            if use_scan:
                devices = await self.hass.async_add_executor_job(discover_devices, network, port)
                if not devices:
                    errors["base"] = "no_devices_found"
                elif len(devices) == 1:
                    device = devices[0]
                    return await self._create_entry(device["host"], port, device["name"], network)
                else:
                    self._discovered_devices = devices
                    self._discovered_network = network
                    self._discovered_port = port
                    return await self.async_step_select_device()
            else:
                if not host:
                    errors[CONF_HOST] = "host_required"
                else:
                    device = await self.hass.async_add_executor_job(probe_host, host, port)
                    if not device:
                        errors["base"] = "cannot_connect"
                    else:
                        return await self._create_entry(device["host"], port, device["name"], network)

        schema = vol.Schema(
            {
                vol.Required(CONF_USE_SCAN, default=True): bool,
                vol.Optional(CONF_NETWORK, default=DEFAULT_SCAN_NETWORK): str,
                vol.Optional(CONF_HOST, default=""): str,
                vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_select_device(self, user_input=None):
        errors = {}
        devices = getattr(self, "_discovered_devices", [])
        if user_input is not None:
            selected = user_input["device"]
            for device in devices:
                key = f"{device['name']}|{device['host']}"
                if key == selected:
                    return await self._create_entry(
                        device["host"],
                        getattr(self, "_discovered_port", DEFAULT_PORT),
                        device["name"],
                        getattr(self, "_discovered_network", DEFAULT_SCAN_NETWORK),
                    )
            errors["base"] = "unknown"

        options = {f"{d['name']}|{d['host']}": f"{d['name']} ({d['host']})" for d in devices}
        return self.async_show_form(
            step_id="select_device",
            data_schema=vol.Schema({vol.Required("device"): vol.In(options)}),
            errors=errors,
        )

    async def _create_entry(self, host: str, port: int, name: str, network: str):
        await self.async_set_unique_id(name)
        self._abort_if_unique_id_configured(updates={CONF_HOST: host, CONF_PORT: port, CONF_NETWORK: network})
        return self.async_create_entry(
            title=name,
            data={CONF_HOST: host, CONF_PORT: port, CONF_NAME: name, CONF_NETWORK: network},
        )


class DometicCfx3OptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_interval = int(self.config_entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL))
        schema = vol.Schema({
            vol.Required(CONF_SCAN_INTERVAL, default=current_interval): vol.All(vol.Coerce(int), vol.Range(min=60, max=360)),
        })
        return self.async_show_form(step_id="init", data_schema=schema)
