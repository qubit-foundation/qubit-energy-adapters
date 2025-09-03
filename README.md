# Qubit Energy Adapters

Data transformation and normalization adapters for the Qubit Energy platform.

## Overview

This package provides adapters for normalizing energy data:
- **Unit Converter** - Convert to SI units (kW→W, F→C, etc.)
- **Timezone Adapter** - Normalize timestamps to UTC
- **Protocol Adapter** - Map protocol-specific fields to schemas
- **Validation Adapter** - Validate and clean data

## Installation

```bash
pip install qubit-energy-adapters

# Install from source
git clone https://github.com/qubit-foundation/qubit-energy-adapters.git
cd qubit-energy-adapters
pip install -e .
```

## Quick Start

### Unit Conversion

```python
from adapters.units import UnitConverter

converter = UnitConverter()

# Convert single value
value, unit = converter.convert(7.2, "kW", "W")  # Returns (7200.0, "W")

# Convert to SI automatically
value, unit = converter.convert(50, "fahrenheit")  # Returns (10.0, "celsius")

# Normalize measurements dict
data = {
    "power": {"value": 7.2, "unit": "kW"},
    "temperature": {"value": 72, "unit": "F"}
}
normalized = converter.normalize_to_si(data)
```

### Timezone Normalization

```python
from adapters.timezone import TimezoneAdapter

tz_adapter = TimezoneAdapter(default_timezone="America/New_York")

# Convert to UTC
utc_time = tz_adapter.to_utc("2025-01-15 15:30:00", "America/Los_Angeles")

# Convert TimeSeries data
timeseries = {
    "timezone": "Europe/Berlin",
    "data_points": [
        {"timestamp": "2025-01-15T12:00:00", "value": 100}
    ]
}
normalized = tz_adapter.convert_timeseries(timeseries)
```

## Architecture

Adapters sit between raw data and validated schemas:

```
Raw Data → Adapters → Schemas → Storage
         ↓
    - Unit conversion
    - Timezone normalization  
    - Field mapping
    - Data cleaning
```

## Unit Conversions

### Supported Units

#### Power
- W, kW, MW, GW → Watts (W)
- HP, PS → Watts
- BTU/h → Watts
- kVA, MVA → Watts (assuming PF=1)

#### Energy
- Wh, kWh, MWh, GWh → Watt-hours (Wh)
- J, kJ, MJ → Watt-hours
- cal, kcal → Watt-hours
- BTU → Watt-hours

#### Temperature
- Fahrenheit → Celsius
- Kelvin → Celsius
- All variations (F, °F, K, °C)

#### Other
- Voltage: V, kV, mV → Volts
- Current: A, kA, mA → Amperes
- Speed: km/h, mph → m/s
- Frequency: kHz, MHz, rpm → Hz
- Pressure: bar, psi, atm → Pascal

### Custom Conversions

```python
# Add custom conversion factors
converter.conversions["power"]["BTU/min"] = 17.5843

# Use with TimeSeries data
timeseries_data = {
    "measurement": {"unit": "kW", "parameter": "active_power"},
    "data_points": [{"value": 7.2}]
}
si_data = converter.convert_timeseries(timeseries_data)
```

## Timezone Handling

### Features
- Convert any timezone to UTC
- Handle naive and aware timestamps
- Batch conversion support
- Automatic DST handling

### Supported Formats
- ISO 8601: `2025-01-15T12:00:00Z`
- With timezone: `2025-01-15T12:00:00+02:00`
- Naive: `2025-01-15 12:00:00`

## Integration with Schemas

Adapters are designed to work with [Qubit Energy Schemas](https://github.com/qubit-foundation/qubit-energy-schemas):

```python
from adapters import UnitConverter, TimezoneAdapter
from connectors.mqtt import MQTTConnector

# Setup pipeline
converter = UnitConverter()
tz_adapter = TimezoneAdapter()

def process_data(raw_data):
    # 1. Convert to TimeSeries format
    timeseries = connector.transform_to_timeseries(raw_data)
    
    # 2. Normalize units
    timeseries = converter.convert_timeseries(timeseries)
    
    # 3. Convert to UTC
    timeseries = tz_adapter.convert_timeseries(timeseries)
    
    # 4. Validate against schema
    validate(timeseries, schema)
    
    return timeseries
```

## Development

```bash
# Install development dependencies
pip install -e .[dev]

# Run tests
pytest

# Format code
black adapters/

# Type checking
mypy adapters/
```

## Testing

```python
# Test unit conversion
def test_power_conversion():
    converter = UnitConverter()
    value, unit = converter.convert(5.5, "kW", "W")
    assert value == 5500.0
    assert unit == "W"

# Test timezone conversion
def test_utc_conversion():
    adapter = TimezoneAdapter()
    utc = adapter.to_utc("2025-01-15 12:00:00", "America/New_York")
    assert utc == "2025-01-15T17:00:00Z"
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

- Issues: [GitHub Issues](https://github.com/qubit-foundation/qubit-energy-adapters/issues)
- Discussions: [GitHub Discussions](https://github.com/qubit-foundation/qubit-energy-adapters/discussions)