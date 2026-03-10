import { apiFetch } from "./client";

export interface SensorReading {
  name: string;
  display_name: string;
  value: number | null;
  avg_24h: number | null;
  unit: string;
  alert_high: number | null;
  alert_low: number | null;
  in_alert: boolean;
}

export interface SensorCurrentResponse {
  readings: SensorReading[];
  timestamp: string | null;
  pause_active: boolean;
}

export interface SensorHistoryPoint {
  label: string;
  value: number | null;
}

export interface SensorHistoryResponse {
  sensor: string;
  data: SensorHistoryPoint[];
}

export const fetchCurrentSensors = () =>
  apiFetch<SensorCurrentResponse>("/sensors/current");

export const fetchSensorHistory = (sensor: string, days: number) =>
  apiFetch<SensorHistoryResponse>(`/sensors/history?sensor=${sensor}&days=${days}`);

export const pauseSensors = () =>
  apiFetch<{ paused: boolean }>("/sensors/pause", { method: "POST" });

export const deleteSensorHistory = (olderThanDays: number) =>
  apiFetch<{ deleted: number }>(`/sensors/history?older_than_days=${olderThanDays}`, {
    method: "DELETE",
  });
