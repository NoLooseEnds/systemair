"""Sensor platform for Systemair0."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.components.sensor.const import SensorDeviceClass, SensorStateClass
from homeassistant.const import PERCENTAGE, REVOLUTIONS_PER_MINUTE, EntityCategory, UnitOfTemperature, UnitOfTime

from .entity import SystemairEntity
from .modbus import ModbusParameter, alarm_parameters, parameter_map

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import SystemairDataUpdateCoordinator
    from .data import SystemairConfigEntry

ALARM_STATE_TO_VALUE_MAP = {
    "Inactive": 0,
    "Active": 1,
    "Waiting": 2,
    "Cleared Error Active": 3,
}

VALUE_MAP_TO_ALARM_STATE = {value: key for key, value in ALARM_STATE_TO_VALUE_MAP.items()}


@dataclass(kw_only=True, frozen=True)
class SystemairSensorEntityDescription(SensorEntityDescription):
    """Describes a Systemair sensor entity."""

    registry: ModbusParameter


ENTITY_DESCRIPTIONS = (
    SystemairSensorEntityDescription(
        key="outside_air_temperature",
        translation_key="outside_air_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        registry=parameter_map["REG_SENSOR_OAT"],
    ),
    SystemairSensorEntityDescription(
        key="extract_air_temperature",
        translation_key="extract_air_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        registry=parameter_map["REG_SENSOR_PDM_EAT_VALUE"],
    ),
    SystemairSensorEntityDescription(
        key="supply_air_temperature",
        translation_key="supply_air_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        registry=parameter_map["REG_SENSOR_SAT"],
    ),
    SystemairSensorEntityDescription(
        key="overheat_temperature",
        translation_key="overheat_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        registry=parameter_map["REG_SENSOR_OHT"],
    ),
    SystemairSensorEntityDescription(
        key="extract_air_relative_humidity",
        translation_key="extract_air_relative_humidity",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        registry=parameter_map["REG_SENSOR_RHS_PDM"],
    ),
    SystemairSensorEntityDescription(
        key="efficiency_temperature",
        translation_key="efficiency_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        registry=parameter_map["REG_SENSOR_EFFICIENCY_TEMP"],
    ),
    SystemairSensorEntityDescription(
        key="overheat_temperature_alt",
        translation_key="overheat_temperature_alt",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        registry=parameter_map["REG_SENSOR_OHT_ALT"],
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SystemairSensorEntityDescription(
        key="calculated_moisture_extraction",
        translation_key="calculated_moisture_extraction",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        registry=parameter_map["REG_SENSOR_CALC_MOISTURE_EXTRACTION"],
    ),
    SystemairSensorEntityDescription(
        key="calculated_moisture_intake",
        translation_key="calculated_moisture_intake",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        registry=parameter_map["REG_SENSOR_CALC_MOISTURE_INTAKE"],
    ),
    SystemairSensorEntityDescription(
        key="supply_air_fan_power_factor",
        translation_key="supply_air_fan_power_factor",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        registry=parameter_map["REG_OUTPUT_SAF_POWER_FACTOR"],
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SystemairSensorEntityDescription(
        key="mode_status_register",
        translation_key="mode_status_register",
        registry=parameter_map["REG_USERMODE_MODE"],
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SystemairSensorEntityDescription(
        key="manual_mode_command",
        translation_key="manual_mode_command",
        registry=parameter_map["REG_USERMODE_MANUAL_COMMAND"],
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SystemairSensorEntityDescription(
        key="enhanced_mode_status",
        translation_key="enhanced_mode_status",
        entity_category=EntityCategory.DIAGNOSTIC,
        registry=parameter_map["REG_USERMODE_MODE"],  # Use mode register as base, but we'll compute the value
    ),
    SystemairSensorEntityDescription(
        key="supply_air_flow_rate",
        translation_key="supply_air_flow_rate",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="m³/h",
        registry=parameter_map["REG_OUTPUT_SAF_POWER_FACTOR"],  # Base register, but we'll compute the value
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SystemairSensorEntityDescription(
        key="exhaust_air_flow_rate",
        translation_key="exhaust_air_flow_rate",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="m³/h",
        registry=parameter_map["REG_OUTPUT_EAF"],  # Base register, but we'll compute the value
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SystemairSensorEntityDescription(
        key="recovery_rate",
        translation_key="recovery_rate",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        registry=parameter_map["REG_SENSOR_SAT"],  # Base register, but we'll compute the value
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SystemairSensorEntityDescription(
        key="meter_saf_rpm",
        translation_key="meter_saf_rpm",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=REVOLUTIONS_PER_MINUTE,
        registry=parameter_map["REG_SENSOR_RPM_SAF"],
    ),
    SystemairSensorEntityDescription(
        key="meter_saf_reg_speed",
        translation_key="meter_saf_reg_speed",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        registry=parameter_map["REG_OUTPUT_SAF"],
    ),
    SystemairSensorEntityDescription(
        key="meter_eaf_rpm",
        translation_key="meter_eaf_rpm",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=REVOLUTIONS_PER_MINUTE,
        registry=parameter_map["REG_SENSOR_RPM_EAF"],
    ),
    SystemairSensorEntityDescription(
        key="meter_eaf_reg_speed",
        translation_key="meter_eaf_reg_speed",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        registry=parameter_map["REG_OUTPUT_EAF"],
    ),
    SystemairSensorEntityDescription(
        key="heater_output_value",
        translation_key="heater_output_value",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        registry=parameter_map["REG_PWM_TRIAC_OUTPUT"],
    ),
    SystemairSensorEntityDescription(
        key="filter_remaining_time",
        translation_key="filter_remaining_time",
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        registry=parameter_map["REG_FILTER_REMAINING_TIME_L"],
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    *(
        SystemairSensorEntityDescription(
            key=f"alarm_{param.short.lower()}",
            name=param.description,
            device_class=SensorDeviceClass.ENUM,
            options=["Inactive", "Active", "Waiting", "Cleared Error Active"],
            registry=param,
            entity_category=EntityCategory.DIAGNOSTIC,
        )
        for param in alarm_parameters.values()
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: SystemairConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    async_add_entities(
        SystemairSensor(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class SystemairSensor(SystemairEntity, SensorEntity):
    """Systemair Sensor class."""

    _attr_has_entity_name = True

    entity_description: SystemairSensorEntityDescription

    def __init__(
        self,
        coordinator: SystemairDataUpdateCoordinator,
        entity_description: SystemairSensorEntityDescription,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}-{entity_description.key}"

    @property
    def native_value(self) -> str | None:
        """Return the native value of the sensor."""
        # Enhanced mode status combines mode register with manual command register
        if self.entity_description.key == "enhanced_mode_status":
            return self._get_enhanced_mode_status()

        # Calculated flow rates
        if self.entity_description.key == "supply_air_flow_rate":
            return self._get_supply_air_flow_rate()

        if self.entity_description.key == "exhaust_air_flow_rate":
            return self._get_exhaust_air_flow_rate()

        # Calculated recovery rate
        if self.entity_description.key == "recovery_rate":
            return self._get_recovery_rate()

        value = self.coordinator.get_modbus_data(
            self.entity_description.registry,
            default=None,
            log_missing=True,
        )

        if value is None:
            return None

        if self.device_class == SensorDeviceClass.ENUM:
            value = int(value)
            return VALUE_MAP_TO_ALARM_STATE.get(value, "Inactive")

        return str(value)

    def _get_supply_air_flow_rate(self) -> str:
        """Calculate supply air flow rate from fan power factor."""
        power_factor = self.coordinator.get_modbus_data(
            parameter_map["REG_OUTPUT_SAF_POWER_FACTOR"],
            default=None,
            log_missing=False,
        )
        if power_factor is None:
            # Fallback to REG_OUTPUT_SAF if power factor not available
            power_factor = self.coordinator.get_modbus_data(
                parameter_map["REG_OUTPUT_SAF"],
                default=0,
                log_missing=False,
            )
        flow_rate = round(float(power_factor) * 3, 0)
        return str(int(flow_rate))

    def _get_exhaust_air_flow_rate(self) -> str:
        """Calculate exhaust air flow rate from fan power factor."""
        power_factor = self.coordinator.get_modbus_data(
            parameter_map["REG_OUTPUT_EAF"],
            default=0,
            log_missing=False,
        )
        flow_rate = round(float(power_factor) * 3, 0)
        return str(int(flow_rate))

    def _get_recovery_rate(self) -> str:
        """Calculate heat recovery rate from temperatures."""
        supply_temp = self.coordinator.get_modbus_data(
            parameter_map["REG_SENSOR_SAT"],
            default=None,
            log_missing=False,
        )
        outdoor_temp = self.coordinator.get_modbus_data(
            parameter_map["REG_SENSOR_OAT"],
            default=None,
            log_missing=False,
        )
        exhaust_temp = self.coordinator.get_modbus_data(
            parameter_map["REG_SENSOR_PDM_EAT_VALUE"],
            default=None,
            log_missing=False,
        )

        if supply_temp is None or outdoor_temp is None or exhaust_temp is None:
            return None

        # Avoid division by zero
        temp_diff = float(exhaust_temp) - float(outdoor_temp)
        if abs(temp_diff) < 0.1:
            return "0"

        recovery_rate = (
            ((float(supply_temp) - float(outdoor_temp)) / temp_diff) * 100
        )
        return str(round(recovery_rate, 1))

    def _get_enhanced_mode_status(self) -> str:
        """Get enhanced mode status by combining mode register with manual command register."""
        mode_register = self.coordinator.get_modbus_data(
            parameter_map["REG_USERMODE_MODE"],
            default=0,
            log_missing=False,
        )
        manual_command = self.coordinator.get_modbus_data(
            parameter_map["REG_USERMODE_MANUAL_COMMAND"],
            default=0,
            log_missing=False,
        )

        mode = int(mode_register)
        manual = int(manual_command)

        # Enhanced mode detection based on repo2_nonhacs logic
        if mode == 0:  # Auto mode
            if manual == 2:
                return "Auto schedule - Low"
            if manual == 3:
                return "Auto schedule - Normal"
            if manual == 4:
                return "Auto schedule - High"
            return "Auto schedule - Normal"
        if mode == 1:  # Manual mode
            if manual == 0:
                return "Manual STOP"
            if manual == 1:
                return "Manual Unknown"  # Shouldn't normally occur
            if manual == 2:
                return "Manual Low"
            if manual == 3:
                return "Manual Normal"
            if manual == 4:
                return "Manual High"
            return "Manual"
        if mode == 2:
            return "Crowded"
        if mode == 3:
            return "Refresh"
        if mode == 4:
            return "Fireplace"
        if mode == 5:
            return "Away"
        if mode == 6:
            return "Holiday"
        if mode == 7:
            return "Cooker Hood"
        if mode == 8:
            return "Vacuum Cleaner"
        if mode == 9:
            return "CDI1"
        if mode == 10:
            return "CDI2"
        if mode == 11:
            return "CDI3"
        if mode == 12:
            return "Pressure Guard"

        return f"Unknown ({mode})"
