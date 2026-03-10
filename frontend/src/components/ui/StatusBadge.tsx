type Status = "on" | "off" | "auto" | "alert" | "ok" | "paused";

const styles: Record<Status, string> = {
  on:     "bg-green-100 text-green-800 border-green-300",
  off:    "bg-red-100 text-red-800 border-red-300",
  auto:   "bg-amber-100 text-amber-800 border-amber-300",
  alert:  "bg-red-100 text-red-800 border-red-400",
  ok:     "bg-green-100 text-green-800 border-green-300",
  paused: "bg-hydropi-100 text-hydropi-700 border-hydropi-300",
};

const labels: Record<Status, string> = {
  on:     "On",
  off:    "Off",
  auto:   "Auto",
  alert:  "Alert",
  ok:     "OK",
  paused: "Paused",
};

interface Props {
  status: Status;
  className?: string;
}

export default function StatusBadge({ status, className = "" }: Props) {
  return (
    <span
      className={[
        "inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold",
        "border",
        styles[status],
        className,
      ].join(" ")}
    >
      {labels[status]}
    </span>
  );
}
