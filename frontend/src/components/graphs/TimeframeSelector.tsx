const OPTIONS = [
  { label: "1D", days: 1 },
  { label: "1W", days: 7 },
  { label: "1M", days: 30 },
  { label: "3M", days: 90 },
  { label: "6M", days: 180 },
  { label: "1Y", days: 365 },
];

interface Props {
  value: number;
  onChange: (days: number) => void;
}

export default function TimeframeSelector({ value, onChange }: Props) {
  return (
    <div className="flex gap-1 flex-wrap">
      {OPTIONS.map(({ label, days }) => (
        <button
          key={days}
          onClick={() => onChange(days)}
          className={[
            "px-3 py-1 rounded text-sm font-medium",
            "transition-[background-color,color] duration-150",
            "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-hydropi-400",
            value === days
              ? "bg-hydropi-700 text-white shadow-btn-primary"
              : "bg-white text-hydropi-700 border border-hydropi-200 hover:bg-hydropi-50 hover:border-hydropi-300 hover:text-hydropi-900 active:bg-hydropi-100",
          ].join(" ")}
        >
          {label}
        </button>
      ))}
    </div>
  );
}
