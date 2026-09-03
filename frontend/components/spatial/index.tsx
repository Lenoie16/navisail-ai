"use client";

import { useEffect, useMemo, useState } from "react";

export type SpatialTwinState = {
  as_of?: string;
  selected_port_id?: string | null;
  selected_berth_id?: string | null;
  selected_vessel_id?: string | null;
  selected_route_id?: string | null;
  vessels?: Array<Record<string, unknown>>;
  ports?: Array<Record<string, unknown>>;
  berths?: Array<Record<string, unknown>>;
  routes?: Array<Record<string, unknown>>;
  congestion?: Record<string, unknown>;
};

type SpatialSceneProps = {
  twin?: SpatialTwinState | null;
  vesselName?: string;
  portName?: string;
  berthName?: string;
  routeName?: string;
};

function resourceLabel(resource: Record<string, unknown> | undefined, fallback: string) {
  if (!resource) return fallback;
  return String(resource.name ?? resource.code ?? resource.id ?? fallback);
}

function supportsWebgl() {
  if (typeof document === "undefined") return false;
  const canvas = document.createElement("canvas");
  return Boolean(canvas.getContext("webgl2") ?? canvas.getContext("webgl"));
}

export function SpatialMaritimeScene({
  twin,
  vesselName = "Vessel",
  portName = "Port",
  berthName = "Berth",
  routeName = "Selected route",
}: SpatialSceneProps) {
  const [threeReady, setThreeReady] = useState(false);
  const [reducedMotion, setReducedMotion] = useState(false);
  const selectedVessel = useMemo(
    () => twin?.vessels?.find((item) => item.id === twin.selected_vessel_id),
    [twin],
  );
  const selectedPort = useMemo(
    () => twin?.ports?.find((item) => item.id === twin.selected_port_id),
    [twin],
  );
  const selectedBerth = useMemo(
    () => twin?.berths?.find((item) => item.id === twin.selected_berth_id),
    [twin],
  );

  useEffect(() => {
    const media = window.matchMedia("(prefers-reduced-motion: reduce)");
    const update = () => setReducedMotion(media.matches);
    update();
    media.addEventListener("change", update);
    setThreeReady(supportsWebgl());
    return () => media.removeEventListener("change", update);
  }, []);

  const labels = {
    vessel: resourceLabel(selectedVessel, vesselName),
    port: resourceLabel(selectedPort, portName),
    berth: resourceLabel(selectedBerth, berthName),
    route: routeName,
  };
  const congestion = String(twin?.congestion?.status ?? "unavailable");

  if (!threeReady || reducedMotion) {
    return (
      <div
        className="spatial-surface spatial-surface--fallback"
        aria-label="2D maritime twin fallback"
      >
        <div className="spatial-route-line" aria-hidden="true" />
        <span className="spatial-node spatial-node--origin">{labels.route}</span>
        <span className="spatial-node spatial-node--vessel">{labels.vessel}</span>
        <span className="spatial-node spatial-node--destination">
          {labels.port} / {labels.berth}
        </span>
        <p className="chart-note">2D mode: 3D is unavailable or reduced motion is enabled.</p>
      </div>
    );
  }

  return (
    <div className="spatial-surface" aria-label="3D maritime twin scene">
      <div className="spatial-world">
        <div className="spatial-route-line" aria-hidden="true" />
        <div className="spatial-vessel" title={labels.vessel}>
          <span>{labels.vessel}</span>
        </div>
        <div className="spatial-port">
          <span>{labels.port}</span>
          <small>{labels.berth}</small>
        </div>
      </div>
      <div className="spatial-legend">
        <span>Route: {labels.route}</span>
        <span>Congestion: {congestion}</span>
        <span>
          {twin?.as_of
            ? `Twin as of ${new Date(twin.as_of).toLocaleString()}`
            : "Twin state unavailable"}
        </span>
      </div>
    </div>
  );
}
