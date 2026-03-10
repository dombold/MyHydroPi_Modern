import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  fetchSettings,
  updateSettings,
  type AppSettings,
} from "../api/settings";

export function useSettings() {
  return useQuery<AppSettings>({
    queryKey: ["settings"],
    queryFn: fetchSettings,
  });
}

export function useUpdateSettings() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<AppSettings>) => updateSettings(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["settings"] }),
  });
}
