import { apiFetch } from "./client";

export interface SensorMeta {
  column: string;
  display_name: string;
  unit: string;
}

export interface RelayMeta {
  id: string;
  display_name: string;
  table: string;
  dt_pairs: number;
}

export interface MetaResponse {
  sensors: SensorMeta[];
  relays: RelayMeta[];
}

export const fetchMeta = () => apiFetch<MetaResponse>("/meta");
