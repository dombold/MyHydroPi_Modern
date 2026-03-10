import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  fetchRelayStates,
  updateRelayState,
  type RelayStatesResponse,
} from "../api/relays";

export function useRelays() {
  return useQuery<RelayStatesResponse>({
    queryKey: ["relays", "states"],
    queryFn: fetchRelayStates,
    refetchInterval: 5_000, // poll every 5s for GPIO feedback
  });
}

export function useUpdateRelay() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ relayId, state }: { relayId: string; state: "on" | "off" | "auto" }) =>
      updateRelayState(relayId, state),
    onMutate: async ({ relayId, state }) => {
      // Optimistic update
      await qc.cancelQueries({ queryKey: ["relays", "states"] });
      const prev = qc.getQueryData<RelayStatesResponse>(["relays", "states"]);
      qc.setQueryData<RelayStatesResponse>(["relays", "states"], (old) => {
        if (!old) return old;
        return {
          relays: old.relays.map((r) =>
            r.id === relayId ? { ...r, override: state } : r
          ),
        };
      });
      return { prev };
    },
    onError: (_err, _vars, ctx) => {
      if (ctx?.prev) qc.setQueryData(["relays", "states"], ctx.prev);
    },
    onSettled: () => qc.invalidateQueries({ queryKey: ["relays", "states"] }),
  });
}
