"""
Helper functions for the application.

This module contains utility functions used across different parts of the application.
"""
from datetime import datetime, timezone


def utc_now_naive() -> datetime:
    """
    Return current UTC time without timezone info for database compatibility.

    PostgreSQL's TIMESTAMP WITHOUT TIME ZONE requires naive datetime objects
    (without tzinfo). This function ensures we get the correct UTC time but
    without timezone information attached.

    Returns:
        datetime: Current UTC time as a naive datetime object (tzinfo=None)

    Example:
        >>> dt = utc_now_naive()
        >>> dt.tzinfo is None
        True
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)
