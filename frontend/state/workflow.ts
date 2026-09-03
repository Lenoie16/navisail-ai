import type { AuditEvent, ExecutionStatus } from "../lib/api";

export const executionStatusLabels: Record<ExecutionStatus, string> = {
  draft: "Draft",
  approved: "Approved",
  booking_requested: "Booking requested",
  booking_in_progress: "Booking in progress",
  booked: "Booked",
  voyage_active: "Voyage active",
  completed: "Completed",
  cancelled: "Cancelled",
};

export function readableAuditDetails(details: Record<string, unknown>): string[] {
  return Object.entries(details).map(([key, value]) => {
    const label = key.replaceAll("_", " ");
    const display =
      typeof value === "object" && value !== null ? JSON.stringify(value) : String(value);
    return `${label}: ${display}`;
  });
}

export function formatAuditEvent(event: AuditEvent): string {
  return `${event.action} by ${event.actor} on ${new Date(event.occurred_at).toLocaleString()}`;
}
