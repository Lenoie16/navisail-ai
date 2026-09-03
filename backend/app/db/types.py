"""Database types that work on both PostgreSQL/PostGIS and SQLite tests."""

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.types import DateTime, TypeDecorator, Uuid
from geoalchemy2 import Geography


class UUIDType(TypeDecorator[object]):
    """Native UUID on PostgreSQL and a portable 32-character UUID on SQLite."""

    impl = Uuid
    cache_ok = True

    def load_dialect_impl(self, dialect: Any) -> Any:
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PGUUID(as_uuid=True))
        return dialect.type_descriptor(Uuid(as_uuid=True))


class UTCDateTime(TypeDecorator[datetime]):
    """Timezone-aware UTC datetime with SQLite round-trip preservation."""

    impl = DateTime
    cache_ok = True

    def __init__(self) -> None:
        super().__init__(timezone=True)

    def process_bind_param(self, value: datetime | None, dialect: Any) -> datetime | None:
        if value is None:
            return None
        return (value if value.tzinfo else value.replace(tzinfo=UTC)).astimezone(UTC)

    def process_result_value(self, value: datetime | None, dialect: Any) -> datetime | None:
        if value is None:
            return None
        return (value if value.tzinfo else value.replace(tzinfo=UTC)).astimezone(UTC)


class GeographyType(TypeDecorator[str]):
    """WGS84 geography; uses PostGIS in production and WKT in SQLite."""

    impl = String
    cache_ok = True
    geometry_type = "POINT"
    spatial_index = False
    use_N_D_index = False

    def load_dialect_impl(self, dialect: Any) -> Any:
        if dialect.name == "postgresql":
            return dialect.type_descriptor(Geography(geometry_type=self.geometry_type, srid=4326))
        return dialect.type_descriptor(String(128))


class GeographyPoint(GeographyType):
    """WGS84 point geography."""


class GeographyLineString(GeographyType):
    """WGS84 route line geography."""

    geometry_type = "LINESTRING"
