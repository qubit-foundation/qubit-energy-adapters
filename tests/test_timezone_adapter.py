"""Tests for TimezoneAdapter."""

import pytest
from datetime import datetime, timezone as dt_tz
import pytz
from adapters.timezone.adapter import TimezoneAdapter


@pytest.fixture
def adapter():
    return TimezoneAdapter(default_timezone="UTC")


@pytest.fixture
def eastern_adapter():
    return TimezoneAdapter(default_timezone="US/Eastern")


# --- Basic UTC conversion ---

class TestToUTC:
    def test_naive_string_with_source_tz(self, adapter):
        result = adapter.to_utc("2025-01-15 12:00:00", source_tz="US/Eastern")
        assert "2025-01-15T17:00:00" in result
        assert result.endswith("Z")

    def test_naive_string_defaults_to_utc(self, adapter):
        result = adapter.to_utc("2025-01-15T12:00:00")
        assert "2025-01-15T12:00:00" in result

    def test_aware_string_already_utc(self, adapter):
        result = adapter.to_utc("2025-01-15T12:00:00Z")
        assert "2025-01-15T12:00:00" in result

    def test_datetime_object_naive(self, adapter):
        dt = datetime(2025, 1, 15, 12, 0, 0)
        result = adapter.to_utc(dt, source_tz="US/Pacific")
        assert "2025-01-15T20:00:00" in result

    def test_datetime_object_aware(self, adapter):
        eastern = pytz.timezone("US/Eastern")
        dt = eastern.localize(datetime(2025, 7, 15, 12, 0, 0))  # EDT = UTC-4
        result = adapter.to_utc(dt)
        assert "2025-07-15T16:00:00" in result

    def test_output_format_is_iso_with_millis(self, adapter):
        result = adapter.to_utc("2025-01-15T12:00:00Z")
        # Should be like 2025-01-15T12:00:00.000Z
        assert result.endswith("Z")
        parts = result.split(".")
        assert len(parts) == 2
        assert len(parts[1]) == 4  # "000Z"

    def test_default_timezone_used_for_naive(self, eastern_adapter):
        result = eastern_adapter.to_utc("2025-01-15T12:00:00")
        # Eastern = UTC-5 in January
        assert "2025-01-15T17:00:00" in result


# --- Phase 1 fix: re-localization instead of replace ---

class TestRelocalizationFix:
    def test_aware_datetime_with_source_tz_relocalizes(self, adapter):
        """Previously dt.replace(tzinfo=tz) was used, which gave wrong results."""
        # Create a datetime that claims to be UTC
        utc_dt = pytz.UTC.localize(datetime(2025, 1, 15, 12, 0, 0))
        # But caller says it's actually Eastern time
        result = adapter.to_utc(utc_dt, source_tz="US/Eastern")
        # Should treat 12:00 as Eastern and convert to 17:00 UTC
        assert "2025-01-15T17:00:00" in result

    def test_aware_datetime_without_source_tz_uses_existing(self, adapter):
        eastern = pytz.timezone("US/Eastern")
        dt = eastern.localize(datetime(2025, 1, 15, 12, 0, 0))
        result = adapter.to_utc(dt)
        # Should use the existing Eastern tzinfo
        assert "2025-01-15T17:00:00" in result


# --- Phase 1 fix: unknown timezone raises ValueError ---

class TestUnknownTimezone:
    def test_unknown_tz_raises(self, adapter):
        with pytest.raises(ValueError, match="Unknown timezone"):
            adapter.to_utc("2025-01-15T12:00:00", source_tz="Fake/Timezone")

    def test_unknown_default_tz_raises(self):
        bad_adapter = TimezoneAdapter(default_timezone="Fake/Zone")
        with pytest.raises(ValueError, match="Unknown timezone"):
            bad_adapter.to_utc("2025-01-15T12:00:00")


# --- Timezone caching ---

class TestCaching:
    def test_same_tz_cached(self, adapter):
        tz1 = adapter.get_timezone("US/Eastern")
        tz2 = adapter.get_timezone("US/Eastern")
        assert tz1 is tz2

    def test_different_tz_not_same(self, adapter):
        tz1 = adapter.get_timezone("US/Eastern")
        tz2 = adapter.get_timezone("US/Pacific")
        assert tz1 is not tz2


# --- convert_timeseries ---

class TestConvertTimeseries:
    def test_converts_all_timestamps(self, adapter):
        ts_data = {
            "timezone": "US/Eastern",
            "period": {
                "start": "2025-01-15T08:00:00",
                "end": "2025-01-15T09:00:00",
            },
            "data_points": [
                {"timestamp": "2025-01-15T08:00:00", "value": 100},
                {"timestamp": "2025-01-15T08:30:00", "value": 200},
            ],
            "created_at": "2025-01-15T07:00:00",
        }
        result = adapter.convert_timeseries(ts_data)
        assert result["timezone"] == "UTC"
        assert "13:00:00" in result["period"]["start"]  # 8am EST = 1pm UTC
        assert "14:00:00" in result["period"]["end"]
        assert "13:00:00" in result["data_points"][0]["timestamp"]
        assert "12:00:00" in result["created_at"]

    def test_explicit_source_tz_overrides_data(self, adapter):
        ts_data = {
            "timezone": "US/Eastern",
            "period": {"start": "2025-01-15T12:00:00"},
            "data_points": [],
        }
        result = adapter.convert_timeseries(ts_data, source_tz="US/Pacific")
        # Pacific = UTC-8, so 12:00 PST = 20:00 UTC
        assert "20:00:00" in result["period"]["start"]


# --- localize_timestamp ---

class TestLocalizeTimestamp:
    def test_utc_to_eastern(self, adapter):
        result = adapter.localize_timestamp("2025-01-15T17:00:00Z", "US/Eastern")
        assert "12:00:00" in result

    def test_naive_assumed_utc(self, adapter):
        result = adapter.localize_timestamp("2025-01-15T17:00:00", "US/Eastern")
        assert "12:00:00" in result


# --- batch_convert ---

class TestBatchConvert:
    def test_batch_converts_all(self, adapter):
        timestamps = [
            "2025-01-15T12:00:00",
            "2025-01-15T13:00:00",
            "2025-01-15T14:00:00",
        ]
        results = adapter.batch_convert(timestamps, source_tz="US/Eastern")
        assert len(results) == 3
        assert all(r.endswith("Z") for r in results)
        assert "17:00:00" in results[0]
