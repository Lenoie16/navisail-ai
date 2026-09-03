export function rankAlternatives<T extends { risk_adjusted_cost: number }>(alternatives: T[]) {
  return [...alternatives].sort(
    (left, right) => left.risk_adjusted_cost - right.risk_adjusted_cost,
  );
}
