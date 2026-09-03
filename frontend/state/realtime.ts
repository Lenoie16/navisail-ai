import { useEffect, useReducer, useRef } from "react";
import { apiBaseUrl } from "../lib/api";

export type RealtimeEventType =
  | "orchestration.started"
  | "orchestration.completed"
  | "forecast.started"
  | "forecast.completed"
  | "optimization.started"
  | "optimization.completed"
  | "recommendation.updated"
  | "scenario.started"
  | "scenario.completed"
  | "approval.changed"
  | "execution.changed"
  | "maritime.state.updated";

export type RealtimeEvent = {
  event_id: string;
  event_type: RealtimeEventType;
  occurred_at: string;
  correlation_id: string;
  decision_session_id?: string | null;
  aggregate_id?: string | null;
  sequence: number;
  payload: Record<string, unknown>;
};

export type RealtimeStatus =
  "connecting" | "connected" | "reconnecting" | "disconnected" | "failed";
export type RealtimeState = {
  status: RealtimeStatus;
  connected: boolean;
  source: "stream" | "unavailable";
  lastUpdatedAt?: string;
  events: RealtimeEvent[];
  seenEventIds: string[];
};

export const initialRealtimeState: RealtimeState = {
  status: "disconnected",
  connected: false,
  source: "unavailable",
  events: [],
  seenEventIds: [],
};

export type RealtimeAction =
  | { type: "connecting" }
  | { type: "connected" }
  | { type: "reconnecting" }
  | { type: "disconnected" }
  | { type: "failed" }
  | { type: "event"; event: RealtimeEvent };

export function realtimeReducer(state: RealtimeState, action: RealtimeAction): RealtimeState {
  if (action.type === "connecting") return { ...state, status: "connecting" };
  if (action.type === "connected")
    return { ...state, status: "connected", connected: true, source: "stream" };
  if (action.type === "reconnecting")
    return { ...state, status: "reconnecting", connected: false, source: "stream" };
  if (action.type === "disconnected") return { ...state, status: "disconnected", connected: false };
  if (action.type === "failed")
    return { ...state, status: "failed", connected: false, source: "unavailable" };
  if (state.seenEventIds.includes(action.event.event_id)) return state;
  return {
    ...state,
    events: [...state.events, action.event].slice(-100),
    seenEventIds: [...state.seenEventIds, action.event.event_id].slice(-500),
    lastUpdatedAt: action.event.occurred_at,
  };
}

export function useRealtimeEvents(decisionSessionId?: string): RealtimeState {
  const [state, dispatch] = useReducer(realtimeReducer, initialRealtimeState);
  const lastEventId = useRef<string | undefined>(undefined);

  useEffect(() => {
    if (typeof window === "undefined") return;
    dispatch({ type: "connecting" });
    const params = new URLSearchParams();
    if (decisionSessionId) params.set("decision_session_id", decisionSessionId);
    const source = new EventSource(`${apiBaseUrl}/api/v1/events/stream?${params.toString()}`);
    source.onopen = () => dispatch({ type: "connected" });
    const handleMessage = (message: MessageEvent<string>) => {
      try {
        const event = JSON.parse(message.data) as RealtimeEvent;
        if (event.event_id === lastEventId.current) return;
        lastEventId.current = event.event_id;
        dispatch({ type: "event", event });
      } catch {
        dispatch({ type: "failed" });
      }
    };
    source.onmessage = handleMessage;
    const eventTypes: RealtimeEventType[] = [
      "orchestration.started",
      "orchestration.completed",
      "forecast.started",
      "forecast.completed",
      "optimization.started",
      "optimization.completed",
      "recommendation.updated",
      "scenario.started",
      "scenario.completed",
      "approval.changed",
      "execution.changed",
      "maritime.state.updated",
    ];
    eventTypes.forEach((eventType) => source.addEventListener(eventType, handleMessage));
    source.onerror = () => dispatch({ type: "reconnecting" });
    return () => {
      eventTypes.forEach((eventType) => source.removeEventListener(eventType, handleMessage));
      source.close();
      dispatch({ type: "disconnected" });
    };
  }, [decisionSessionId]);

  return state;
}
