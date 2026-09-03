"""Deterministic synthetic and demo data for local development.

The package is intentionally dependency-light and has no network or provider
integrations.  Every generator is seeded and every record is marked SYNTHETIC or
DEMO.
"""

from app.synthetic.generators import (
    apply_shock,
    generate_ais_positions,
    generate_berths,
    generate_congestion,
    generate_contract_alternatives,
    generate_demo_scenario,
    generate_freight_observations,
    generate_fuel,
    generate_fx,
    generate_inventory,
    generate_market_shocks,
    generate_ports,
    generate_vessels,
    generate_voyages,
    generate_weather,
    records_to_jsonable,
)
from app.synthetic.models import ShockDefinition, ShockType, SyntheticRecord

# Short aliases keep the package convenient for scripts and notebooks.
generate_ais = generate_ais_positions
generate_positions = generate_ais_positions
generate_freight = generate_freight_observations
generate_contracts = generate_contract_alternatives
generate_shocks = generate_market_shocks

__all__ = [
    "ShockDefinition",
    "ShockType",
    "SyntheticRecord",
    "apply_shock",
    "generate_ais_positions",
    "generate_ais",
    "generate_positions",
    "generate_berths",
    "generate_contract_alternatives",
    "generate_contracts",
    "generate_congestion",
    "generate_demo_scenario",
    "generate_freight_observations",
    "generate_freight",
    "generate_shocks",
    "generate_fuel",
    "generate_fx",
    "generate_inventory",
    "generate_market_shocks",
    "generate_ports",
    "generate_vessels",
    "generate_voyages",
    "generate_weather",
    "records_to_jsonable",
]
