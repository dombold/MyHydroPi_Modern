import { useState } from "react";
import Button from "../ui/Button";

interface Props {
  id: string;
  label: string;
  unit?: string;
  poolSize: number;
  calculate: (testValue: number, poolSize: number) => string;
}

export default function ChemicalRow({ id, label, unit = "mg/L", poolSize, calculate }: Props) {
  const [value, setValue] = useState("");
  const [result, setResult] = useState<string | null>(null);

  const handleCheck = () => {
    const num = parseFloat(value);
    if (isNaN(num)) return;
    setResult(calculate(num, poolSize));
    setValue("");
  };

  const isOk = result === "OK";

  return (
    <tr className="border-b border-hydropi-100 last:border-0 hover:bg-hydropi-50/70 transition-[background-color] duration-150">
      <td className="py-3 px-4 font-medium text-hydropi-900 whitespace-nowrap">
        {label}
        <span className="ml-1 text-xs text-hydropi-400">({unit})</span>
      </td>
      <td className="py-3 px-4">
        <input
          type="number"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleCheck()}
          placeholder="Test reading"
          className={[
            "w-32 bg-white border border-hydropi-300 rounded px-3 py-1.5",
            "text-hydropi-900 text-sm",
            "focus:outline-none focus:ring-2 focus:ring-hydropi-500 focus:border-hydropi-500",
            "placeholder:text-hydropi-400",
            "shadow-[0_1px_2px_rgba(3,60,115,0.06)]",
          ].join(" ")}
        />
      </td>
      <td className="py-3 px-4">
        <Button size="sm" onClick={handleCheck} disabled={!value}>
          Check
        </Button>
      </td>
      <td className="py-3 px-4 text-sm">
        {result == null ? (
          <span className="text-hydropi-400">—</span>
        ) : isOk ? (
          <span className="text-green-700 font-semibold">✓ OK</span>
        ) : (
          <span className="text-amber-700 font-medium">{result}</span>
        )}
      </td>
    </tr>
  );
}
