import { apiFetch } from "./client";

export interface AppSettings {
  ds18b20_temp_hi?: number;
  ds18b20_temp_low?: number;
  atlas_temp_hi?: number;
  atlas_temp_low?: number;
  ec_hi?: number;
  ec_low?: number;
  ph_hi?: number;
  ph_low?: number;
  orp_hi?: number;
  orp_low?: number;
  read_sensor_delay?: number;
  email_reset_delay?: number;
  pause_reset_delay?: number;
  pause_readings?: boolean;
  to_email?: string;
  pool_size?: number;
}

export const fetchSettings = () => apiFetch<AppSettings>("/settings");

export const updateSettings = (data: Partial<AppSettings>) =>
  apiFetch<{ updated: boolean }>("/settings", {
    method: "PUT",
    body: JSON.stringify(data),
  });
