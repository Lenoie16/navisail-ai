"use client";

import { createContext, useContext, type ReactNode } from "react";
import { useRealtimeEvents, type RealtimeState } from "../state/realtime";

const RealtimeContext = createContext<RealtimeState | null>(null);

export function RealtimeProvider({ children }: { children: ReactNode }) {
  const state = useRealtimeEvents();
  return <RealtimeContext.Provider value={state}>{children}</RealtimeContext.Provider>;
}

export function useRealtime(): RealtimeState {
  const state = useContext(RealtimeContext);
  if (!state) throw new Error("useRealtime must be used inside RealtimeProvider");
  return state;
}
