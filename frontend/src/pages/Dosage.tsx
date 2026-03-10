import ChemicalRow from "../components/dosage/ChemicalRow";
import Card from "../components/ui/Card";
import Button from "../components/ui/Button";
import { useSettings } from "../hooks/useSettings";

// Chemical calculation functions (ported from hydropi.js)
const calculators = {
  cya: (test: number, pool: number) => {
    if (test >= 30 && test <= 50) return "OK";
    if (test > 50) return "Remove some water and add Fresh Water";
    return `Add ${((40 - test) * 0.001 * pool).toFixed(0)}g of Stabiliser`;
  },
  ta: (test: number, pool: number) => {
    if (test >= 80 && test <= 150) return "OK";
    if (test > 150) return "Remove some water and add Fresh Water";
    return `Add ${((115 - test) * 0.001 * pool).toFixed(0)}g of AlkPlus`;
  },
  tcl: (test: number, pool: number) => {
    if (test >= 3 && test <= 5) return "OK";
    if (test > 5) return "Remove some water and add Fresh Water";
    return `Add ${((4 - test) * 0.001 * pool).toFixed(0)}g of Chlorine`;
  },
  ch: (test: number, pool: number) => {
    if (test >= 150 && test <= 250) return "OK";
    if (test > 250) return "Remove some water and add Fresh Water";
    return `Add ${((200 - test) * 0.001 * pool).toFixed(0)}g of CalPlus`;
  },
};

export default function Dosage() {
  const { data: settings, isLoading } = useSettings();
  const poolSize = settings?.pool_size ?? 27000;

  if (isLoading) return <p className="text-hydropi-400 text-sm">Loading…</p>;

  return (
    <div className="space-y-4">
      <p className="text-sm text-hydropi-600">
        Pool size: <span className="text-hydropi-900 font-semibold">{poolSize.toLocaleString()} L</span>
        {" · "}Enter your test strip readings below.
      </p>

      <Card>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-xs text-hydropi-500 uppercase tracking-wide border-b border-hydropi-100 bg-hydropi-50/60">
                <th className="py-2 px-4 text-left">Chemical</th>
                <th className="py-2 px-4 text-left">Test Value</th>
                <th className="py-2 px-4 text-left"></th>
                <th className="py-2 px-4 text-left">Action</th>
              </tr>
            </thead>
            <tbody>
              <ChemicalRow
                id="cya"
                label="Stabiliser (CYA)"
                unit="mg/L"
                poolSize={poolSize}
                calculate={calculators.cya}
              />
              <ChemicalRow
                id="ta"
                label="Total Alkalinity"
                unit="mg/L"
                poolSize={poolSize}
                calculate={calculators.ta}
              />
              <ChemicalRow
                id="tcl"
                label="Total Chlorine"
                unit="mg/L"
                poolSize={poolSize}
                calculate={calculators.tcl}
              />
              <ChemicalRow
                id="ch"
                label="Calcium Hardness"
                unit="mg/L"
                poolSize={poolSize}
                calculate={calculators.ch}
              />
            </tbody>
          </table>
        </div>
      </Card>

      <p className="text-xs text-hydropi-500">
        Ranges: CYA 30–50 · Total Alkalinity 80–150 · Total Chlorine 3–5 · Calcium Hardness 150–250 (all mg/L)
      </p>
    </div>
  );
}
