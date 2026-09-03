"""Physical port, berth, vessel, and cargo compatibility engine."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field


class DynamicConstraints(BaseModel):
	model_config = ConfigDict(extra="forbid")

	water_depth_m: float | None = Field(default=None, gt=0)
	weather_permits: bool = True
	berth_closed: bool = False
	congestion_level: str | None = None
	operational_available: bool = True
	warning_messages: tuple[str, ...] = ()
	available_from: datetime | None = None
	available_until: datetime | None = None


class VesselTechnicalProfile(BaseModel):
	model_config = ConfigDict(extra="forbid")

	vessel_id: str = Field(min_length=1)
	name: str = Field(min_length=1)
	loa_m: float = Field(gt=0)
	beam_m: float = Field(gt=0)
	draft_m: float = Field(gt=0)
	dwt_tonnes: float = Field(gt=0)
	cargo_capabilities: frozenset[str] = frozenset()
	technical_constraints: tuple[str, ...] = ()
	operational_available: bool = True


class CargoConstraints(BaseModel):
	model_config = ConfigDict(extra="forbid")

	cargo_type: str = Field(min_length=1)
	quantity_tonnes: float = Field(gt=0)
	required_capabilities: frozenset[str] = frozenset()


class BerthCapability(BaseModel):
	model_config = ConfigDict(extra="forbid")

	berth_id: str = Field(min_length=1)
	name: str = Field(min_length=1)
	max_loa_m: float | None = Field(default=None, gt=0)
	max_beam_m: float | None = Field(default=None, gt=0)
	max_draft_m: float | None = Field(default=None, gt=0)
	max_dwt_tonnes: float | None = Field(default=None, gt=0)
	cargo_capabilities: frozenset[str] = frozenset()
	active: bool = True
	operational_restrictions: tuple[str, ...] = ()
	dynamic: DynamicConstraints = Field(default_factory=DynamicConstraints)


class PortCapability(BaseModel):
	model_config = ConfigDict(extra="forbid")

	port_id: str = Field(min_length=1)
	name: str = Field(min_length=1)
	channel_max_loa_m: float | None = Field(default=None, gt=0)
	channel_max_beam_m: float | None = Field(default=None, gt=0)
	channel_max_draft_m: float | None = Field(default=None, gt=0)
	channel_max_dwt_tonnes: float | None = Field(default=None, gt=0)
	cargo_capabilities: frozenset[str] = frozenset()
	active: bool = True
	operational_restrictions: tuple[str, ...] = ()
	berths: tuple[BerthCapability, ...] = ()
	dynamic: DynamicConstraints = Field(default_factory=DynamicConstraints)


class CompatibilityResult(BaseModel):
	feasible: bool
	hard_failures: tuple[str, ...] = ()
	soft_constraints: tuple[str, ...] = ()
	warnings: tuple[str, ...] = ()
	limiting_factor: str | None = None
	berth_id: str | None = None
	berth_level_compatibility: bool | None = None
	confidence: float = Field(ge=0, le=1)
	supporting_evidence: tuple[str, ...] = ()
	penalty: float = Field(ge=0)


class CompatibilityEngine:
	"""Evaluate physical feasibility while preserving hard exclusions."""

	def check(
		self,
		vessel: VesselTechnicalProfile,
		port: PortCapability,
		cargo: CargoConstraints,
		berth: BerthCapability | None = None,
		*,
		dynamic: DynamicConstraints | None = None,
		at: datetime | None = None,
	) -> CompatibilityResult:
		hard: list[str] = []
		soft: list[str] = []
		warnings: list[str] = []
		evidence: list[str] = []
		active_dynamic = dynamic or port.dynamic
		limits = [
			(port.channel_max_loa_m, vessel.loa_m, "LOA exceeds channel limit"),
			(port.channel_max_beam_m, vessel.beam_m, "beam exceeds channel limit"),
			(port.channel_max_draft_m, vessel.draft_m, "draft exceeds channel limit"),
			(port.channel_max_dwt_tonnes, vessel.dwt_tonnes, "DWT exceeds channel limit"),
		]
		for limit, value, failure in limits:
			if limit is not None:
				evidence.append(
					f"{failure.removesuffix(' exceeds channel limit')}: {value} <= {limit}"
				)
				if value > limit:
					hard.append(failure)
		if not port.active or not active_dynamic.operational_available:
			hard.append("port is operationally unavailable")
		if not vessel.operational_available:
			hard.append("vessel is operationally unavailable")
		if (
			active_dynamic.water_depth_m is not None
			and vessel.draft_m > active_dynamic.water_depth_m
		):
			hard.append("draft exceeds current water depth")
			evidence.append(f"current water depth: {active_dynamic.water_depth_m} m")
		if not active_dynamic.weather_permits:
			hard.append("weather conditions prohibit operation")
		if active_dynamic.berth_closed:
			hard.append("berth is closed")
		missing = cargo.required_capabilities - port.cargo_capabilities
		if missing:
			hard.append(f"port lacks cargo capabilities: {', '.join(sorted(missing))}")
		if cargo.quantity_tonnes > vessel.dwt_tonnes:
			hard.append("cargo quantity exceeds vessel DWT")
		missing_vessel = cargo.required_capabilities - vessel.cargo_capabilities
		if missing_vessel:
			hard.append(f"vessel lacks cargo capabilities: {', '.join(sorted(missing_vessel))}")
		for restriction in port.operational_restrictions:
			soft.append(restriction)
		if active_dynamic.congestion_level and active_dynamic.congestion_level.lower() not in {
			"low",
			"normal",
		}:
			soft.append(f"congestion is {active_dynamic.congestion_level}")
		warnings.extend(active_dynamic.warning_messages)
		berth_result: CompatibilityResult | None = None
		if berth is not None:
			berth_result = self._check_berth(vessel, cargo, berth)
			hard.extend(berth_result.hard_failures)
			soft.extend(berth_result.soft_constraints)
			warnings.extend(berth_result.warnings)
			evidence.extend(berth_result.supporting_evidence)
		if at is not None and at.tzinfo is None:
			raise ValueError("at must include a timezone")
		if at is not None:
			evaluation_time = at.astimezone(UTC)
			if (
				active_dynamic.available_from is not None
				and evaluation_time < active_dynamic.available_from.astimezone(UTC)
			) or (
				active_dynamic.available_until is not None
				and evaluation_time > active_dynamic.available_until.astimezone(UTC)
			):
				hard.append("operation falls outside temporal availability window")
		limiting = hard[0] if hard else (soft[0] if soft else None)
		return CompatibilityResult(
			feasible=not hard,
			hard_failures=tuple(dict.fromkeys(hard)),
			soft_constraints=tuple(dict.fromkeys(soft)),
			warnings=tuple(dict.fromkeys(warnings)),
			limiting_factor=limiting,
			berth_id=berth.berth_id if berth else None,
			berth_level_compatibility=not berth_result.hard_failures if berth_result else None,
			confidence=0.95 if not warnings else 0.8,
			supporting_evidence=tuple(evidence),
			penalty=float(len(soft)) if not hard else float("inf"),
		)

	def _check_berth(
		self, vessel: VesselTechnicalProfile, cargo: CargoConstraints, berth: BerthCapability
	) -> CompatibilityResult:
		hard: list[str] = []
		evidence: list[str] = []
		for limit, value, failure in (
			(berth.max_loa_m, vessel.loa_m, "LOA exceeds berth limit"),
			(berth.max_beam_m, vessel.beam_m, "beam exceeds berth limit"),
			(berth.max_draft_m, vessel.draft_m, "draft exceeds berth limit"),
			(berth.max_dwt_tonnes, vessel.dwt_tonnes, "DWT exceeds berth limit"),
		):
			if limit is not None:
				evidence.append(
					f"{failure.removesuffix(' exceeds berth limit')}: {value} <= {limit}"
				)
				if value > limit:
					hard.append(failure)
		if not berth.active or berth.dynamic.berth_closed:
			hard.append("berth is closed")
		missing = cargo.required_capabilities - berth.cargo_capabilities
		if missing:
			hard.append(f"berth lacks cargo capabilities: {', '.join(sorted(missing))}")
		return CompatibilityResult(
			feasible=not hard,
			hard_failures=tuple(hard),
			warnings=berth.dynamic.warning_messages,
			confidence=0.95,
			supporting_evidence=tuple(evidence),
			penalty=float("inf") if hard else 0,
		)

	def vessel_candidate_compatibility(
		self,
		vessels: Iterable[VesselTechnicalProfile],
		port: PortCapability,
		cargo: CargoConstraints,
	) -> dict[str, CompatibilityResult]:
		return {vessel.vessel_id: self.check(vessel, port, cargo) for vessel in vessels}

	def port_candidate_matrix(
		self,
		vessel: VesselTechnicalProfile,
		ports: Iterable[PortCapability],
		cargo: CargoConstraints,
	) -> dict[str, CompatibilityResult]:
		return {port.port_id: self.check(vessel, port, cargo) for port in ports}

	def berth_candidate_matrix(
		self,
		vessel: VesselTechnicalProfile,
		port: PortCapability,
		cargo: CargoConstraints,
	) -> dict[str, CompatibilityResult]:
		return {
			berth.berth_id: self.check(vessel, port, cargo, berth)
			for berth in port.berths
		}


compatibility_engine = CompatibilityEngine()

__all__ = [
	"BerthCapability",
	"CargoConstraints",
	"CompatibilityEngine",
	"CompatibilityResult",
	"DynamicConstraints",
	"PortCapability",
	"VesselTechnicalProfile",
	"compatibility_engine",
]
