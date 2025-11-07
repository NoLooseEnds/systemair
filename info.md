# Systemair Dev

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

_Enhanced integration for Systemair SAVE Connect 2 ventilation systems with advanced features._

## Features

- **Full Climate Control**: Control ventilation modes (Auto, Manual, Away, Crowded, Refresh, Fireplace, Holiday)
- **Comprehensive Sensors**: Temperature, humidity, fan speeds, flow rates, recovery rate, and more
- **Enhanced Mode Detection**: Detailed mode status combining multiple registers
- **Countdown Timers**: Real-time remaining time for active modes
- **Calculated Values**: Flow rates and heat recovery rate calculations
- **Configuration Options**: Adjustable time delays, eco offset, filter period, and moisture setpoints
- **Alarm Monitoring**: Status monitoring for system alarms
- **Model Detection**: Automatic model detection with graceful degradation for unsupported features

## Supported Models

- VTR-300
- VTR-500
- VSR-300
- Other Systemair models with Modbus support (with limited feature set)

## Installation

1. Install via HACS (this repository)
2. Restart Home Assistant
3. Add integration via Settings → Devices & Services → Add Integration
4. Enter your SAVE Connect IP address

## Configuration

Configuration is done entirely through the Home Assistant UI. No YAML configuration required.

## Requirements

- Systemair SAVE Connect 2 gateway
- Home Assistant 2024.8.0 or later
- Network connectivity to SAVE Connect

## Differences from Original Integration

This is a development fork with additional features:
- Enhanced mode detection
- Countdown timers for modes
- Calculated flow rates and recovery rate
- Additional configuration options
- Better error handling and model detection

## Support

For issues and feature requests, please use the [GitHub Issues][issues] page.

[releases-shield]: https://img.shields.io/github/release/NoLooseEnds/systemair.svg?style=for-the-badge
[releases]: https://github.com/NoLooseEnds/systemair/releases
[commits-shield]: https://img.shields.io/github/commit-activity/y/NoLooseEnds/systemair.svg?style=for-the-badge
[commits]: https://github.com/NoLooseEnds/systemair/commits/main
[license-shield]: https://img.shields.io/github/license/NoLooseEnds/systemair.svg?style=for-the-badge
[issues]: https://github.com/NoLooseEnds/systemair/issues

