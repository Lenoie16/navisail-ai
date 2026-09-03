# MaritimeStateVector

`MaritimeStateVector` is NAVISAIL's canonical, versioned cross-domain state
contract. Downstream forecasting, vessel, port, congestion, cost, optimization,
risk, simulation, recommendation, copilot, and execution components must consume
this snapshot rather than independently assembling competing state.

Each snapshot has a deterministic snapshot ID, monotonically meaningful version,
generated and effective UTC timestamps, and a decision-session UUID. Components
are named for shipment, cargo, origin/destination, vessel, AIS, port, berth,
route, freight, congestion, weather, fuel, FX, inventory, market, and risk.

Every populated component retains:

- observation timestamp
- source
- quality score
- freshness state and evaluation metadata
- explicit source status
- confidence where meaningful
- normalized component data

The builder accepts normalized Phase 3 `SourceRecord` values or already typed
components. Fixed inputs, including timestamps, produce the same snapshot ID
and serialized state. Snapshot comparison reports added, removed, changed, and
stale components; added or changed information is included in
`material_changes`.

## API

- `POST /api/v1/maritime-state/snapshots` creates and stores a snapshot.
- `GET /api/v1/maritime-state/snapshots/{snapshot_id}` retrieves one.
- `GET /api/v1/maritime-state/sessions/{decision_session_id}/snapshots` lists
  snapshots for a decision session in version order.
- `GET /api/v1/maritime-state/snapshots/{before_id}/compare/{after_id}` compares
  two snapshots.

The current store is process-local by design. Durable snapshot persistence will
be introduced with the later audit and execution persistence work; the contract
and API boundary remain stable.
