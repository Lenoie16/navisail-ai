"""Seeded generators for NAVISAIL's local synthetic and demo datasets."""

from __future__ import annotations

import copy
import hashlib
import random
from datetime import UTC, date, datetime, timedelta
from typing import Any
from uuid import UUID, uuid5

from app.data.contracts import (
    AISVesselPayload,
    AISVesselRecord,
    BerthPayload,
    BerthRecord,
    Coordinate,
    FreightMarketPayload,
    FreightMarketRecord,
    FuelPayload,
    FuelRecord,
    FXPayload,
    FXRecord,
    InventoryPayload,
    InventoryRecord,
    Lineage,
    PortPayload,
    PortRecord,
    SourceStatus,
    WeatherPayload,
    WeatherRecord,
)
from app.synthetic.models import ShockDefinition, ShockType, SyntheticRecord

DateLike = date | datetime | str
_NAMESPACE = UUID("3d0a4ac6-df8a-4ab1-b7a6-8c0af9d3c0aa")
_DEFAULT_START = date(2025, 1, 1)
_DEFAULT_END = date(2025, 1, 7)


def _as_datetime(value: DateLike) -> datetime:
    if isinstance(value, datetime):
        return value.astimezone(UTC) if value.tzinfo else value.replace(tzinfo=UTC)
    if isinstance(value, date):
        return datetime.combine(value, datetime.min.time(), tzinfo=UTC)
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return parsed.astimezone(UTC) if parsed.tzinfo else parsed.replace(tzinfo=UTC)


def _window(
    start_date: DateLike = _DEFAULT_START,
    end_date: DateLike = _DEFAULT_END,
    date_range: tuple[DateLike, DateLike] | None = None,
) -> tuple[datetime, datetime]:
    start, end = date_range or (start_date, end_date)
    start_dt, end_dt = _as_datetime(start), _as_datetime(end)
    if end_dt < start_dt:
        raise ValueError("end_date must not precede start_date")
    return start_dt, end_dt


def _rng(seed: int, scenario_id: str, domain: str) -> random.Random:
    material = f"{seed}:{scenario_id}:{domain}".encode()
    return random.Random(int.from_bytes(hashlib.sha256(material).digest()[:8], "big"))


def _status(demo: bool) -> SourceStatus:
    return SourceStatus.DEMO if demo else SourceStatus.SYNTHETIC


def _record_uuid(seed: int, scenario_id: str, domain: str, identifier: str) -> UUID:
    return uuid5(_NAMESPACE, f"{seed}:{scenario_id}:{domain}:{identifier}")


def _envelope(
    record_type: type[Any],
    *,
    seed: int,
    scenario_id: str,
    domain: str,
    identifier: str,
    observed_at: datetime,
    payload: Any,
    status: SourceStatus,
) -> Any:
    job_id = _record_uuid(seed, scenario_id, domain, "ingestion")
    lineage = Lineage(
        ingestion_job_id=job_id,
        transformation_version="synthetic-v1",
        connector_name="synthetic-engine",
    )
    return record_type(
        source="demo-engine" if status is SourceStatus.DEMO else "synthetic-engine",
        source_identifier=identifier,
        observed_at=observed_at,
        ingested_at=observed_at,
        quality_score=1.0,
        status=status,
        raw_payload=payload.model_dump(mode="json"),
        normalized_payload=payload,
        schema_version="1.0",
        ingestion_job_id=job_id,
        transformation_version="synthetic-v1",
        lineage=lineage,
    )


def _custom_record(
    *,
    seed: int,
    scenario_id: str,
    domain: str,
    identifier: str,
    observed_at: datetime,
    geography: str,
    payload: dict[str, Any],
    status: SourceStatus,
) -> SyntheticRecord:
    return SyntheticRecord(
        record_id=str(_record_uuid(seed, scenario_id, domain, identifier)),
        source="demo-engine" if status is SourceStatus.DEMO else "synthetic-engine",
        source_status=status,
        scenario_id=scenario_id,
        observed_at=observed_at,
        geography=geography,
        payload=payload,
    )


def _count(quantity: int | float | None, default: int, maximum: int = 100) -> int:
    if quantity is None:
        return default
    result = int(quantity)
    if result < 1:
        raise ValueError("quantity must be positive")
    return min(result, maximum)


