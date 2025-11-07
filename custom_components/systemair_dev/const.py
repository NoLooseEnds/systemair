"""Constants for Systemair."""

from enum import Enum
from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "systemair_dev"
ATTRIBUTION = "Data provided by Systemair SAVE Connect."

MAX_TEMP = 30
MIN_TEMP = 12

PRESET_MODE_AUTO = "auto"
PRESET_MODE_MANUAL = "manual"
PRESET_MODE_CROWDED = "crowded"
PRESET_MODE_REFRESH = "refresh"
PRESET_MODE_FIREPLACE = "fireplace"
PRESET_MODE_AWAY = "away"
PRESET_MODE_HOLIDAY = "holiday"


class SystemairModel(str, Enum):
    """Systemair ventilation unit models."""

    VTR300 = "VTR-300"
    VTR500 = "VTR-500"
    VSR300 = "VSR-300"
    UNKNOWN = "Unknown"

    @classmethod
    def from_string(cls, model_string: str | None) -> "SystemairModel":
        """Convert model string to SystemairModel enum."""
        if not model_string:
            return cls.UNKNOWN

        model_upper = model_string.upper()
        for model in cls:
            if model.value.upper() == model_upper:
                return model

        # Try partial matches
        if "VTR-300" in model_string or "VTR300" in model_upper:
            return cls.VTR300
        if "VTR-500" in model_string or "VTR500" in model_upper:
            return cls.VTR500
        if "VSR-300" in model_string or "VSR300" in model_upper:
            return cls.VSR300

        LOGGER.warning("Unknown Systemair model: %s", model_string)
        return cls.UNKNOWN
