import { useQuery } from "@tanstack/react-query";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";
import { fetchSensorHistory, type SensorHistoryPoint } from "../../api/sensors";
import type { SensorMeta } from "../../api/meta";
import Card from "../ui/Card";

interface Props {
  sensor: SensorMeta;
  days: number;
}

export default function SensorChart({ sensor, days }: Props) {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["sensor-history", sensor.column, days],
    queryFn: () => fetchSensorHistory(sensor.column, days),
    staleTime: 60_000,
  });

  return (
    <Card className="p-4">
      <h3 className="text-sm font-display text-hydropi-800 mb-3">
        {sensor.display_name}
        {sensor.unit && <span className="text-hydropi-400 text-xs ml-1">({sensor.unit})</span>}
      </h3>

      {isLoading && (
        <div className="h-40 flex items-center justify-center text-hydropi-400 text-sm">
          Loading…
        </div>
      )}

      {isError && (
        <div className="h-40 flex items-center justify-center text-red-600 text-sm">
          Failed to load data
        </div>
      )}

      {data && (
        <ResponsiveContainer width="100%" height={180}>
          <LineChart data={data.data} margin={{ top: 4, right: 8, left: -20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(3,60,115,0.08)" />
            <XAxis
              dataKey="label"
              tick={{ fill: "#1271c2", fontSize: 10 }}
              tickLine={false}
              axisLine={{ stroke: "rgba(3,60,115,0.15)" }}
              interval="preserveStartEnd"
            />
            <YAxis
              tick={{ fill: "#1271c2", fontSize: 10 }}
              tickLine={false}
              axisLine={false}
              domain={["auto", "auto"]}
            />
            <Tooltip
              contentStyle={{
                background: "#ffffff",
                border: "1px solid rgba(3,60,115,0.15)",
                borderRadius: "8px",
                color: "#033C73",
                fontSize: "12px",
                boxShadow: "0 4px 16px rgba(3,60,115,0.12)",
              }}
              labelStyle={{ color: "#1271c2" }}
            />
            <Line
              type="monotone"
              dataKey="value"
              stroke="#1A82D6"
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4, fill: "#47a3e8" }}
              connectNulls
            />
          </LineChart>
        </ResponsiveContainer>
      )}
    </Card>
  );
}