def generate_vessels(
    *,
    seed: int = 26006,
    scenario_id: str = "synthetic",
    start_date: DateLike = _DEFAULT_START,
    end_date: DateLike = _DEFAULT_END,
    geographic_region: str = "global",
    quantity: int | None = None,
    volume: float | None = None,
    date_range: tuple[DateLike, DateLike] | None = None,
    demo: bool = False,
) -> list[SyntheticRecord]:
    """Generate deterministic vessel particulars for a region."""

    start, _ = _window(start_date, end_date, date_range)
    rng = _rng(seed, scenario_id, "vessels")
    records: list[SyntheticRecord] = []
    classes = ("Capesize", "Panamax", "Supramax")
    for index in range(_count(quantity, 6)):
        vessel_id = f"VSL-{scenario_id.upper()[:8]}-{index + 1:03d}"
        vessel_class = classes[index % len(classes)]
        dwt = {"Capesize": 175000, "Panamax": 82000, "Supramax": 58000}[vessel_class]
        payload = {
            "vessel_id": vessel_id,
            "name": f"Demo {vessel_class} {index + 1}",
            "imo_number": f"{9100000 + index:07d}",
            "vessel_class": vessel_class,
            "operator": ("Southern Cross Shipping", "Bayline Maritime")[index % 2],
            "deadweight_tonnes": dwt,
            "speed_knots": round(13.0 + rng.random() * 2.5, 2),
            "status": "active",
            "requested_volume_tonnes": volume,
            "source_status": _status(demo).value,
        }
        records.append(
            _custom_record(
                seed=seed,
                scenario_id=scenario_id,
                domain="vessels",
                identifier=vessel_id,
                observed_at=start,
                geography=geographic_region,
                payload=payload,
                status=_status(demo),
            )
        )
    return records


def generate_ports(
    *,
    seed: int = 26006,
    scenario_id: str = "synthetic",
    start_date: DateLike = _DEFAULT_START,
    end_date: DateLike = _DEFAULT_END,
    geographic_region: str = "Australia-East Coast India",
    quantity: int | None = None,
    date_range: tuple[DateLike, DateLike] | None = None,
    demo: bool = False,
) -> list[PortRecord]:
    """Generate typed ports, including the canonical Australia/India candidates."""

    start, _ = _window(start_date, end_date, date_range)
    candidates = (
        ("AUNCL", "Newcastle", "AU", -32.9283, 151.7817),
        ("AUPKL", "Port Kembla", "AU", -34.4733, 150.9025),
        ("INPRD", "Paradip", "IN", 20.2667, 86.7000),
        ("INDBD", "Dhamra", "IN", 20.6250, 86.9500),
    )
    chosen = candidates[: _count(quantity, len(candidates))]
    status = _status(demo)
    return [
        _envelope(
            PortRecord,
            seed=seed,
            scenario_id=scenario_id,
            domain="ports",
            identifier=unlocode,
            observed_at=start,
            payload=PortPayload(
                port_id=unlocode,
                name=name,
                country_code=country,
                coordinate=Coordinate(latitude=latitude, longitude=longitude),
            ),
            status=status,
        )
        for unlocode, name, country, latitude, longitude in chosen
    ]


def generate_berths(
    *,
    seed: int = 26006,
    scenario_id: str = "synthetic",
    start_date: DateLike = _DEFAULT_START,
    end_date: DateLike = _DEFAULT_END,
    geographic_region: str = "Australia-East Coast India",
    quantity: int | None = None,
    date_range: tuple[DateLike, DateLike] | None = None,
    demo: bool = False,
) -> list[BerthRecord]:
    """Generate deterministic berth capacities for the generated ports."""

    del geographic_region
    start, _ = _window(start_date, end_date, date_range)
    ports = generate_ports(
        seed=seed,
        scenario_id=scenario_id,
        start_date=start,
        end_date=end_date,
        quantity=quantity,
        demo=demo,
    )
    status = _status(demo)
    records: list[BerthRecord] = []
    for index, port in enumerate(ports):
        port_id = port.normalized_payload.port_id
        records.append(
            _envelope(
                BerthRecord,
                seed=seed,
                scenario_id=scenario_id,
                domain="berths",
                identifier=f"{port_id}-B01",
                observed_at=start,
                payload=BerthPayload(
                    berth_id=f"{port_id}-B01",
                    port_id=port_id,
                    max_draft_m=18.5 if index % 2 == 0 else 16.0,
                    available=True,
                ),
                status=status,
            )
        )
    return records


