"""DataUpdateCoordinator for Systemair."""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, Any

from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import (
    SystemairApiClientError,
)
from .const import DOMAIN, LOGGER, SystemairModel
from .modbus import IntegerType, parameter_map

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import SystemairConfigEntry
    from .modbus import ModbusParameter


class InvalidBooleanValueError(HomeAssistantError):
    """Exception raised for invalid boolean values."""

    def __init__(self) -> None:
        """Initialize."""
        super().__init__("Value must be a boolean")


# https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
class SystemairDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    config_entry: SystemairConfigEntry
    modbus_parameters: list[ModbusParameter]
    _model: SystemairModel | None = None
    _missing_registers: set[str]

    def __init__(
        self,
        hass: HomeAssistant,
    ) -> None:
        """Initialize."""
        super().__init__(
            hass=hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=10),
        )
        self.modbus_parameters = []
        self._missing_registers = set()

    @property
    def model(self) -> SystemairModel:
        """Get the detected Systemair model."""
        if self._model is None:
            model_string = self.config_entry.runtime_data.mb_model
            self._model = SystemairModel.from_string(model_string)
            LOGGER.info("Detected Systemair model: %s (from: %s)", self._model.value, model_string)
        return self._model

    def register_modbus_parameters(self, modbus_parameter: ModbusParameter) -> None:
        """Register a list of Modbus parameters to be updated."""
        if modbus_parameter not in self.modbus_parameters:
            self.modbus_parameters.append(modbus_parameter)

        if modbus_parameter.combine_with_32_bit:
            combine_with = next(
                (param for param in parameter_map.values() if param.register == modbus_parameter.combine_with_32_bit),
                None,
            )

            if combine_with and combine_with not in self.modbus_parameters:
                self.modbus_parameters.append(combine_with)

    def is_register_available(self, register: ModbusParameter) -> bool:
        """Check if a register is available in the current data."""
        if self.data is None:
            return False
        register_key = str(register.register - 1)
        return register_key in self.data

    def get_modbus_data(
        self,
        register: ModbusParameter,
        *,
        default: float | None = 0,
        log_missing: bool = True,
    ) -> float | None:
        """
        Get the data for a Modbus register.

        Args:
            register: The Modbus parameter to read
            default: Default value to return if register is missing (None to return None)
            log_missing: Whether to log a warning if register is missing (only logs once per register)

        Returns:
            The register value, or default/None if register is not available
        """
        self.register_modbus_parameters(register)
        
        if self.data is None:
            if log_missing and register.short not in self._missing_registers:
                LOGGER.warning(
                    "Register %s (%s) not available - data not yet loaded",
                    register.short,
                    register.register,
                )
                self._missing_registers.add(register.short)
            return default

        register_key = str(register.register - 1)
        value = self.data.get(register_key)

        if value is None:
            if log_missing and register.short not in self._missing_registers:
                LOGGER.debug(
                    "Register %s (%s) not available for model %s - may not be supported",
                    register.short,
                    register.register,
                    self.model.value,
                )
                self._missing_registers.add(register.short)
            return default

        if register.boolean:
            return value != 0
        
        value = int(value)

        if register.combine_with_32_bit:
            high_key = str(register.combine_with_32_bit - 1)
            high = self.data.get(high_key)
            if high is None:
                if log_missing and register.short not in self._missing_registers:
                    LOGGER.debug(
                        "Register %s (%s) high word not available for model %s",
                        register.short,
                        register.combine_with_32_bit,
                        self.model.value,
                    )
                    self._missing_registers.add(register.short)
                return default
            value += int(high) << 16

        if register.sig == IntegerType.INT and value > (1 << 15):
            value = -(65536 - value)
        return value / (register.scale_factor or 1)

    async def set_modbus_data(self, register: ModbusParameter, value: Any) -> None:
        """Set the data for a Modbus register."""
        if register.boolean:
            if not isinstance(value, bool):
                raise InvalidBooleanValueError
            value = 1 if value else 0
            return await self.config_entry.runtime_data.client.async_set_data(register, value)

        value = int(value)
        value = value * (register.scale_factor or 1)
        if register.min_value is not None and value < register.min_value:
            value = register.min_value
        if register.max_value is not None and value > register.max_value:
            value = register.max_value

        return await self.config_entry.runtime_data.client.async_set_data(register, value)

    async def _async_setup(self) -> None:
        """Set up the coordinator."""
        menu = await self.config_entry.runtime_data.client.async_get_endpoint("menu")
        unit_version = await self.config_entry.runtime_data.client.async_get_endpoint("unit_version")
        self.config_entry.runtime_data.mac_address = menu["mac"]
        self.config_entry.runtime_data.serial_number = unit_version["System Serial Number"]
        self.config_entry.runtime_data.mb_hw_version = unit_version["MB HW version"]
        self.config_entry.runtime_data.mb_model = unit_version["MB Model"]
        self.config_entry.runtime_data.mb_sw_version = unit_version["MB SW version"]
        self.config_entry.runtime_data.iam_sw_version = unit_version["IAM SW version"]

        # Initialize model detection
        _ = self.model  # This will log the detected model

        # Required for setup of climate entity
        self.register_modbus_parameters(parameter_map["REG_FUNCTION_ACTIVE_HEATER"])
        self.register_modbus_parameters(parameter_map["REG_FUNCTION_ACTIVE_COOLER"])
        self.data = await self._async_update_data()

    async def _async_update_data(self) -> Any:
        """Update data via library."""
        try:
            return await self.config_entry.runtime_data.client.async_get_data(self.modbus_parameters)
        except SystemairApiClientError as exception:
            raise UpdateFailed(exception) from exception
