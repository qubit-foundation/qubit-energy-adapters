"""
Unit converter for normalizing energy measurements to SI units.
"""

from typing import Dict, Tuple, Optional, Any
import json
import os


class UnitConverter:
    """Convert various energy units to SI standard units."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize unit converter.
        
        Args:
            config: Optional configuration dict
        """
        self.config = config or {}
        self.conversions = self._load_conversions()
        
    def _load_conversions(self) -> Dict[str, Dict[str, float]]:
        """Load unit conversion mappings."""
        # Default conversion factors to SI units
        return {
            # Power conversions to Watts (W)
            "power": {
                "W": 1.0,
                "kW": 1000.0,
                "MW": 1000000.0,
                "GW": 1000000000.0,
                "HP": 745.7,  # Horsepower
                "PS": 735.5,  # Metric horsepower
                "BTU/h": 0.293071,  # BTU per hour
                "kVA": 1000.0,  # Assuming PF=1 for simplicity
                "MVA": 1000000.0
            },
            
            # Energy conversions to Watt-hours (Wh)
            "energy": {
                "Wh": 1.0,
                "kWh": 1000.0,
                "MWh": 1000000.0,
                "GWh": 1000000000.0,
                "J": 0.000277778,  # Joules
                "kJ": 0.277778,
                "MJ": 277.778,
                "cal": 0.00116222,  # Calories
                "kcal": 1.16222,
                "BTU": 0.293071
            },
            
            # Voltage conversions to Volts (V)
            "voltage": {
                "V": 1.0,
                "kV": 1000.0,
                "mV": 0.001
            },
            
            # Current conversions to Amperes (A)
            "current": {
                "A": 1.0,
                "kA": 1000.0,
                "mA": 0.001
            },
            
            # Temperature conversions to Celsius
            "temperature": {
                "celsius": 1.0,
                "C": 1.0,
                "kelvin": "K_to_C",  # Special conversion
                "K": "K_to_C",
                "fahrenheit": "F_to_C",  # Special conversion
                "F": "F_to_C"
            },
            
            # Speed conversions to m/s
            "speed": {
                "m/s": 1.0,
                "km/h": 0.277778,
                "mph": 0.44704,
                "knots": 0.514444
            },
            
            # Irradiance conversions to W/m²
            "irradiance": {
                "W/m2": 1.0,
                "W/m²": 1.0,
                "kW/m2": 1000.0,
                "kW/m²": 1000.0
            },
            
            # Frequency conversions to Hz
            "frequency": {
                "Hz": 1.0,
                "kHz": 1000.0,
                "MHz": 1000000.0,
                "rpm": 0.0166667  # Revolutions per minute
            },
            
            # Pressure conversions to Pascal (Pa)
            "pressure": {
                "Pa": 1.0,
                "kPa": 1000.0,
                "MPa": 1000000.0,
                "bar": 100000.0,
                "psi": 6894.76,
                "atm": 101325.0,
                "mmHg": 133.322
            }
        }
    
    def convert(self, value: float, from_unit: str, 
                to_unit: Optional[str] = None,
                measurement_type: Optional[str] = None) -> Tuple[float, str]:
        """
        Convert a value from one unit to another.
        
        Args:
            value: The numeric value to convert
            from_unit: Source unit
            to_unit: Target unit (if None, converts to SI)
            measurement_type: Type of measurement (power, energy, etc.)
            
        Returns:
            Tuple of (converted_value, target_unit)
        """
        # Determine measurement type if not provided
        if measurement_type is None:
            measurement_type = self._detect_measurement_type(from_unit)
        
        if measurement_type is None:
            raise ValueError(
                f"Unknown unit '{from_unit}': cannot detect measurement type. "
                f"Provide measurement_type explicitly or use a recognized unit."
            )
        
        # Get SI unit for this measurement type
        si_unit = self._get_si_unit(measurement_type)
        
        # If no target unit specified, use SI
        if to_unit is None:
            to_unit = si_unit
        
        # Handle temperature special cases
        if measurement_type == "temperature":
            return self._convert_temperature(value, from_unit, to_unit), to_unit
        
        # Get conversion factors
        conversions = self.conversions.get(measurement_type, {})
        
        if from_unit not in conversions:
            raise ValueError(
                f"Unknown source unit '{from_unit}' for measurement type '{measurement_type}'. "
                f"Known units: {list(conversions.keys())}"
            )
        
        # Convert to SI first
        si_value = value * conversions[from_unit]
        
        # If target is SI, we're done
        if to_unit == si_unit:
            return si_value, to_unit
        
        # Convert from SI to target unit
        if to_unit in conversions:
            target_value = si_value / conversions[to_unit]
            return target_value, to_unit
        
        # Unknown target unit, return SI value
        return si_value, si_unit
    
    def _detect_measurement_type(self, unit: str) -> Optional[str]:
        """Detect measurement type from unit string."""
        unit_lower = unit.lower()
        
        # Check each measurement type
        for mtype, units in self.conversions.items():
            if unit in units or unit_lower in [u.lower() for u in units]:
                return mtype
        
        return None
    
    def _get_si_unit(self, measurement_type: str) -> str:
        """Get SI unit for measurement type."""
        si_units = {
            "power": "W",
            "energy": "Wh",
            "voltage": "V",
            "current": "A",
            "temperature": "celsius",
            "speed": "m/s",
            "irradiance": "W/m2",
            "frequency": "Hz",
            "pressure": "Pa"
        }
        return si_units.get(measurement_type, "unknown")
    
    def _convert_temperature(self, value: float, from_unit: str, to_unit: str) -> float:
        """Handle temperature conversions."""
        # Normalize unit names
        from_unit = from_unit.lower()
        to_unit = to_unit.lower()
        
        # Convert to Celsius first
        if from_unit in ["fahrenheit", "f"]:
            celsius = (value - 32) * 5/9
        elif from_unit in ["kelvin", "k"]:
            celsius = value - 273.15
        else:
            celsius = value
        
        # Convert from Celsius to target
        if to_unit in ["fahrenheit", "f"]:
            return celsius * 9/5 + 32
        elif to_unit in ["kelvin", "k"]:
            return celsius + 273.15
        else:
            return celsius
    
    def normalize_to_si(self, measurements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize all measurements in a dict to SI units.
        
        Args:
            measurements: Dict with measurement data including units
            
        Returns:
            Dict with normalized values and SI units
        """
        normalized = measurements.copy()
        
        for key, value in measurements.items():
            if isinstance(value, dict) and 'value' in value and 'unit' in value:
                # This looks like a measurement with unit
                converted_value, si_unit = self.convert(
                    value['value'],
                    value['unit']
                )
                normalized[key] = {
                    'value': converted_value,
                    'unit': si_unit,
                    'original_value': value['value'],
                    'original_unit': value['unit']
                }
        
        return normalized
    
    def convert_timeseries(self, timeseries_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert units in TimeSeries schema data to SI.
        
        Args:
            timeseries_data: Data conforming to TimeSeries schema
            
        Returns:
            TimeSeries data with SI units
        """
        converted = timeseries_data.copy()
        
        # Get current unit from measurement
        if 'measurement' in converted and 'unit' in converted['measurement']:
            current_unit = converted['measurement']['unit']
            parameter = converted['measurement'].get('parameter', '')
            
            # Determine measurement type from parameter name
            measurement_type = None
            if 'power' in parameter.lower():
                measurement_type = 'power'
            elif 'energy' in parameter.lower():
                measurement_type = 'energy'
            elif 'voltage' in parameter.lower():
                measurement_type = 'voltage'
            elif 'current' in parameter.lower():
                measurement_type = 'current'
            elif 'temperature' in parameter.lower():
                measurement_type = 'temperature'
            
            # Get SI unit
            _, si_unit = self.convert(1.0, current_unit, measurement_type=measurement_type)
            
            # Update unit in measurement
            converted['measurement']['unit'] = si_unit
            converted['measurement']['original_unit'] = current_unit
            
            # Convert all data points
            if 'data_points' in converted:
                for point in converted['data_points']:
                    if isinstance(point.get('value'), (int, float)):
                        converted_value, _ = self.convert(
                            point['value'],
                            current_unit,
                            measurement_type=measurement_type
                        )
                        point['original_value'] = point['value']
                        point['value'] = converted_value
        
        return converted