def generate_ais_positions(
    *,
    seed: int = 26006,
    scenario_id: str = "synthetic",
    start_date: DateLike = _DEFAULT_START,
    end_date: DateLike = _DEFAULT_END,
    geographic_region: str = "Australia-East Coast India",
    quantity: int | None = None,
    volume: float | None = None,
    points_per_vessel: int = 8,
    date_range: tuple[DateLike, DateLike] | None = None,
    demo: bool = False,
) -> list[AISVesselRecord]:
    """Generate interpolated AIS trajectories between Australia and India."""

    start, end = _window(start_date, end_date, date_range)
    vessels = generate_vessels(
        seed=seed,
        scenario_id=scenario_id,
        start_date=start,
        end_date=end,
        geographic_region=geographic_region,
        quantity=quantity,
        volume=volume,
        demo=demo,
    )
    points = max(2, min(points_per_vessel, 100))
    status = _status(demo)
    records: list[AISVesselRecord] = []
    for _vessel_index, vessel in enumerate(vessels):
        vessel_id = str(vessel.payload["vessel_id"])
        rng = _rng(seed, scenario_id, f"ais:{vessel_id}")
        for point_index in range(points):
            fraction = point_index / (points - 1)
            # Small deterministic offsets make tracks distinct while remaining plausible.
            latitude = -32.9 + fraction * 53.2 + (rng.random() - 0.5) * 0.5
            longitude = 151.8 - fraction * 65.0 + (rng.random() - 0.5) * 0.5
            observed_at = start + (end - start) * fraction
            identifier = f"{vessel_id}-{point_index + 1:03d}"
            records.append(
                _envelope(
                    AISVesselRecord,
                    seed=seed,
                    scenario_id=scenario_id,
                    domain="ais",
                    identifier=identifier,
                    observed_at=observed_at,
                    payload=AISVesselPayload(
                        vessel_id=vessel_id,
                        latitude=round(latitude, 5),
                        longitude=round(longitude, 5),
                        speed_knots=round(12.0 + rng.random() * 2.5, 2),
                        heading_degrees=round(230 + rng.random() * 15, 2),
                    ),
                    status=status,
                )
            )
    return records


def generate_freight_observations(
    *,
    seed: int = 26006,
    scenario_id: str = "synthetic",
    start_date: DateLike = _DEFAULT_START,
    end_date: DateLike = _DEFAULT_END,
    geographic_region: str = "Australia-East Coast India",
    quantity: int | None = None,
    volume: float | None = 150000,
    date_range: tuple[DateLike, DateLike] | None = None,
    demo: bool = False,
) -> list[FreightMarketRecord]:
    """Generate freight rates for candidate routes."""

    start, end = _window(start_date, end_date, date_range)
    routes = (
        ("AU-IND-1", "Newcastle", "Paradip", 34.0),
        ("AU-IND-2", "Port Kembla", "Dhamra", 36.5),
    )
    rng = _rng(seed, scenario_id, "freight")
    chosen = routes[: _count(quantity, len(routes))]
    status = _status(demo)
    observations: list[FreightMarketRecord] = []
    for route_id, origin, destination, base_rate in chosen:
        payload = FreightMarketPayload(
            route_id=route_id,
            vessel_class="Capesize",
            rate=round(base_rate + rng.random() * 2, 2),
            currency="USD",
            unit="usd/tonne",
        )
        observations.append(
            _envelope(
                FreightMarketRecord,
                seed=seed,
                scenario_id=scenario_id,
                domain="freight",
                identifier=route_id,
                observed_at=end,
                payload=payload,
                status=status,
            )
        )
        # Keep volume in the raw payload for downstream demo displays without changing the contract.
        if isinstance(observations[-1].raw_payload, dict):
            observations[-1].raw_payload["cargo_volume_tonnes"] = volume
            observations[-1].raw_payload["origin"] = origin
            observations[-1].raw_payload["destination"] = destination
    return observations


