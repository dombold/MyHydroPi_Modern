import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  fetchTimers,
  updateTimers,
  type TimerPair,
  type TimersResponse,
} from "../api/timers";

export function useTimers() {
  return useQuery<TimersResponse>({
    queryKey: ["timers"],
    queryFn: fetchTimers,
  });
}

export function useUpdateTimers() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ relayId, pairs }: { relayId: string; pairs: TimerPair[] }) =>
      updateTimers(relayId, pairs),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["timers"] }),
  });
}
