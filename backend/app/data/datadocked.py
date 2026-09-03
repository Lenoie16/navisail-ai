"""Public Data Docked adapter surface.

This module avoids colliding with the repository's legacy ``connectors.py``
module while keeping provider code behind the data package boundary.
"""

from app.data.datadocked_client import (
    DataDockedError,
    DataDockedProvider,
    datadocked_provider,
)
from app.data.datadocked_mapper import map_vessel_location

__all__ = [
    "DataDockedError",
    "DataDockedProvider",
    "datadocked_provider",
    "map_vessel_location",
]