def generate_fuel(
    *,
    seed: int = 26006,
    scenario_id: str = "synthetic",
    start_date: DateLike = _DEFAULT_START,
    end_date: DateLike = _DEFAULT_END,
    geographic_region: str = "Australia-East Coast India",
    quantity: int | None = None,
    date_range: tuple[DateLike, DateLike] | None = None,
    demo: bool = False,
) -> list[FuelRecord]:
    """Generate bunker fuel prices at candidate ports."""

    del geographic_region
    start, end = _window(start_date, end_date, date_range)
    ports = ("AUNCL", "AUPKL", "INPRD", "INDBD")[: _count(quantity, 4)]
    rng = _rng(seed, scenario_id, "fuel")
    return [
        _envelope(
            FuelRecord,
            seed=seed,
            scenario_id=scenario_id,
            domain="fuel",
            identifier=f"{port}-VLSFO",
            observed_at=end,
            payload=FuelPayload(
                port_id=port,
                fuel_type="VLSFO",
                price=round(590 + rng.random() * 35, 2),
                currency="USD",
                unit="usd/m3",
            ),
            status=_status(demo),
        )
        for port in ports
    ]


def generate_fx(
    *,
    seed: int = 26006,
    scenario_id: str = "synthetic",
    start_date: DateLike = _DEFAULT_START,
    end_date: DateLike = _DEFAULT_END,
    geographic_region: str = "Australia-East Coast India",
    quantity: int | None = None,
    date_range: tuple[DateLike, DateLike] | None = None,
    demo: bool = False,
) -> list[FXRecord]:
    """Generate deterministic USD/INR and AUD/USD observations."""

    del geographic_region, quantity
    _, end = _window(start_date, end_date, date_range)
    rng = _rng(seed, scenario_id, "fx")
    pairs = (("USD", "INR", 83.1), ("AUD", "USD", 0.66))
    return [
        _envelope(
            FXRecord,
            seed=seed,
            scenario_id=scenario_id,
            domain="fx",
            identifier=f"{base}{quote}",
            observed_at=end,
            payload=FXPayload(
                base_currency=base,
                quote_currency=quote,
                rate=round(rate + (rng.random() - 0.5) * 0.2, 4),
            ),
            status=_status(demo),
        )
        for base, quote, rate in pairs
    ]


def generate_weather(
    *,
    seed: int = 26006,
    scenario_id: str = "synthetic",
    start_date: DateLike = _DEFAULT_START,
    end_date: DateLike = _DEFAULT_END,
    geographic_region: str = "Australia-East Coast India",
    quantity: int | None = None,
    date_range: tuple[DateLike, DateLike] | None = None,
    demo: bool = False,
) -> list[WeatherRecord]:
    """Generate weather observations at route endpoints."""

    start, end = _window(start_date, end_date, date_range)
    locations: tuple[tuple[str, float, float], ...] = (
        ("AUNCL", -32.9283, 151.7817),
        ("INPRD", 20.2667, 86.7),
    )
    locations = locations[: _count(quantity, len(locations))]
    rng = _rng(seed, scenario_id, "weather")
    return [
        _envelope(
            WeatherRecord,
            seed=seed,
            scenario_id=scenario_id,
            domain="weather",
            identifier=f"{location}-weather",
            observed_at=start + (end - start) / 2,
            payload=WeatherPayload(
                location_id=location,
                coordinate=Coordinate(latitude=latitude, longitude=longitude),
                temperature_c=round(21 + rng.random() * 12, 1),
                wind_speed_knots=round(8 + rng.random() * 12, 1),
            ),
            status=_status(demo),
        )
        for location, latitude, longitude in locations
    ]


def generate_inventory(
    *,
    seed: int = 26006,
    scenario_id: str = "synthetic",
    start_date: DateLike = _DEFAULT_START,
    end_date: DateLike = _DEFAULT_END,
    geographic_region: str = "East Coast India",
    quantity: int | None = None,
    volume: float | None = 150000,
    date_range: tuple[DateLike, DateLike] | None = None,
    demo: bool = False,
) -> list[InventoryRecord]:
    """Generate plant inventory exposure for steel raw material."""

    del geographic_region, quantity
    _, end = _window(start_date, end_date, date_range)
    rng = _rng(seed, scenario_id, "inventory")
    amount = float(volume if volume is not None else 150000)
    return [
        _envelope(
            InventoryRecord,
            seed=seed,
            scenario_id=scenario_id,
            domain="inventory",
            identifier="PLANT-BOKARO:IRON-ORE",
            observed_at=end,
            payload=InventoryPayload(
                location_id="PLANT-BOKARO",
                item_id="IRON-ORE",
                quantity=round(max(0, amount * 0.22 + rng.random() * 5000), 3),
                unit="tonnes",
            ),
            status=_status(demo),
        )
    ]


