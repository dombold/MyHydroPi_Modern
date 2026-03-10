import { useState } from "react";
import Button from "../ui/Button";
import Card from "../ui/Card";
import { useUpdateTimers } from "../../hooks/useTimers";
import type { TimerPair } from "../../api/timers";
import type { RelayMeta } from "../../api/meta";

interface Props {
  relay: RelayMeta;
  pairs: TimerPair[];
}

function toDateTimeLocal(dt: string | null): string {
  if (!dt) return "";
  return dt.slice(0, 16).replace(" ", "T");
}

function toDbFormat(dt: string): string | null {
  if (!dt) return null;
  return dt.replace("T", " ") + ":00";
}

export default function TimerForm({ relay, pairs: initialPairs }: Props) {
  const [pairs, setPairs] = useState<TimerPair[]>(initialPairs);
  const update = useUpdateTimers();

  const handleChange = (idx: number, field: "starttime" | "stoptime", value: string) => {
    setPairs((prev) =>
      prev.map((p, i) =>
        i === idx ? { ...p, [field]: toDbFormat(value) } : p
      )
    );
  };

  const handleSave = () => {
    update.mutate({ relayId: relay.id, pairs });
  };

  return (
    <Card className="p-4">
      <h3 className="text-sm font-display text-hydropi-800 mb-3">
        {relay.display_name}
      </h3>
      <div className="space-y-2">
        {pairs.map((pair, idx) => (
          <div key={pair.pk} className="grid grid-cols-[auto_1fr_1fr] items-center gap-2">
            <span className="text-xs text-hydropi-400 w-5 text-right">{idx + 1}</span>
            <input
              type="datetime-local"
              value={toDateTimeLocal(pair.starttime)}
              onChange={(e) => handleChange(idx, "starttime", e.target.value)}
              className={inputCls}
            />
            <input
              type="datetime-local"
              value={toDateTimeLocal(pair.stoptime)}
              onChange={(e) => handleChange(idx, "stoptime", e.target.value)}
              className={inputCls}
            />
          </div>
        ))}
      </div>
      <div className="mt-3 flex justify-end">
        <Button
          size="sm"
          loading={update.isPending}
          onClick={handleSave}
        >
          Save
        </Button>
      </div>
      {update.isSuccess && (
        <p className="mt-2 text-xs text-green-700 font-medium">Saved successfully.</p>
      )}
    </Card>
  );
}

const inputCls = [
  "w-full bg-white border border-hydropi-300 rounded px-2 py-1.5",
  "text-hydropi-900 text-xs",
  "focus:outline-none focus:ring-2 focus:ring-hydropi-500 focus:border-hydropi-500",
  "shadow-[0_1px_2px_rgba(3,60,115,0.06)]",
].join(" ");
