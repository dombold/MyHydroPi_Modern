import { useQuery } from "@tanstack/react-query";
import { fetchMeta, type MetaResponse } from "../api/meta";

export function useMeta() {
  return useQuery<MetaResponse>({
    queryKey: ["meta"],
    queryFn: fetchMeta,
    staleTime: Infinity, // Schema never changes without a service restart
  });
}