def generate_congestion(
    *,
    seed: int = 26006,
    scenario_id: str = "synthetic",
    start_date: DateLike = _DEFAULT_START,
    end_date: DateLike = _DEFAULT_END,
    geographic_region: str = "East Coast India",
    quantity: int | None = None,
    date_range: tuple[DateLike, DateLike] | None = None,
    demo: bool = False,
) -> list[SyntheticRecord]:
    """Generate port queue and congestion observations."""

    del geographic_region
    _, end = _window(start_date, end_date, date_range)
    ports = ("INPRD", "INDBD")[: _count(quantity, 2)]
    rng = _rng(seed, scenario_id, "congestion")
    status = _status(demo)
    return [
        _custom_record(
            seed=seed,
            scenario_id=scenario_id,
            domain="congestion",
            identifier=f"{port}-congestion",
            observed_at=end,
            geography="East Coast India",
            payload={
                "port_id": port,
                "congestion_days": round(2 + rng.random() * 2, 1),
                "queue_vessels": 4 + index,
                "severity": "moderate",
                "source_status": status.value,
            },
            status=status,
        )
        for index, port in enumerate(ports)
    ]


def generate_voyages(
    *,
    seed: int = 26006,
    scenario_id: str = "synthetic",
    start_date: DateLike = _DEFAULT_START,
    end_date: DateLike = _DEFAULT_END,
    geographic_region: str = "Australia-East Coast India",
    quantity: int | None = None,
    volume: float | None = 150000,
    date_range: tuple[DateLike, DateLike] | None = None,
    demo: bool = False,
) -> list[SyntheticRecord]:
    """Generate planned voyages for the candidate routes."""

    start, end = _window(start_date, end_date, date_range)
    routes = (("AU-IND-1", "AUNCL", "INPRD"), ("AU-IND-2", "AUPKL", "INDBD"))
    chosen = routes[: _count(quantity, len(routes))]
    status = _status(demo)
    return [
        _custom_record(
            seed=seed,
            scenario_id=scenario_id,
            domain="voyages",
            identifier=f"VOY-{index + 1:03d}",
            observed_at=start,
            geography=geographic_region,
            payload={
                "voyage_id": f"VOY-{index + 1:03d}",
                "route_id": route,
                "vessel_id": f"VSL-{scenario_id.upper()[:8]}-{index + 1:03d}",
                "origin_port_id": origin,
                "destination_port_id": destination,
                "departure_at": start.isoformat(),
                "arrival_at": (end + timedelta(days=18 + index)).isoformat(),
                "cargo_volume_tonnes": volume,
                "source_status": status.value,
            },
            status=status,
        )
        for index, (route, origin, destination) in enumerate(chosen)
    ]


def generate_contract_alternatives(
    *,
    seed: int = 26006,
    scenario_id: str = "synthetic",
    start_date: DateLike = _DEFAULT_START,
    end_date: DateLike = _DEFAULT_END,
    geographic_region: str = "Australia-East Coast India",
    quantity: int | None = None,
    volume: float | None = 150000,
    date_range: tuple[DateLike, DateLike] | None = None,
    demo: bool = False,
) -> list[SyntheticRecord]:
    """Generate comparable spot, index-linked, and COA contract alternatives."""

    start, end = _window(start_date, end_date, date_range)
    names = (
        ("SPOT-2025", "spot", 34.8, "single voyage"),
        ("INDEX-2025", "index_linked", 33.6, "Platts index + premium"),
        ("COA-2025", "coa", 31.9, "annual volume commitment"),
    )[: _count(quantity, 3)]
    status = _status(demo)
    return [
        _custom_record(
            seed=seed,
            scenario_id=scenario_id,
            domain="contracts",
            identifier=contract_id,
            observed_at=start,
            geography=geographic_region,
            payload={
                "contract_id": contract_id,
                "alternative": alternative,
                "rate_usd_per_tonne": rate,
                "cargo_volume_tonnes": volume,
                "valid_from": start.date().isoformat(),
                "valid_until": end.date().isoformat(),
                "terms": terms,
                "source_status": status.value,
            },
            status=status,
        )
        for contract_id, alternative, rate, terms in names
    ]


