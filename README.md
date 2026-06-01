# Dometic CFX3 WiFi integration for Home Assistant

[![Validate](https://github.com/JS-DE-Tech/hacs-dometic-cfx3/actions/workflows/validate.yml/badge.svg)](https://github.com/JS-DE-Tech/hacs-dometic-cfx3/actions/workflows/validate.yml)

Home Assistant custom integration for Dometic CFX3 coolers. The integration communicates directly with the cooler over the local network using the DDMP protocol on TCP port `13142`. It does not use a cloud service and does not add external Python dependencies.

## Features

- Local-only communication with a Dometic CFX3 cooler
- Automatic discovery within a configurable IPv4 network or manual setup by IP address
- Automatic rediscovery by device name after an IP address change when a discovery network is configured
- Cooler power control and target-temperature control
- Battery-protection mode selection
- Sensors for temperatures, battery voltage, power source, device name, IP address, and the last successful communication
- Binary sensors for cooler power and compressor state
- Configurable polling interval between 60 and 360 seconds
- Local integration icon and logo for Home Assistant 2026.3 and newer

## Requirements

- Home Assistant `2025.1.0` or newer
- A Dometic CFX3 cooler reachable from Home Assistant over the local network
- TCP port `13142` reachable from Home Assistant to the cooler

The integration has no cloud dependency. If network segmentation or firewall rules are in use, allow Home Assistant to initiate TCP connections to the cooler on port `13142`.

## Installation with HACS as a custom repository

This repository can be installed through [HACS](https://www.hacs.xyz/) as a custom integration repository:

1. Open HACS in Home Assistant.
2. Open the menu in the top-right corner and select **Custom repositories**.
3. Enter `https://github.com/JS-DE-Tech/hacs-dometic-cfx3` as the repository URL.
4. Select **Integration** as the category and add the repository.
5. Search for **Dometic CFX3 WiFi** in HACS and download it.
6. Restart Home Assistant.
7. Open **Settings > Devices & services**, select **Add integration**, and search for **Dometic CFX3**.

## Manual installation

1. Download or clone this repository.
2. Copy the directory `custom_components/dometic_cfx3` into the `custom_components` directory inside your Home Assistant configuration directory.
3. Verify that the resulting path is:

   ```text
   <home-assistant-config>/custom_components/dometic_cfx3/manifest.json
   ```

4. Restart Home Assistant.
5. Open **Settings > Devices & services**, select **Add integration**, and search for **Dometic CFX3**.

## Configuration

The setup flow supports two modes:

- **Network scan:** Enter an IPv4 network in CIDR notation. The default is `10.100.3.0/24`. The integration probes devices locally on TCP port `13142` and asks you to select a cooler when it finds more than one.
- **Manual setup:** Disable network scanning and enter the cooler's IP address. The default TCP port remains `13142`.

After setup, the polling interval can be changed through the integration options or through the polling-interval configuration entity. The supported range is 60 to 360 seconds.

## Entities

| Platform | Entity | Purpose |
| --- | --- | --- |
| Climate | Cooling | Power and target-temperature control |
| Switch | Cooler on/off | Explicit cooler power control |
| Select | Battery protection | Battery-protection mode selection |
| Number | Polling interval | Polling interval configuration |
| Binary sensor | Cooler status | Cooler power state |
| Binary sensor | Compressor status | Compressor running state |
| Sensor | Current temperature | Measured temperature |
| Sensor | Target temperature | Configured target temperature |
| Sensor | Battery voltage | Measured battery voltage |
| Sensor | Power source | Current power source |
| Sensor | Device name | Cooler-reported device name |
| Sensor | IP address | Current cooler address |
| Sensor | Last communication | Time of the last successful update |

Every entity has a stable unique ID derived from the Home Assistant config entry and is attached to the Dometic CFX3 device.

## Brand images

Home Assistant 2026.3 and newer can load custom-integration brand images directly from `custom_components/dometic_cfx3/brand/`. This repository includes the supported files:

```text
custom_components/dometic_cfx3/brand/icon.png
custom_components/dometic_cfx3/brand/logo.png
```

No copy into Home Assistant's `www` directory is needed.

## Release

The integration manifest is prepared for release `v1.0.0`. For HACS release selection, publish a GitHub release with the tag `v1.0.0` after the validation workflow succeeds.

## Support

Please report problems through the [GitHub issue tracker](https://github.com/JS-DE-Tech/hacs-dometic-cfx3/issues). Include your Home Assistant version, cooler model, configuration mode (scan or manual), and relevant log messages.
