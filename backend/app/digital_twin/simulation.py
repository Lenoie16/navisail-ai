"""Deterministic digital-twin event simulation."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

from app.digital_twin.events import TwinEvent
from app.digital_twin.state import TwinScenarioParameters, TwinState
from app.maritime.state_vector import MaritimeStateVector
from pydantic import BaseModel, ConfigDict


class TwinSimulationResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scenario_id: str
    source_snapshot_id: UUID
    timeline: tuple[TwinEvent, ...]
    initial_state: TwinState
    final_state: TwinState


class DigitalTwinSimulator:
    """Run isolated what-if events from a canonical state projection."""

    def state_from_vector(
        self, snapshot: MaritimeStateVector, parameters: TwinScenarioParameters | None = None
    ) -> TwinState:
        components = {name: component.data for name, component in snapshot.components.items()}
        params = parameters or TwinScenarioParameters()
        inventory = self._inventory(components.get("inventory", {}))
        return TwinState(
            as_of=snapshot.effective_at,
            shipment=deepcopy(components.get("shipment", {})),
            vessels=tuple(self._records(components.get("vessel", []))),
            ports=tuple(self._records(components.get("port", []))),
            berths=tuple(self._records(components.get("berth", []))),
            routes=tuple(self._records(components.get("route", []))),
            voyage_states={},
            inventory=inventory,
            congestion=deepcopy(components.get("congestion", {})),
            weather=deepcopy(components.get("weather", {})),
            market_conditions=deepcopy(components.get("market", {})),
            selected_port_id=params.port_id,
            selected_vessel_id=params.vessel_id,
            selected_route_id=params.route_id,
            selected_contract=params.contract,
        )

    def simulate(
        self,
        snapshot: MaritimeStateVector,
        *,
        scenario_id: str = "baseline",
        parameters: TwinScenarioParameters | None = None,
    ) -> TwinSimulationResult:
        params = parameters or TwinScenarioParameters()
        initial = self.state_from_vector(snapshot, params)
        current = initial.model_copy(deep=True)
        timeline: list[TwinEvent] = []
        start = params.booking_date or snapshot.effective_at

        def emit(event_type: str, occurred_at: datetime, details: dict[str, Any], mutate) -> None:
            nonlocal current
            before = current.model_dump(mode="json")
            mutate(current)
            after = current.model_dump(mode="json")
            timeline.append(
                TwinEvent(
                    event_type=event_type,
                    occurred_at=occurred_at,
                    state_before=before,
                    state_after=after,
                    details=details,
                )
            )

        emit(
            "vessel departure",
            start,
            {"vessel_id": current.selected_vessel_id},
            lambda state: state.voyage_states.update({"voyage": "departed"}),
        )
        if params.delay_hours:
            emit(
                "vessel delay",
                start + timedelta(hours=params.delay_hours),
                {"delay_hours": params.delay_hours},
                lambda state: state.voyage_states.update({"voyage": "delayed"}),
            )
        arrival = start + timedelta(hours=24 + params.delay_hours)
        emit(
            "port arrival",
            arrival,
            {"port_id": current.selected_port_id},
            lambda state: state.voyage_states.update({"voyage": "port_arrival"}),
        )
        emit(
            "queue formation",
            arrival,
            {"port_id": current.selected_port_id},
            lambda state: state.voyage_states.update({"voyage": "queued"}),
        )
        emit(
            "berth assignment",
            arrival + timedelta(hours=2),
            {},
            lambda state: state.voyage_states.update({"voyage": "berthed"}),
        )
        emit(
            "loading/discharge",
            arrival + timedelta(hours=6),
            {},
            lambda state: state.voyage_states.update({"voyage": "discharged"}),
        )
        emit(
            "departure",
            arrival + timedelta(hours=12),
            {},
            lambda state: state.voyage_states.update({"voyage": "departed_port"}),
        )
        emit(
            "inland arrival",
            arrival + timedelta(hours=36),
            {},
            lambda state: state.voyage_states.update({"voyage": "inland_arrival"}),
        )

        def consume(state: TwinState) -> None:
            quantity = float(state.shipment.get("quantity_tonnes", 0))
            location = str(state.shipment.get("inventory_location", "default"))
            state.inventory[location] = max(0, state.inventory.get(location, 0) - quantity)
            state.voyage_states["voyage"] = "inventory_consumed"

        emit("inventory consumption", arrival + timedelta(hours=38), {}, consume)
        return TwinSimulationResult(
            scenario_id=scenario_id,
            source_snapshot_id=snapshot.snapshot_id,
            timeline=tuple(timeline),
            initial_state=initial,
            final_state=current,
        )

    @staticmethod
    def _records(value: Any) -> list[dict[str, Any]]:
        if isinstance(value, list):
            return [deepcopy(item) for item in value if isinstance(item, dict)]
        return [deepcopy(value)] if isinstance(value, dict) else []

    @staticmethod
    def _inventory(value: Any) -> dict[str, float]:
        if not isinstance(value, dict):
            return {}
        location = value.get("location_id") or value.get("inventory_location")
        quantity = value.get("quantity", value.get("quantity_tonnes"))
        if location is not None and isinstance(quantity, (int, float)):
            return {str(location): float(quantity)}
        return {
            str(key): float(amount)
            for key, amount in value.items()
            if isinstance(amount, (int, float))
        }


digital_twin_simulator = DigitalTwinSimulator()

__all__ = ["DigitalTwinSimulator", "TwinSimulationResult", "digital_twin_simulator"]