def generate_market_shocks(
    *,
    seed: int = 26006,
    scenario_id: str = "synthetic",
    start_date: DateLike = _DEFAULT_START,
    end_date: DateLike = _DEFAULT_END,
    geographic_region: str = "Australia-East Coast India",
    quantity: int | None = None,
    date_range: tuple[DateLike, DateLike] | None = None,
    demo: bool = False,
) -> list[ShockDefinition]:
    """Return the fixed shock catalogue used by the demo and tests."""

    del seed, start_date, end_date, geographic_region, quantity, date_range, demo
    definitions = (
        (ShockType.PORT_OUTAGE, "Paradip port outage", "INPRD", {"outage_days": 3}),
        (ShockType.CONGESTION_PLUS_5_DAYS, "Paradip congestion +5 days", "INPRD", {"days": 5}),
        (ShockType.FREIGHT_SPIKE, "Freight market spike", "AU-IND-1", {"multiplier": 1.35}),
        (ShockType.CYCLONE, "Bay of Bengal cyclone", "INPRD", {"wind_speed_knots": 55}),
        (ShockType.FUEL_SPIKE, "Bunker fuel spike", "INPRD", {"multiplier": 1.30}),
        (ShockType.VESSEL_FAILURE, "Candidate vessel failure", "VESSEL-1", {"available": 0}),
        (ShockType.SEVERE_CONGESTION, "Severe Paradip congestion", "INPRD", {"days": 10}),
    )
    return [
        ShockDefinition(
            shock_id=f"{scenario_id}-{shock_type.value}",
            shock_type=shock_type,
            name=name,
            description=f"Deterministic demo shock: {name.lower()}.",
            target=target,
            parameters=parameters,
        )
        for shock_type, name, target, parameters in definitions
    ]


def apply_shock(records: list[Any], shock: ShockDefinition) -> list[Any]:
    """Apply one shock to records without mutating the caller's list or records."""

    updated = copy.deepcopy(records)
    target = shock.target
    for record in updated:
        payload = (
            record.normalized_payload.model_dump(mode="python")
            if hasattr(record, "normalized_payload")
            else record.payload
        )
        identifier = (
            getattr(record, "source_identifier", "")
            or payload.get("port_id", "")
            or payload.get("vessel_id", "")
            or payload.get("route_id", "")
        )
        matches = (
            target in str(identifier)
            or target == payload.get("port_id")
            or target == payload.get("location_id")
        )
        if shock.shock_type is ShockType.VESSEL_FAILURE and target == "VESSEL-1":
            matches = str(payload.get("vessel_id", "")).endswith("-001") or matches
        if not matches:
            continue
        if shock.shock_type is ShockType.PORT_OUTAGE and matches:
            payload["operational_status"] = "closed"
            payload["available"] = False
        elif shock.shock_type in {ShockType.CONGESTION_PLUS_5_DAYS, ShockType.SEVERE_CONGESTION}:
            payload["congestion_days"] = round(
                float(payload.get("congestion_days", 0)) + float(shock.parameters["days"]), 1
            )
            payload["severity"] = "severe"
        elif shock.shock_type is ShockType.FREIGHT_SPIKE and matches:
            payload["rate"] = round(
                float(payload.get("rate", 0)) * float(shock.parameters["multiplier"]), 2
            )
        elif shock.shock_type is ShockType.CYCLONE and payload.get("location_id") == target:
            payload["wind_speed_knots"] = float(shock.parameters["wind_speed_knots"])
        elif shock.shock_type is ShockType.FUEL_SPIKE and payload.get("port_id") == target:
            payload["price"] = round(
                float(payload.get("price", 0)) * float(shock.parameters["multiplier"]), 2
            )
        elif shock.shock_type is ShockType.VESSEL_FAILURE and matches:
            payload["status"] = "failed"
            payload["available"] = False
        if hasattr(record, "normalized_payload"):
            record.normalized_payload = type(record.normalized_payload).model_validate(payload)
            record.raw_payload = record.normalized_payload.model_dump(mode="json")
        else:
            record.payload = payload
    return updated


