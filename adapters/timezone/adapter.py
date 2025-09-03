"""
Timezone adapter for converting timestamps to UTC.
"""

from datetime import datetime, timezone
from typing import Dict, Any, Optional, Union
import pytz
from dateutil import parser


class TimezoneAdapter:
    """Convert timestamps from various timezones to UTC."""
    
    def __init__(self, default_timezone: str = "UTC"):
        """
        Initialize timezone adapter.
        
        Args:
            default_timezone: Default timezone for naive timestamps
        """
        self.default_timezone = default_timezone
        self._tz_cache = {}
        
    def get_timezone(self, tz_name: str):
        """Get timezone object from cache or create new."""
        if tz_name not in self._tz_cache:
            try:
                self._tz_cache[tz_name] = pytz.timezone(tz_name)
            except pytz.exceptions.UnknownTimeZoneError:
                # Fall back to UTC if timezone unknown
                self._tz_cache[tz_name] = pytz.UTC
        return self._tz_cache[tz_name]
    
    def to_utc(self, timestamp: Union[str, datetime], 
               source_tz: Optional[str] = None) -> str:
        """
        Convert timestamp to UTC.
        
        Args:
            timestamp: Timestamp string or datetime object
            source_tz: Source timezone (if None, assumes UTC or uses default)
            
        Returns:
            ISO format UTC timestamp string
        """
        # Parse string timestamps
        if isinstance(timestamp, str):
            dt = parser.parse(timestamp)
        else:
            dt = timestamp
        
        # Handle timezone-aware vs naive timestamps
        if dt.tzinfo is None:
            # Naive timestamp - localize to source timezone
            if source_tz:
                tz = self.get_timezone(source_tz)
                dt = tz.localize(dt)
            else:
                # Use default timezone
                tz = self.get_timezone(self.default_timezone)
                dt = tz.localize(dt)
        elif source_tz:
            # Already has timezone but we want to ensure it's correct
            tz = self.get_timezone(source_tz)
            dt = dt.replace(tzinfo=tz)
        
        # Convert to UTC
        utc_dt = dt.astimezone(pytz.UTC)
        
        # Return ISO format string
        return utc_dt.strftime('%Y-%m-%dT%H:%M:%S.%fZ')[:-4] + 'Z'
    
    def convert_timeseries(self, timeseries_data: Dict[str, Any],
                          source_tz: Optional[str] = None) -> Dict[str, Any]:
        """
        Convert all timestamps in TimeSeries data to UTC.
        
        Args:
            timeseries_data: TimeSeries schema data
            source_tz: Source timezone for the data
            
        Returns:
            TimeSeries data with UTC timestamps
        """
        converted = timeseries_data.copy()
        
        # Get timezone from data if not provided
        if not source_tz and 'timezone' in converted:
            source_tz = converted['timezone']
        
        # Convert period timestamps
        if 'period' in converted:
            if 'start' in converted['period']:
                converted['period']['start'] = self.to_utc(
                    converted['period']['start'],
                    source_tz
                )
            if 'end' in converted['period']:
                converted['period']['end'] = self.to_utc(
                    converted['period']['end'],
                    source_tz
                )
        
        # Convert data point timestamps
        if 'data_points' in converted:
            for point in converted['data_points']:
                if 'timestamp' in point:
                    point['timestamp'] = self.to_utc(
                        point['timestamp'],
                        source_tz
                    )
        
        # Convert metadata timestamps
        if 'created_at' in converted:
            converted['created_at'] = self.to_utc(
                converted['created_at'],
                source_tz
            )
        if 'updated_at' in converted:
            converted['updated_at'] = self.to_utc(
                converted['updated_at'],
                source_tz
            )
        
        # Update timezone field to UTC
        converted['timezone'] = 'UTC'
        
        return converted
    
    def localize_timestamp(self, utc_timestamp: Union[str, datetime],
                          target_tz: str) -> str:
        """
        Convert UTC timestamp to local timezone.
        
        Args:
            utc_timestamp: UTC timestamp
            target_tz: Target timezone name
            
        Returns:
            Localized timestamp string
        """
        # Parse if string
        if isinstance(utc_timestamp, str):
            dt = parser.parse(utc_timestamp)
        else:
            dt = utc_timestamp
        
        # Ensure it's UTC
        if dt.tzinfo is None:
            dt = pytz.UTC.localize(dt)
        else:
            dt = dt.astimezone(pytz.UTC)
        
        # Convert to target timezone
        tz = self.get_timezone(target_tz)
        local_dt = dt.astimezone(tz)
        
        # Return with timezone info
        return local_dt.isoformat()
    
    def batch_convert(self, timestamps: list, 
                     source_tz: Optional[str] = None) -> list:
        """
        Convert multiple timestamps to UTC.
        
        Args:
            timestamps: List of timestamp strings
            source_tz: Source timezone
            
        Returns:
            List of UTC timestamp strings
        """
        return [self.to_utc(ts, source_tz) for ts in timestamps]