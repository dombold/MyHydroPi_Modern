import TimerForm from "../components/timers/TimerForm";
import { useMeta } from "../hooks/useMeta";
import { useTimers } from "../hooks/useTimers";

export default function Timers() {
  const { data: meta, isLoading: metaLoading } = useMeta();
  const { data: timers, isLoading: timersLoading } = useTimers();

  if (metaLoading || timersLoading) {
    return <p className="text-hydropi-500 text-sm">Loading…</p>;
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {meta?.relays.map((relay) => {
        const pairs = timers?.[relay.id] ?? [];
        return <TimerForm key={relay.id} relay={relay} pairs={pairs} />;
      })}
    </div>
  );
}
