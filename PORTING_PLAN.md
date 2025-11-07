# Porting Plan: repo2_nonhacs → dev Integration

## Architecture Overview

### SAVE Connect Gateway
- **SAVE Connect** is a gateway device that translates HTTP REST API calls to Modbus RTU
- The `dev` integration communicates with SAVE Connect via HTTP (`/mread`, `/mwrite`, `/menu`, `/unit_version`)
- SAVE Connect handles the actual Modbus communication with the ventilation unit
- This is different from `repo2_nonhacs` which uses direct Modbus TCP (via Elfin EW11 converter)

### Model Detection
- Models are detected via `unit_version["MB Model"]` API endpoint during setup
- Available models: VTR-300, VTR-500, VSR-300 (and potentially others)
- Currently, the integration uses a **single unified register map** for all models
- **This needs to change** - different models may have different register addresses and available features

### Key Differences: repo2_nonhacs vs dev
1. **Communication Method**:
   - repo2_nonhacs: Direct Modbus TCP (via Elfin EW11 converter)
   - dev: HTTP API via SAVE Connect gateway

2. **Register Addressing**:
   - repo2_nonhacs: Uses Modbus addresses directly (may be 0-indexed or 1-indexed)
   - dev: Uses register numbers that SAVE Connect translates (register - 1 in API calls)
   - **Important**: Register address discrepancies may be due to:
     - Model differences (VTR-500 vs VTR-300 vs VSR-300)
     - Direct Modbus vs SAVE Connect API translation
     - Different firmware versions

---

## 1. Model-Specific Register Mapping Strategy

### 1.1 Create Model Registry System
**Priority: HIGH**

Create a model detection and register mapping system:

```python
# In modbus.py or new file models.py
from enum import Enum

class SystemairModel(Enum):
    VTR300 = "VTR-300"
    VTR500 = "VTR-500"
    VSR300 = "VSR-300"
    UNKNOWN = "Unknown"

# Model-specific parameter maps
MODEL_PARAMETER_MAPS = {
    SystemairModel.VTR300: {...},
    SystemairModel.VTR500: {...},
    SystemairModel.VSR300: {...},
}
```

**Implementation Steps**:
1. Extract model from `mb_model` field in `SystemairData`
2. Create model-specific parameter maps
3. Update `parameter_map` to be model-aware
4. Add fallback to common registers for unknown models

### 1.2 Register Address Verification
**Priority: HIGH**

The register discrepancies found need model-specific verification:

| Register Name | dev (current) | repo2_nonhacs | Likely Model | Notes |
|--------------|---------------|---------------|--------------|-------|
| Mode Status | 1161 (Input) | 1160 (Holding) | VTR-500 | May be model-specific |
| Temp Setpoint | 2001 | 2000 | VTR-500 | Verify for each model |
| Overheat Temp | 12108 | 12107 | VTR-500 | Different sensors? |
| Alarm A/B/C | 15901-15903 | 15900-15902 | VTR-500 | Offset difference |
| Filter Time | 7005/7006 (32-bit) | 7005/7006 (alarm) | VTR-500 | Different interpretation |

**Action Items**:
- Test register reads for each model (VTR-300, VTR-500, VSR-300)
- Document which registers exist on which models
- Create model-specific register maps
- Handle missing registers gracefully (some may not exist on all models)

---

## 2. Model-Specific Feature Support

### 2.1 Conditional Entity Creation
**Priority: HIGH**

Some features may only be available on certain models:

```python
# In sensor.py, switch.py, etc.
def should_create_entity(model: SystemairModel, register: ModbusParameter) -> bool:
    """Check if entity should be created for this model."""
    model_features = MODEL_FEATURES.get(model, set())
    return register.short in model_features
```

**Features to check**:
- Heater support (VTR-500 has heater, VSR-300 may not)
- Cooler support (model-dependent)
- Specific alarm types (may vary by model)
- Advanced features (eco mode, free cooling, etc.)

### 2.2 Model-Specific Sensor Lists
**Priority: MEDIUM**

