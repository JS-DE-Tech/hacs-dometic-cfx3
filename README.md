# Dometic CFX3 WiFi Integration for Home Assistant

[![Validate](https://github.com/JS-DE-Tech/hacs-dometic-cfx3/actions/workflows/validate.yml/badge.svg)](https://github.com/JS-DE-Tech/hacs-dometic-cfx3/actions/workflows/validate.yml)

This custom Home Assistant integration allows you to connect Dometic CFX3 WiFi coolers (such as the CFX3 35, CFX3 45, CFX3 55 and related models) directly to Home Assistant using the local DDMP protocol.

The integration communicates locally over your network and does not require any cloud services, internet access or third-party accounts.

## Features

- Local WiFi communication
- No cloud dependency
- Monitor actual temperature
- Monitor target temperature
- Monitor battery voltage
- Detect power source (AC / DC)
- Monitor compressor status
- Monitor cooler power status
- Configure battery protection mode
- Turn cooler on or off
- Config Flow setup
- HACS compatible
- German and English translations

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
