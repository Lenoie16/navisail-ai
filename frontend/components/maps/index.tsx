export function MapReadySurface({
  portName,
  berthName,
  vesselName,
}: {
  portName: string;
  berthName: string;
  vesselName: string;
}) {
  return (
    <div className="map-surface" aria-label="Maritime map context">
      <div className="map-surface__grid" aria-hidden="true" />
      <div className="map-node map-node--port">
        <span>PORT</span>
        <strong>{portName}</strong>
      </div>
      <div className="map-route" aria-hidden="true">
        <span />
      </div>
      <div className="map-node map-node--berth">
        <span>BERTH</span>
        <strong>{berthName}</strong>
      </div>
      <div className="map-node map-node--vessel">
        <span>VESSEL</span>
        <strong>{vesselName}</strong>
      </div>
      <p className="map-surface__note">
        Map geometry and live positions require a connected geospatial feed.
      </p>
    </div>
  );
}