Create model-specific sensor entity descriptions:

```python
# In sensor.py
def get_sensor_entities_for_model(model: SystemairModel) -> tuple:
    """Get sensor entities available for specific model."""
    base_sensors = BASE_SENSOR_ENTITIES
    model_specific = MODEL_SPECIFIC_SENSORS.get(model, [])
    return base_sensors + model_specific
```

---

## 3. Additional Sensor Registers to Add (Model-Aware)

### 3.1 Common Sensors (All Models)
These should work across all models:

- **Efficiency Temperature** (register 12106) - Verify per model
- **Calculated Moisture Extraction** (register 2210) - Verify per model
- **Calculated Moisture Intake** (register 2211) - Verify per model
- **Supply Air Fan Power Factor** (register 14000) - Verify per model
- **Extractor Fan Power Factor** (register 14001) - Verify per model
- **Heat Recovery** (register 14102) - Verify per model

### 3.2 VTR-500 Specific Sensors (from repo2_nonhacs)
These are likely VTR-500 specific:

- **Summer/Winter Operation** (register 1038)
- **Extractor Hood Pressure Switch** (register 12020)
- **TRIAC After Manual Override** (register 2148)
- **TRIAC Control Signal** (register 14380)
- **Manual Mode Command Register** (register 1130)
- **Exhaust Air Setpoint** (register 2012)
- **Exhaust Air Min/Max Setpoint** (registers 2020, 2021)
- **Temperature Control Mode** (register 2030)
- **Eco Heat Offset** (register 2503)
- **Fan Speed Compensation** registers (1251-1258)
- **Filter Replacement Period** (register 7000)
- **Moisture Extraction Setpoint** (register 2202)

**Implementation**: Add with model check - only create for VTR-500

### 3.3 VTR-300 / VSR-300 Specific Sensors
**Action**: Review documentation PDFs to identify model-specific registers
- May have different register addresses
- May have different feature sets
- May lack some VTR-500 features

---

## 4. Register Address Resolution Strategy

### 4.1 Unified Register Map with Model Overrides
**Priority: HIGH**

```python
# In modbus.py
COMMON_PARAMETERS = [
    # Registers that exist on all models with same address
    ModbusParameter(register=12102, ...),  # OAT - common
    ModbusParameter(register=12103, ...),  # SAT - common
    # ...
]

VTR500_SPECIFIC_PARAMETERS = [
    # VTR-500 specific registers
    ModbusParameter(register=1038, ...),   # Summer/Winter
    ModbusParameter(register=2503, ...),   # Eco offset
    # ...
]

VTR300_SPECIFIC_PARAMETERS = [
    # VTR-300 specific registers (to be determined from docs)
    # ...
]

VSR300_SPECIFIC_PARAMETERS = [
    # VSR-300 specific registers (to be determined from docs)
    # ...
]

def get_parameters_for_model(model: SystemairModel) -> dict:
    """Get parameter map for specific model."""
    params = COMMON_PARAMETERS.copy()
    if model == SystemairModel.VTR500:
        params.extend(VTR500_SPECIFIC_PARAMETERS)
    elif model == SystemairModel.VTR300:
        params.extend(VTR300_SPECIFIC_PARAMETERS)
    elif model == SystemairModel.VSR300:
        params.extend(VSR300_SPECIFIC_PARAMETERS)
    return {param.short: param for param in params}
```

### 4.2 Register Address Mapping Table
Create a mapping table to resolve discrepancies:

```python
# Register address mappings by model
REGISTER_MAPPINGS = {
    SystemairModel.VTR500: {
        "REG_USERMODE_MODE": 1160,  # repo2_nonhacs uses 1160
        "REG_TC_SP": 2000,          # repo2_nonhacs uses 2000
        # ...
    },
    SystemairModel.VTR300: {
        "REG_USERMODE_MODE": 1161,  # dev uses 1161
        "REG_TC_SP": 2001,          # dev uses 2001
        # ...
    },
    # ...
}
```

---

