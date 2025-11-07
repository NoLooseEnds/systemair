# Example Lovelace Dashboard Configuration

This is an example Lovelace dashboard configuration for the Systemair integration. You can customize it to fit your needs.

## Basic Entities Card

```yaml
type: entities
title: Systemair Ventilation
entities:
  - entity: climate.systemair_dev_ventilation_unit
    name: Ventilation Unit
  - entity: sensor.systemair_dev_outside_air_temperature
    name: Outside Temperature
  - entity: sensor.systemair_dev_supply_air_temperature
    name: Supply Temperature
  - entity: sensor.systemair_dev_extract_air_temperature
    name: Extract Temperature
  - entity: sensor.systemair_dev_extract_air_relative_humidity
    name: Humidity
  - entity: sensor.systemair_dev_recovery_rate
    name: Heat Recovery Rate
  - entity: sensor.systemair_dev_supply_air_flow_rate
    name: Supply Air Flow
  - entity: sensor.systemair_dev_exhaust_air_flow_rate
    name: Exhaust Air Flow
  - entity: sensor.systemair_dev_filter_remaining_time
    name: Filter Remaining Time
show_header_toggle: false
```

## Climate Card

```yaml
type: climate
entity: climate.systemair_dev_ventilation_unit
```

## Gauge Cards for Key Metrics

```yaml
type: gauge
entity: sensor.systemair_dev_recovery_rate
name: Heat Recovery
min: 0
max: 100
severity:
  green: 70
  yellow: 50
  red: 0
```

```yaml
type: gauge
entity: sensor.systemair_dev_supply_air_flow_rate
name: Supply Air Flow
min: 0
max: 300
```

## History Graph

```yaml
type: history-graph
title: Temperature History
entities:
  - sensor.systemair_dev_outside_air_temperature
  - sensor.systemair_dev_supply_air_temperature
  - sensor.systemair_dev_extract_air_temperature
hours_to_show: 24
refresh_interval: 60
```

## Countdown Timers Card

```yaml
type: entities
title: Mode Countdown Timers
entities:
  - entity: sensor.systemair_dev_countdown_away
    name: Away Mode
  - entity: sensor.systemair_dev_countdown_crowded
    name: Crowded Mode
  - entity: sensor.systemair_dev_countdown_refresh
    name: Refresh Mode
  - entity: sensor.systemair_dev_countdown_fireplace
    name: Fireplace Mode
  - entity: sensor.systemair_dev_countdown_holiday
    name: Holiday Mode
show_header_toggle: false
```

## Configuration Entities Card

```yaml
type: entities
title: Configuration
entities:
  - entity: number.systemair_dev_time_delay_holiday
    name: Holiday Duration
  - entity: number.systemair_dev_time_delay_away
    name: Away Duration
  - entity: number.systemair_dev_time_delay_crowded
    name: Crowded Duration
  - entity: number.systemair_dev_time_delay_refresh
    name: Refresh Duration
  - entity: number.systemair_dev_time_delay_fireplace
    name: Fireplace Duration
  - entity: number.systemair_dev_eco_heat_offset
    name: Eco Heat Offset
  - entity: number.systemair_dev_filter_replacement_period
    name: Filter Replacement Period
  - entity: number.systemair_dev_moisture_extraction_setpoint
    name: Moisture Extraction Setpoint
show_header_toggle: false
```

## Complete Dashboard Example

```yaml
title: Ventilation
path: ventilation
icon: mdi:air-filter
cards:
  - type: vertical-stack
    cards:
      - type: climate
        entity: climate.systemair_dev_ventilation_unit
      - type: horizontal-stack
        cards:
          - type: gauge
            entity: sensor.systemair_dev_recovery_rate
            name: Recovery Rate
            min: 0
            max: 100
          - type: gauge
            entity: sensor.systemair_dev_supply_air_flow_rate
            name: Supply Flow
            min: 0
            max: 300
          - type: gauge
            entity: sensor.systemair_dev_exhaust_air_flow_rate
            name: Exhaust Flow
            min: 0
            max: 300
      - type: history-graph
        title: Temperature History
        entities:
          - sensor.systemair_dev_outside_air_temperature
          - sensor.systemair_dev_supply_air_temperature
          - sensor.systemair_dev_extract_air_temperature
        hours_to_show: 24
      - type: entities
        title: Current Status
        entities:
          - entity: sensor.systemair_dev_outside_air_temperature
          - entity: sensor.systemair_dev_supply_air_temperature
          - entity: sensor.systemair_dev_extract_air_temperature
          - entity: sensor.systemair_dev_extract_air_relative_humidity
          - entity: sensor.systemair_dev_enhanced_mode_status
          - entity: sensor.systemair_dev_filter_remaining_time
```

## Notes

- Replace `systemair_dev` with your actual integration domain if different
- Entity IDs may vary based on your configuration entry name
- Customize colors, icons, and layouts to match your theme
- Consider using Mushroom Cards or button-card for more advanced UI customization

