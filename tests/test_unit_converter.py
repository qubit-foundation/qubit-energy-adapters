"""Tests for UnitConverter."""

import pytest
from adapters.units.converter import UnitConverter


@pytest.fixture
def converter():
    return UnitConverter()


# --- Power conversions ---

class TestPowerConversions:
    def test_kw_to_w(self, converter):
        value, unit = converter.convert(5.0, "kW")
        assert unit == "W"
        assert value == 5000.0

    def test_mw_to_w(self, converter):
        value, unit = converter.convert(1.0, "MW")
        assert unit == "W"
        assert value == 1_000_000.0

    def test_w_to_kw(self, converter):
        value, unit = converter.convert(5000.0, "W", to_unit="kW")
        assert unit == "kW"
        assert value == pytest.approx(5.0)

    def test_kw_to_mw(self, converter):
        value, unit = converter.convert(1000.0, "kW", to_unit="MW")
        assert unit == "MW"
        assert value == pytest.approx(1.0)

    def test_hp_to_w(self, converter):
        value, unit = converter.convert(1.0, "HP")
        assert unit == "W"
        assert value == pytest.approx(745.7)

    def test_w_to_w_identity(self, converter):
        value, unit = converter.convert(42.0, "W")
        assert unit == "W"
        assert value == 42.0


# --- Energy conversions ---

class TestEnergyConversions:
    def test_kwh_to_wh(self, converter):
        value, unit = converter.convert(1.0, "kWh")
        assert unit == "Wh"
        assert value == 1000.0

    def test_mwh_to_wh(self, converter):
        value, unit = converter.convert(1.0, "MWh")
        assert unit == "Wh"
        assert value == 1_000_000.0

    def test_wh_to_kwh(self, converter):
        value, unit = converter.convert(5000.0, "Wh", to_unit="kWh")
        assert unit == "kWh"
        assert value == pytest.approx(5.0)

    def test_j_to_wh(self, converter):
        value, unit = converter.convert(3600.0, "J")
        assert unit == "Wh"
        assert value == pytest.approx(1.0, rel=1e-3)


# --- Temperature conversions ---

class TestTemperatureConversions:
    def test_fahrenheit_to_celsius(self, converter):
        value, unit = converter.convert(212.0, "F")
        assert value == pytest.approx(100.0)

    def test_celsius_to_fahrenheit(self, converter):
        value, unit = converter.convert(100.0, "C", to_unit="F")
        assert value == pytest.approx(212.0)

    def test_kelvin_to_celsius(self, converter):
        value, unit = converter.convert(273.15, "K")
        assert value == pytest.approx(0.0)

    def test_celsius_to_kelvin(self, converter):
        value, unit = converter.convert(0.0, "C", to_unit="K")
        assert value == pytest.approx(273.15)

    def test_fahrenheit_to_kelvin(self, converter):
        value, unit = converter.convert(32.0, "F", to_unit="K")
        assert value == pytest.approx(273.15)

    def test_celsius_identity(self, converter):
        value, unit = converter.convert(25.0, "C")
        assert value == pytest.approx(25.0)


# --- Voltage, current, speed, pressure, frequency, irradiance ---

class TestOtherConversions:
    def test_kv_to_v(self, converter):
        value, unit = converter.convert(1.0, "kV")
        assert unit == "V"
        assert value == 1000.0

    def test_ma_to_a(self, converter):
        value, unit = converter.convert(500.0, "mA")
        assert unit == "A"
        assert value == pytest.approx(0.5)

    def test_kmh_to_ms(self, converter):
        value, unit = converter.convert(3.6, "km/h")
        assert unit == "m/s"
        assert value == pytest.approx(1.0, rel=1e-3)

    def test_bar_to_pa(self, converter):
        value, unit = converter.convert(1.0, "bar")
        assert unit == "Pa"
        assert value == 100_000.0

    def test_khz_to_hz(self, converter):
        value, unit = converter.convert(1.0, "kHz")
        assert unit == "Hz"
        assert value == 1000.0

    def test_kw_m2_to_w_m2(self, converter):
        value, unit = converter.convert(1.0, "kW/m2")
        assert unit == "W/m2"
        assert value == 1000.0


# --- Error handling (Phase 1 fix: no more silent failures) ---

class TestErrorHandling:
    def test_unknown_unit_raises(self, converter):
        with pytest.raises(ValueError, match="Unknown unit"):
            converter.convert(100.0, "foo_unit")

    def test_unknown_unit_with_measurement_type_raises(self, converter):
        with pytest.raises(ValueError, match="Unknown source unit"):
            converter.convert(100.0, "lightyears", measurement_type="power")

    def test_explicit_measurement_type_bypasses_detection(self, converter):
        value, unit = converter.convert(5.0, "kW", measurement_type="power")
        assert value == 5000.0
        assert unit == "W"

    def test_unknown_target_unit_returns_si(self, converter):
        value, unit = converter.convert(5.0, "kW", to_unit="bogus_unit")
        assert unit == "W"
        assert value == 5000.0


# --- normalize_to_si ---

class TestNormalizeToSI:
    def test_normalize_dict(self, converter):
        measurements = {
            "power": {"value": 5.0, "unit": "kW"},
            "voltage": {"value": 230.0, "unit": "V"},
            "name": "test_sensor",
        }
        result = converter.normalize_to_si(measurements)
        assert result["power"]["value"] == 5000.0
        assert result["power"]["unit"] == "W"
        assert result["power"]["original_value"] == 5.0
        assert result["voltage"]["value"] == 230.0  # Already SI
        assert result["name"] == "test_sensor"  # Non-measurement untouched


# --- convert_timeseries ---

class TestConvertTimeseries:
    def test_convert_timeseries_power(self, converter):
        ts_data = {
            "measurement": {
                "parameter": "active_power",
                "unit": "kW",
            },
            "data_points": [
                {"value": 5.0, "timestamp": "2025-01-01T00:00:00Z"},
                {"value": 10.0, "timestamp": "2025-01-01T01:00:00Z"},
            ],
        }
        result = converter.convert_timeseries(ts_data)
        assert result["measurement"]["unit"] == "W"
        assert result["measurement"]["original_unit"] == "kW"
        assert result["data_points"][0]["value"] == 5000.0
        assert result["data_points"][0]["original_value"] == 5.0
        assert result["data_points"][1]["value"] == 10000.0
