import Button from "../ui/Button";
import StatusBadge from "../ui/StatusBadge";
import { useUpdateRelay } from "../../hooks/useRelays";
import type { RelayState } from "../../api/relays";

interface Props {
  relay: RelayState;
}

const STATES = ["on", "off", "auto"] as const;

export default function RelayCard({ relay }: Props) {
  const update = useUpdateRelay();

  return (
    <tr className="border-b border-hydropi-100 last:border-0 hover:bg-hydropi-50/70 transition-[background-color] duration-150">
      <td className="py-3 px-4 font-medium text-hydropi-900 whitespace-nowrap">
        {relay.display_name}
      </td>
      <td className="py-3 px-4">
        <StatusBadge status={relay.is_on ? "on" : "off"} />
      </td>
      <td className="py-3 px-4 text-sm text-hydropi-600 capitalize">
        {relay.override}
      </td>
      <td className="py-3 px-4">
        <div className="flex gap-1">
          {STATES.map((s) => (
            <Button
              key={s}
              size="sm"
              variant={relay.override === s ? "primary" : "secondary"}
              loading={update.isPending && update.variables?.relayId === relay.id && update.variables?.state === s}
              onClick={() => update.mutate({ relayId: relay.id, state: s })}
              className="capitalize"
            >
              {s}
            </Button>
          ))}
        </div>
      </td>
    </tr>
  );
}
