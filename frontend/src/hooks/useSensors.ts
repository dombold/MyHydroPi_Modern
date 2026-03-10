import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  deleteSensorHistory,
  fetchCurrentSensors,
  pauseSensors,
  type SensorCurrentResponse,
} from "../api/sensors";

export function useSensors() {
  return useQuery<SensorCurrentResponse>({
    queryKey: ["sensors", "current"],
    queryFn: fetchCurrentSensors,
    refetchInterval: 30_000, // poll every 30s
  });
}

export function usePauseSensors() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: pauseSensors,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["sensors"] }),
  });
}

export function useDeleteSensorHistory() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (days: number) => deleteSensorHistory(days),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["sensors"] }),
  });
}
