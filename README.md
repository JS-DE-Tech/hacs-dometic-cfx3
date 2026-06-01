# Dometic CFX3 WiFi

Local Home Assistant integration for Dometic CFX3 WiFi coolers with automatic discovery, temperature control and status monitoring.

## Overview

**Dometic CFX3 WiFi** connects Home Assistant directly to a compatible Dometic CFX3 cooler over the local network. The integration communicates with the cooler through the local DDMP TCP interface and does not require a cloud account or an external service.

## Features

- Local communication with compatible Dometic CFX3 WiFi coolers
- Automatic device discovery on a configurable IPv4 network
- Manual setup by IP address when network scanning is not desired
- Automatic rediscovery by device name if a discovered cooler receives a new IP address
- Cooler power control
- Current and target temperature monitoring
- Target temperature control from the Home Assistant climate entity
- Battery-protection level selection
- Battery voltage, power source and compressor status monitoring
- Configurable polling interval from 60 to 360 seconds

## Requirements

- Home Assistant **2025.1.0** or newer
- A compatible Dometic CFX3 cooler with WiFi connectivity
- Home Assistant and the cooler must be able to reach each other over the local network
- TCP port **13142** must be reachable from Home Assistant to the cooler

## Installation

### HACS custom repository

This integration can be installed as a [HACS](https://hacs.xyz/) custom repository:

1. Open **HACS** in Home Assistant.
2. Select **Integrations**.
3. Open the menu in the top-right corner and choose **Custom repositories**.
4. Add `https://github.com/JS-DE-Tech/hacs-dometic-cfx3` as the repository URL.
5. Select **Integration** as the category and add the repository.
6. Search for **Dometic CFX3 WiFi** in HACS and install it.
7. Restart Home Assistant.
8. Go to **Settings** → **Devices & services** → **Add integration** and select **Dometic CFX3**.

### Manual installation

1. Download or clone this repository.
2. Copy the `custom_components/dometic_cfx3` directory into the `custom_components` directory of your Home Assistant configuration:

   ```text
   <config>/custom_components/dometic_cfx3
   ```

3. Restart Home Assistant.
4. Go to **Settings** → **Devices & services** → **Add integration** and select **Dometic CFX3**.

## Configuration

The setup flow supports two connection methods:

- **Automatic discovery:** scans the configured IPv4 network for compatible coolers. The default network is `10.100.3.0/24`.
- **Manual connection:** connects directly to a specified cooler IP address.

The default DDMP TCP port is `13142`. If automatic discovery was used, the integration can search for the cooler again by device name if its IP address changes.

## Local communication and privacy

Communication stays on your local network. The integration connects directly from Home Assistant to the cooler using the local DDMP protocol over TCP port `13142`. No cloud account, cloud API or external relay service is required.

## Entities

The integration creates the following Home Assistant entities for each configured cooler:

| Platform | Entity | Purpose |
| --- | --- | --- |
| Climate | Kühlbetrieb | Turn cooling on or off and set the target temperature |
| Switch | Kühlbox Ein/Aus | Turn the cooler on or off |
| Binary sensor | Kühlbox-Status | Report whether the cooler is powered on |
| Binary sensor | Kompressor-Status | Report whether the compressor is running |
| Sensor | Ist-Temperatur | Show the current cooler temperature |
| Sensor | Soll-Temperatur | Show the configured target temperature |
| Sensor | Spannungsquelle | Show the active power source (AC or DC) |
| Sensor | Batteriespannung | Show the measured battery voltage |
| Sensor | Gerätename | Show the name reported by the cooler |
| Sensor | IP-Adresse | Show the current cooler IP address |
| Sensor | Letzte Kommunikation | Show the timestamp of the most recent successful communication |
| Select | Batteriewächter | Select the battery-protection level (`LOW`, `MED` or `HIGH`) |
| Number | Abfrageintervall | Configure the polling interval from 60 to 360 seconds |

## Network details

| Setting | Default | Description |
| --- | --- | --- |
| Protocol | DDMP over TCP | Local communication protocol used by the cooler |
| TCP port | `13142` | Port that must be reachable from Home Assistant to the cooler |
| Discovery network | `10.100.3.0/24` | Default IPv4 network scanned during automatic discovery |
| Polling interval | `60` seconds | Default status update interval; configurable from 60 to 360 seconds |

## Recommended GitHub/HACS repository description

> Local Home Assistant integration for Dometic CFX3 WiFi coolers with automatic discovery, temperature control and status monitoring.

## Support

Please report bugs and feature requests through the [GitHub issue tracker](https://github.com/JS-DE-Tech/hacs-dometic-cfx3/issues).
