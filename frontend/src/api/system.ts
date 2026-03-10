import { apiFetch } from "./client";

export const restartSystem = () =>
  apiFetch<{ status: string }>("/system/restart", {
    method: "POST",
    body: JSON.stringify({ confirm: true }),
  });

export const shutdownSystem = () =>
  apiFetch<{ status: string }>("/system/shutdown", {
    method: "POST",
    body: JSON.stringify({ confirm: true }),
  });
