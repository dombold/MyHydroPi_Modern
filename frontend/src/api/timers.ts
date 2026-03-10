import { apiFetch } from "./client";

export interface TimerPair {
  pk: number;
  starttime: string | null;
  stoptime: string | null;
}

export type TimersResponse = Record<string, TimerPair[]>;

export const fetchTimers = () => apiFetch<TimersResponse>("/timers");

export const updateTimers = (relayId: string, pairs: TimerPair[]) =>
  apiFetch<{ relay_id: string; updated: number }>(`/timers/${relayId}`, {
    method: "PUT",
    body: JSON.stringify(pairs),
  });