## 5. Enhanced Features to Port (Model-Aware)

### 5.1 Enhanced Mode Detection
**Priority: HIGH**

Combine mode status register with manual command register for detailed status:
- "Auto schedule - Low" vs "Auto schedule - Normal" vs "Auto schedule - High"
- "Manual Low" vs "Manual Normal" vs "Manual High"
- Better mode status display

**Implementation**: 
- Add `REG_USERMODE_MANUAL_COMMAND` (register 1130) to modbus.py
- Update climate entity to combine both registers
- Model-specific: Verify register exists on all models

### 5.2 Countdown Timer Support
**Priority: MEDIUM**

Display remaining time for active modes (Away, Crowded, Refresh, Fireplace, Holiday).

**Implementation**:
- Use existing registers 1111/1112 (32-bit remaining time)
- Add template sensors or calculate in Python
- Format as "X h Y min" or "X days"
- Model-specific: Verify countdown works on all models

### 5.3 Template Sensors for Calculated Values
**Priority: MEDIUM**

- **Supply Air Flow Rate**: `(fan_power_factor * 3) rounded` (m³/h)
- **Exhaust Air Flow Rate**: `(fan_power_factor * 3) rounded` (m³/h)
- **Recovery Rate**: `((supply_temp - outdoor_temp) / (exhaust_temp - outdoor_temp)) * 100` (%)
- **Time to Filter Change**: Format seconds as months/days
- **Mode Status**: Combine registers for detailed status
- **Summer/Winter Status**: Convert 0/1 to "Summer"/"Winter"
- **Regulation Mode**: Convert 0/1/2 to descriptive text

**Implementation Options**:
1. Python calculations in sensor.py (better performance)
2. Template sensors in YAML (more flexible, user-customizable)
3. Hybrid: Core calculations in Python, advanced in templates

### 5.4 Additional Number Entities
**Priority: MEDIUM**

- **Eco Heat Offset** (register 2503) - VTR-500 specific
- **Filter Replacement Period** (register 7000) - Verify per model
- **Moisture Extraction Setpoint** (register 2202) - Verify per model
- **Fan Speed Normal** (registers 1414, 1415) - If configurable

---

## 6. Implementation Architecture Changes

### 6.1 Update Coordinator for Model Awareness
**Priority: HIGH**

```python
# In coordinator.py
class SystemairDataUpdateCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant) -> None:
        super().__init__(...)
        self.model: SystemairModel = SystemairModel.UNKNOWN
        self.parameter_map: dict[str, ModbusParameter] = {}
    
    async def _async_setup(self) -> None:
        # ... existing code ...
        model_str = self.config_entry.runtime_data.mb_model
        self.model = SystemairModel(model_str) if model_str else SystemairModel.UNKNOWN
        self.parameter_map = get_parameters_for_model(self.model)
```

### 6.2 Update Entity Creation for Model Awareness
**Priority: HIGH**

```python
# In sensor.py, switch.py, etc.
async def async_setup_entry(
    hass: HomeAssistant,
    entry: SystemairConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data.coordinator
    model = coordinator.model
    
    # Get model-specific entity descriptions
    entity_descriptions = get_entity_descriptions_for_model(model)
    
    async_add_entities(
        SystemairSensor(coordinator, desc)
        for desc in entity_descriptions
        if should_create_entity(model, desc.registry)
    )
```

### 6.3 Graceful Handling of Missing Registers
**Priority: HIGH**

```python
# In coordinator.py
def get_modbus_data(self, register: ModbusParameter) -> float:
    """Get the data for a Modbus register."""
    # Check if register exists for this model
    if register.short not in self.parameter_map:
        LOGGER.debug("Register %s not available for model %s", register.short, self.model)
        return None  # or 0, depending on use case
    
    # ... existing code ...
```

---

## 7. Documentation and Examples

### 7.1 Model-Specific Documentation
**Priority: LOW**

- Document which features are available on which models
- Create model comparison table
- Document register differences between models

