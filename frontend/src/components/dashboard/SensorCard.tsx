import type { SensorReading } from "../../api/sensors";

interface Props {
  reading: SensorReading;
}

export default function SensorCard({ reading }: Props) {
  const { display_name, value, avg_24h, unit, in_alert } = reading;

  const fmt = (v: number | null) =>
    v == null ? "—" : `${v}${unit ? "\u202F" + unit : ""}`;

  return (
    <tr
      className={[
        "border-b border-hydropi-100 last:border-0",
        "transition-[background-color] duration-150",
        in_alert ? "bg-red-50" : "hover:bg-hydropi-50/70",
      ].join(" ")}
    >
      <td className="py-3 px-4 font-medium text-hydropi-900 whitespace-nowrap">
        {display_name}
        {in_alert && (
          <span className="ml-2 text-xs text-red-600 font-semibold">⚠ Alert</span>
        )}
      </td>
      <td className={[
        "py-3 px-4 text-right font-mono text-base tabular-nums font-semibold",
        in_alert ? "text-red-700" : "text-hydropi-800",
      ].join(" ")}>
        {fmt(value)}
      </td>
      <td className="py-3 px-4 text-right font-mono text-sm tabular-nums text-hydropi-500">
        {fmt(avg_24h)}
      </td>
      <td className="py-3 px-4 text-right text-xs text-hydropi-400 whitespace-nowrap">
        {reading.alert_high != null && reading.alert_low != null
          ? `${reading.alert_low} – ${reading.alert_high}`
          : "—"}
      </td>
    </tr>
  );
}
