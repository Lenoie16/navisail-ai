"""Common, typed contracts for external and synthetic maritime data."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.data.freshness import FreshnessInfo


class SourceStatus(StrEnum):
    LIVE = "LIVE"
    DELAYED = "DELAYED"
    ESTIMATED = "ESTIMATED"
    SYNTHETIC = "SYNTHETIC"
    DEMO = "DEMO"


class DataDomain(StrEnum):
    FREIGHT_MARKET = "freight_market"
    AIS_VESSEL = "ais_vessel"
    PORT = "port"
    BERTH = "berth"
    WEATHER = "weather"
    FUEL = "fuel"
    FX = "fx"
    INVENTORY = "inventory"
    ROUTE_REFERENCE = "route_reference"
    NEWS_GEOPOLITICAL = "news_geopolitical"


class Coordinate(BaseModel):
    """WGS84 coordinate with bounds checked at the contract boundary."""

    model_config = ConfigDict(extra="forbid")

    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


class PayloadModel(BaseModel):
    model_config = ConfigDict(extra="allow", str_strip_whitespace=True)

    @model_validator(mode="after")
    def timestamps_are_timezone_aware(self) -> PayloadModel:
        for value in self.__dict__.values():
            if isinstance(value, datetime) and (value.tzinfo is None or value.utcoffset() is None):
                raise ValueError("payload timestamps must include a timezone")
        return self


class FreightMarketPayload(PayloadModel):
    route_id: str = Field(min_length=1)
    vessel_class: str = Field(min_length=1)
    rate: float = Field(gt=0)
    currency: str = Field(min_length=3, max_length=3)
    unit: str = Field(min_length=1)


class AISVesselPayload(PayloadModel):
    vessel_id: str = Field(min_length=1)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    speed_knots: float = Field(default=0, ge=0)
    heading_degrees: float | None = Field(default=None, ge=0, lt=360)


class PortPayload(PayloadModel):
    port_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    country_code: str = Field(min_length=2, max_length=2)
    coordinate: Coordinate


class BerthPayload(PayloadModel):
    berth_id: str = Field(min_length=1)
    port_id: str = Field(min_length=1)
    max_draft_m: float | None = Field(default=None, ge=0)
    available: bool = True


class WeatherPayload(PayloadModel):
    location_id: str = Field(min_length=1)
    coordinate: Coordinate
    temperature_c: float
    wind_speed_knots: float = Field(default=0, ge=0)


class FuelPayload(PayloadModel):
    port_id: str = Field(min_length=1)
    fuel_type: str = Field(min_length=1)
    price: float = Field(gt=0)
    currency: str = Field(min_length=3, max_length=3)
    unit: str = Field(min_length=1)


class FXPayload(PayloadModel):
    base_currency: str = Field(min_length=3, max_length=3)
    quote_currency: str = Field(min_length=3, max_length=3)
    rate: float = Field(gt=0)

    @model_validator(mode="after")
    def different_currencies(self) -> FXPayload:
        if self.base_currency.upper() == self.quote_currency.upper():
            raise ValueError("base_currency and quote_currency must differ")
        return self


class InventoryPayload(PayloadModel):
    location_id: str = Field(min_length=1)
    item_id: str = Field(min_length=1)
    quantity: float = Field(ge=0)
    unit: str = Field(min_length=1)


class RouteReferencePayload(PayloadModel):
    route_id: str = Field(min_length=1)
    origin_id: str = Field(min_length=1)
    destination_id: str = Field(min_length=1)
    distance_nm: float = Field(gt=0)

    @model_validator(mode="after")
    def distinct_endpoints(self) -> RouteReferencePayload:
        if self.origin_id == self.destination_id:
            raise ValueError("origin_id and destination_id must differ")
        return self


class NewsGeopoliticalPayload(PayloadModel):
    event_id: str = Field(min_length=1)
    headline: str = Field(min_length=1)
    region: str = Field(min_length=1)
    severity: str = Field(min_length=1)
    published_at: datetime


class Lineage(BaseModel):
    """Traceability metadata retained through normalization."""

    model_config = ConfigDict(extra="forbid")

    ingestion_job_id: UUID = Field(default_factory=uuid4)
    transformation_version: str = Field(min_length=1)
    connector_name: str = Field(min_length=1)
    parent_record_ids: tuple[str, ...] = ()


class SourceRecord[PayloadT: PayloadModel](BaseModel):
    """Envelope shared by every source and domain."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    source: str = Field(min_length=1)
    source_identifier: str = Field(min_length=1)
    domain: DataDomain
    observed_at: datetime
    ingested_at: datetime
    quality_score: float = Field(ge=0, le=1)
    freshness: FreshnessInfo = Field(default_factory=FreshnessInfo)
    status: SourceStatus
    raw_payload: dict[str, Any] | list[Any] | str | None = None
    raw_reference: str | None = Field(default=None, min_length=1)
    normalized_payload: PayloadT
    schema_version: str = Field(min_length=1)
    ingestion_job_id: UUID = Field(default_factory=uuid4)
    transformation_version: str = Field(min_length=1)
    lineage: Lineage

    @field_validator("observed_at", "ingested_at")
    @classmethod
    def timezone_required(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("timestamps must include a timezone")
        return value.astimezone(UTC)

    @model_validator(mode="after")
    def envelope_is_consistent(self) -> SourceRecord[PayloadT]:
        if self.raw_payload is None and self.raw_reference is None:
            raise ValueError("raw_payload or raw_reference is required")
        if self.ingested_at < self.observed_at:
            raise ValueError("ingested_at cannot precede observed_at")
        if self.lineage.ingestion_job_id != self.ingestion_job_id:
            raise ValueError("lineage.ingestion_job_id must match ingestion_job_id")
        if self.lineage.transformation_version != self.transformation_version:
            raise ValueError("lineage.transformation_version must match transformation_version")
        return self


class FreightMarketRecord(SourceRecord[FreightMarketPayload]):
    domain: Literal[DataDomain.FREIGHT_MARKET] = DataDomain.FREIGHT_MARKET


class AISVesselRecord(SourceRecord[AISVesselPayload]):
    domain: Literal[DataDomain.AIS_VESSEL] = DataDomain.AIS_VESSEL


class PortRecord(SourceRecord[PortPayload]):
    domain: Literal[DataDomain.PORT] = DataDomain.PORT


class BerthRecord(SourceRecord[BerthPayload]):
    domain: Literal[DataDomain.BERTH] = DataDomain.BERTH


class WeatherRecord(SourceRecord[WeatherPayload]):
    domain: Literal[DataDomain.WEATHER] = DataDomain.WEATHER


class FuelRecord(SourceRecord[FuelPayload]):
    domain: Literal[DataDomain.FUEL] = DataDomain.FUEL


class FXRecord(SourceRecord[FXPayload]):
    domain: Literal[DataDomain.FX] = DataDomain.FX


class InventoryRecord(SourceRecord[InventoryPayload]):
    domain: Literal[DataDomain.INVENTORY] = DataDomain.INVENTORY


class RouteReferenceRecord(SourceRecord[RouteReferencePayload]):
    domain: Literal[DataDomain.ROUTE_REFERENCE] = DataDomain.ROUTE_REFERENCE


class NewsGeopoliticalRecord(SourceRecord[NewsGeopoliticalPayload]):
    domain: Literal[DataDomain.NEWS_GEOPOLITICAL] = DataDomain.NEWS_GEOPOLITICAL


# Friendly aliases for callers that use the abbreviated names in the catalog.
AISVesselSourceRecord = AISVesselRecord
SourceContract = SourceRecord
DataStatus = SourceStatus


__all__ = [
    "AISVesselPayload",
    "AISVesselRecord",
    "AISVesselSourceRecord",
    "BerthPayload",
    "BerthRecord",
    "Coordinate",
    "DataDomain",
    "DataStatus",
    "FreightMarketPayload",
    "FreightMarketRecord",
    "FuelPayload",
    "FuelRecord",
    "FXPayload",
    "FXRecord",
    "InventoryPayload",
    "InventoryRecord",
    "Lineage",
    "NewsGeopoliticalPayload",
    "NewsGeopoliticalRecord",
    "PayloadModel",
    "PortPayload",
    "PortRecord",
    "RouteReferencePayload",
    "RouteReferenceRecord",
    "SourceRecord",
    "SourceContract",
    "SourceStatus",
    "WeatherPayload",
    "WeatherRecord",
]
