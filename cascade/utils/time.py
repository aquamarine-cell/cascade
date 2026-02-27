"""System time utilities for Cascade."""

from datetime import datetime, timedelta
import os
from zoneinfo import ZoneInfo


def current_time(tz: str = None) -> datetime:
    """Get current time with optional timezone.
    
    Args:
        tz: Timezone string (e.g., 'US/Arizona'). Defaults to system TZ or UTC.
    
    Returns:
        Current datetime object.
    """
    if tz:
        return datetime.now(ZoneInfo(tz))
    return datetime.now()


def formatted_time(format_str: str = "%Y-%m-%d %H:%M:%S %Z", tz: str = None) -> str:
    """Get formatted current time string.
    
    Args:
        format_str: strftime format string.
        tz: Timezone string (e.g., 'US/Arizona').
    
    Returns:
        Formatted time string.
    """
    now = current_time(tz)
    return now.strftime(format_str)


def next_occurrence(hour: int, minute: int = 0, tz: str = None) -> datetime:
    """Calculate next occurrence of a given time.
    
    Useful for scheduling/cron operations.
    
    Args:
        hour: Hour (0-23).
        minute: Minute (0-59).
        tz: Timezone string.
    
    Returns:
        Next datetime when the time will occur.
    """
    now = current_time(tz)
    next_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    
    # If that time has already passed today, move to tomorrow
    if next_time <= now:
        next_time += timedelta(days=1)
    
    return next_time


def get_timezone() -> str:
    """Get configured timezone from environment or system default.
    
    Returns:
        Timezone string (e.g., 'US/Arizona' or 'UTC').
    """
    return os.environ.get("CASCADE_TZ", "UTC")
