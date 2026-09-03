import type { StrategyRequest } from "./api";

export function validateStrategyRequest(request: StrategyRequest): string | null {
  if (request.voyages.length === 0) return "At least one voyage is required.";
  if (request.voyages.some((voyage) => voyage.volume_tonnes <= 0))
    return "Voyage volumes must be positive.";
  if (
    request.voyages.some(
      (voyage) => !(voyage.spot_p10 <= voyage.spot_p50 && voyage.spot_p50 <= voyage.spot_p90),
    )
  ) {
    return "Spot quantiles must be ordered.";
  }
  return null;
}
