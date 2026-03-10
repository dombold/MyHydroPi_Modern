import { useState } from "react";
import TimeframeSelector from "../components/graphs/TimeframeSelector";
import SensorChart from "../components/graphs/SensorChart";
import { useMeta } from "../hooks/useMeta";

export default function Graphs() {
  const [days, setDays] = useState(1);
  const { data: meta, isLoading } = useMeta();

  if (isLoading) {
    return <p className="text-hydropi-500 text-sm">Loading…</p>;
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-4">
        <span className="text-sm text-hydropi-400">Timeframe:</span>
        <TimeframeSelector value={days} onChange={setDays} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {meta?.sensors.map((sensor) => (
          <SensorChart key={sensor.column} sensor={sensor} days={days} />
        ))}
      </div>
    </div>
  );
}
