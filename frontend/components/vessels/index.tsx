export function VesselRelationship({ vessel, berth }: { vessel: string; berth: string }) {
  return (
    <p className="relationship-line">
      <span>{vessel}</span>
      <span aria-hidden="true">→</span>
      <span>{berth}</span>
    </p>
  );
}
