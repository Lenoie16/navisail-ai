"use client";

import { useEffect, useMemo, useState } from "react";
import { Shell } from "../../components/layout";
import { MapReadySurface } from "../../components/maps";
import { CompatibilitySummary } from "../../components/ports";
import { VesselRelationship } from "../../components/vessels";
import { SpatialMaritimeScene } from "../../components/spatial";
import { ErrorState, LoadingState, MetricCard, StatusBadge } from "../../components/ui";
import {
  type BerthResource,
  type PortResource,
  type VesselResource,
  fetchResource,
} from "../../lib/api";

function label(resource: { name?: string; code?: string; id?: string }) {
  return resource.name ?? resource.code ?? resource.id ?? "Unnamed";
}

export default function PortsPage() {
  const [ports, setPorts] = useState<PortResource[]>([]);
  const [berths, setBerths] = useState<BerthResource[]>([]);
  const [vessels, setVessels] = useState<VesselResource[]>([]);
  const [portId, setPortId] = useState("");
  const [berthId, setBerthId] = useState("");
  const [vesselId, setVesselId] = useState("");
  const [status, setStatus] = useState<"loading" | "ready" | "error">("loading");
  const [error, setError] = useState("");

  useEffect(() => {
    const controller = new AbortController();
    Promise.all([
      fetchResource<PortResource>("ports", controller.signal),
      fetchResource<BerthResource>("berths", controller.signal),
      fetchResource<VesselResource>("vessels", controller.signal),
    ])
      .then(([loadedPorts, loadedBerths, loadedVessels]) => {
        setPorts(loadedPorts);
        setBerths(loadedBerths);
        setVessels(loadedVessels);
        setPortId(loadedPorts[0]?.id ?? "");
        setBerthId(loadedBerths[0]?.id ?? "");
        setVesselId(loadedVessels[0]?.id ?? "");
        setStatus("ready");
      })
      .catch((reason: unknown) => {
        if (!controller.signal.aborted) {
          setError(reason instanceof Error ? reason.message : "Unable to load port intelligence.");
          setStatus("error");
        }
      });
    return () => controller.abort();
  }, []);

  const selectedPort = ports.find((port) => port.id === portId);
  const portBerths = useMemo(
    () => berths.filter((berth) => berth.port_id === portId),
    [berths, portId],
  );
  const selectedBerth =
    portBerths.find((berth) => berth.id === berthId) ??
    berths.find((berth) => berth.id === berthId);
  const selectedVessel = vessels.find((vessel) => vessel.id === vesselId);

  useEffect(() => {
    if (portBerths.length > 0 && !portBerths.some((berth) => berth.id === berthId)) {
      setBerthId(portBerths[0].id ?? "");
    }
  }, [berthId, portBerths]);

  if (status === "loading")
    return (
      <Shell>
        <main className="dashboard">
          <LoadingState />
        </main>
      </Shell>
    );
  if (status === "error")
    return (
      <Shell>
        <main className="dashboard">
          <ErrorState message={error} />
        </main>
      </Shell>
    );

  return (
    <Shell>
      <main className="dashboard">
        <header className="dashboard__header">
          <div>
            <p className="eyebrow">Physical feasibility</p>
            <h1>Port digital twin</h1>
            <p>
              Select a vessel, port, and berth to inspect authoritative constraints and
              relationships.
            </p>
          </div>
          <StatusBadge status="DELAYED" />
        </header>
        <section className="filter-bar" aria-label="Port twin selectors">
          <label>
            Port
            <select value={portId} onChange={(event) => setPortId(event.target.value)}>
              <option value="">Select port</option>
              {ports.map((port) => (
                <option key={port.id} value={port.id}>
                  {label(port)}
                </option>
              ))}
            </select>
          </label>
          <label>
            Berth
            <select value={berthId} onChange={(event) => setBerthId(event.target.value)}>
              <option value="">Select berth</option>
              {portBerths.map((berth) => (
                <option key={berth.id} value={berth.id}>
                  {label(berth)}
                </option>
              ))}
            </select>
          </label>
          <label>
            Candidate vessel
            <select value={vesselId} onChange={(event) => setVesselId(event.target.value)}>
              <option value="">Select vessel</option>
              {vessels.map((vessel) => (
                <option key={vessel.id} value={vessel.id}>
                  {label(vessel)}
                </option>
              ))}
            </select>
          </label>
        </section>
        <section className="panel-grid">
          <div className="glass-panel">
            <h2>Operational context</h2>
            <MapReadySurface
              portName={selectedPort ? label(selectedPort) : "Unselected port"}
              berthName={selectedBerth ? label(selectedBerth) : "Unselected berth"}
              vesselName={selectedVessel ? label(selectedVessel) : "Unselected vessel"}
            />
            <SpatialMaritimeScene
              twin={{
                selected_port_id: selectedPort?.id,
                selected_berth_id: selectedBerth?.id,
                selected_vessel_id: selectedVessel?.id,
                vessels: selectedVessel ? [selectedVessel] : [],
                ports: selectedPort ? [selectedPort] : [],
                berths: selectedBerth ? [selectedBerth] : [],
                congestion: selectedPort?.congestion_status
                  ? { status: selectedPort.congestion_status }
                  : undefined,
              }}
              portName={selectedPort ? label(selectedPort) : "Unselected port"}
              berthName={selectedBerth ? label(selectedBerth) : "Unselected berth"}
              vesselName={selectedVessel ? label(selectedVessel) : "Unselected vessel"}
            />
            <VesselRelationship
              vessel={selectedVessel ? label(selectedVessel) : "Vessel"}
              berth={selectedBerth ? label(selectedBerth) : "Berth"}
            />
          </div>
          <div className="glass-panel">
            <h2>Compatibility</h2>
            <CompatibilitySummary feasible={null} hardFailures={[]} warnings={[]} />
            <p className="muted-copy">
              The backend requires complete technical and cargo profiles; partial CRUD records are
              not used to infer feasibility.
            </p>
          </div>
        </section>
        <section className="panel-grid">
          <div className="glass-panel">
            <h2>Selected berth constraints</h2>
            {selectedBerth ? (
              <div className="metric-grid metric-grid--compact">
                <MetricCard label="Max LOA" value={selectedBerth.max_loa_m ?? "—"} hint="metres" />
                <MetricCard
                  label="Max beam"
                  value={selectedBerth.max_beam_m ?? "—"}
                  hint="metres"
                />
                <MetricCard
                  label="Max draft"
                  value={selectedBerth.max_draft_m ?? "—"}
                  hint="metres"
                />
                <MetricCard
                  label="Max DWT"
                  value={selectedBerth.max_dwt_tonnes ?? "—"}
                  hint="tonnes"
                />
              </div>
            ) : (
              <p className="muted-copy">Select a berth to inspect limits.</p>
            )}
            <p className="detail-copy">
              <strong>Restrictions:</strong>{" "}
              {selectedBerth?.operational_restrictions ?? "Unavailable"}
            </p>
            <p className="detail-copy">
              <strong>Cargo handling:</strong> {selectedBerth?.working_capability ?? "Unavailable"}
            </p>
          </div>
          <div className="glass-panel">
            <h2>Port signals</h2>
            <MetricCard
              label="Congestion"
              value={selectedPort?.congestion_status ?? "Unavailable"}
              hint="Backend signal only"
            />
            <p className="detail-copy">
              <strong>Operational status:</strong>{" "}
              {selectedPort?.operational_status ?? "Unavailable"}
            </p>
            <p className="detail-copy">
              <strong>Location:</strong> {selectedPort?.location ?? "Unavailable"}{" "}
            </p>
            <p className="muted-copy">
              Queue forecasts, live ETA, weather depth, and berth closures are unavailable without
              their source feeds.
            </p>
          </div>
        </section>
      </main>
    </Shell>
  );
}
