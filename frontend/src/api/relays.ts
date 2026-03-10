import { apiFetch } from "./client";

export interface RelayState {
  id: string;
  display_name: string;
  override: "on" | "off" | "auto";
  is_on: boolean;
}

export interface RelayStatesResponse {
  relays: RelayState[];
}

export const fetchRelayStates = () =>
  apiFetch<RelayStatesResponse>("/relays/states");

export const updateRelayState = (relayId: string, state: "on" | "off" | "auto") =>
  apiFetch<{ relay_id: string; state: string }>(`/relays/${relayId}/state`, {
    method: "PUT",
    body: JSON.stringify({ state }),
  });
