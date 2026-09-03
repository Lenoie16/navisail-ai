import React from "react";

export function CompatibilitySummary({
  feasible,
  hardFailures,
  warnings,
}: {
  feasible: boolean | null;
  hardFailures: string[];
  warnings: string[];
}) {
  if (feasible === null) {
    return (
      <p className="muted-copy">
        Compatibility not evaluated. Complete vessel and cargo inputs first.
      </p>
    );
  }
  return (
    <div
      className={`compatibility-result ${feasible ? "compatibility-result--ok" : "compatibility-result--failed"}`}
    >
      <strong>{feasible ? "Feasible" : "Infeasible"}</strong>
      {!feasible && <p>Hard failures exclude this option until explicitly overridden.</p>}
      {hardFailures.length > 0 && (
        <ul>
          {hardFailures.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      )}
      {warnings.length > 0 && <p>Warnings: {warnings.join("; ")}</p>}
    </div>
  );
}