def records_to_jsonable(records: list[Any]) -> list[dict[str, Any]]:
    """Serialize typed and custom records in stable list order."""

    result: list[dict[str, Any]] = []
    for record in records:
        if hasattr(record, "model_dump"):
            serialized = record.model_dump(mode="json")
            if isinstance(record, SyntheticRecord):
                serialized["status"] = serialized["source_status"]
            result.append(serialized)
        else:
            raise TypeError(f"unsupported synthetic record: {type(record)!r}")
    return result


def generate_demo_scenario(
    *,
    seed: int = 26006,
    scenario_id: str = "au-steel-east-india",
    start_date: DateLike = date(2025, 1, 6),
    end_date: DateLike = date(2025, 1, 12),
    geographic_region: str = "Australia-East Coast India",
    quantity: int | None = None,
    volume: float | None = 150000,
    date_range: tuple[DateLike, DateLike] | None = None,
) -> dict[str, Any]:
    """Build the canonical 150,000 MT Australia-origin steel plant scenario."""

    start, end = _window(start_date, end_date, date_range)
    kwargs: dict[str, Any] = {
        "seed": seed,
        "scenario_id": scenario_id,
        "start_date": start,
        "end_date": end,
        "geographic_region": geographic_region,
        "demo": True,
    }
    cargo_volume = float(volume if volume is not None else 150000)
    return {
        "scenario_id": scenario_id,
        "scenario_name": "Australia-origin to East Coast India steel plant",
        "source_status": SourceStatus.DEMO.value,
        "seed": seed,
        "date_range": {"start": start.date().isoformat(), "end": end.date().isoformat()},
        "cargo": {
            "commodity": "steelmaking coal",
            "origin_country": "AU",
            "origin_region": "Australia",
            "destination_plant": "Bokaro Steel Plant",
            "destination_country": "IN",
            "volume_tonnes": cargo_volume,
        },
        "vessels": records_to_jsonable(
            generate_vessels(**kwargs, quantity=quantity, volume=cargo_volume)
        ),
        "ports": records_to_jsonable(generate_ports(**kwargs, quantity=None)),
        "berths": records_to_jsonable(generate_berths(**kwargs, quantity=None)),
        "ais_positions": records_to_jsonable(
            generate_ais_positions(**kwargs, quantity=quantity, volume=cargo_volume)
        ),
        "freight": records_to_jsonable(
            generate_freight_observations(**kwargs, quantity=None, volume=cargo_volume)
        ),
        "fuel": records_to_jsonable(generate_fuel(**kwargs, quantity=None)),
        "fx": records_to_jsonable(generate_fx(**kwargs)),
        "weather": records_to_jsonable(generate_weather(**kwargs)),
        "congestion": records_to_jsonable(generate_congestion(**kwargs)),
        "inventory": records_to_jsonable(generate_inventory(**kwargs, volume=cargo_volume)),
        "voyages": records_to_jsonable(
            generate_voyages(**kwargs, quantity=None, volume=cargo_volume)
        ),
        "contract_alternatives": records_to_jsonable(
            generate_contract_alternatives(**kwargs, quantity=None, volume=cargo_volume)
        ),
        "market_shocks": [
            shock.model_dump(mode="json") for shock in generate_market_shocks(**kwargs)
        ],
        "inventory_exposure": {
            "plant": "Bokaro Steel Plant",
            "committed_volume_tonnes": cargo_volume,
            "at_risk_tonnes": cargo_volume,
            "exposure_status": "shipment_not_yet_booked",
        },
    }


__all__ = [
    "apply_shock",
    "generate_ais_positions",
    "generate_ais",
    "generate_positions",
    "generate_berths",
    "generate_contract_alternatives",
    "generate_congestion",
    "generate_demo_scenario",
    "generate_freight_observations",
    "generate_freight",
    "generate_contracts",
    "generate_fuel",
    "generate_fx",
    "generate_inventory",
    "generate_market_shocks",
    "generate_shocks",
    "generate_ports",
    "generate_vessels",
    "generate_voyages",
    "generate_weather",
    "records_to_jsonable",
]

# Backwards-friendly names used by the command-line demo helpers.
generate_ais = generate_ais_positions
generate_positions = generate_ais_positions
generate_freight = generate_freight_observations
generate_contracts = generate_contract_alternatives
generate_shocks = generate_market_shocks