### 7.2 Lovelace Dashboard Examples
**Priority: LOW**

- Port Lovelace configs as examples (not part of integration)
- Create model-specific dashboard examples
- Document customization options

### 7.3 Node-RED Flow Examples
**Priority: LOW**

- Port Node-RED flows as examples
- Document automation patterns
- Model-specific automation examples

---

## 8. Testing Strategy

### 8.1 Model Detection Testing
- [ ] Test with VTR-300 unit
- [ ] Test with VTR-500 unit
- [ ] Test with VSR-300 unit
- [ ] Test with unknown/unsupported model (graceful fallback)

### 8.2 Register Verification Testing
- [ ] Verify common registers work on all models
- [ ] Verify model-specific registers only appear on correct models
- [ ] Test register address mappings
- [ ] Test missing register handling

### 8.3 Feature Testing
- [ ] Test all sensors on each model
- [ ] Test all switches on each model
- [ ] Test all number entities on each model
- [ ] Test climate entity on each model
- [ ] Test calculated/template sensors

### 8.4 Backward Compatibility
- [ ] Ensure existing installations continue to work
- [ ] Test migration from unified to model-specific maps
- [ ] Verify default behavior for unknown models

---

## 9. Implementation Priority (Revised)

### Priority 1 (Critical - Blocks Other Work)
1. **Model Detection System** - Extract and store model from API
2. **Model-Specific Parameter Maps** - Create model registry system
3. **Register Address Verification** - Test registers on each model
4. **Graceful Missing Register Handling** - Don't crash on missing registers

### Priority 2 (High Value)
1. **VTR-500 Specific Sensors** - Port from repo2_nonhacs with model checks
2. **Enhanced Mode Detection** - Combine registers for better status
3. **Template Sensors** - Calculated values (flow rates, recovery rate)
4. **Additional Number Entities** - Eco offset, filter period, etc.

### Priority 3 (Medium Value)
1. **Countdown Timer Support** - Remaining time for active modes
2. **VTR-300 / VSR-300 Specific Features** - From documentation
3. **Model-Specific Documentation** - Feature comparison table

### Priority 4 (Lower Priority)
1. **Lovelace Dashboard Examples** - User customization examples
2. **Node-RED Flow Examples** - Automation examples
3. **Advanced Configuration Options** - User preferences

---

## 10. Key Changes from Original Plan

### 10.1 Architecture Understanding
- **SAVE Connect is a gateway** - Not direct Modbus communication
- **Model detection is available** - Via `unit_version["MB Model"]` API
- **Register addresses may differ by model** - Need model-specific maps

### 10.2 Register Address Discrepancies Explained
- Differences between dev and repo2_nonhacs are likely due to:
  1. **Model differences** - VTR-500 vs VTR-300 vs VSR-300
  2. **Communication method** - Direct Modbus vs SAVE Connect API
  3. **Firmware versions** - Different versions may use different registers

### 10.3 Implementation Strategy Changes
- **Must implement model-aware system first** - Before adding new registers
- **Test registers per model** - Cannot assume all registers exist on all models
- **Graceful degradation** - Handle missing features/registers gracefully

### 10.4 New Requirements
- Extract model information during setup
- Create model-specific register maps
- Conditional entity creation based on model
- Documentation of model differences

---

## 11. Next Steps

1. **Extract Model Information** - Update coordinator to store and use model
2. **Create Model Registry** - Define model enum and parameter maps
3. **Test Register Availability** - Test common registers on each model
4. **Implement Model-Specific Maps** - Create VTR-500, VTR-300, VSR-300 maps
5. **Port VTR-500 Features** - Add repo2_nonhacs features with model checks
6. **Document Model Differences** - Create comparison table
7. **Test All Models** - Verify functionality on each supported model

---

## Notes

- SAVE Connect handles Modbus translation, so register addresses in API may differ from direct Modbus
- Some registers may be read-only or write-only depending on model
- Firmware versions may affect register availability
- Always test register reads/writes before assuming they work
- Provide fallback behavior for unknown models or missing registers
