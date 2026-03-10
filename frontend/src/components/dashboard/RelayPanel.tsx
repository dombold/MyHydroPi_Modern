import Card from "../ui/Card";
import RelayCard from "./RelayCard";
import { useRelays } from "../../hooks/useRelays";

export default function RelayPanel() {
  const { data, isLoading } = useRelays();

  return (
    <Card>
      <div className="px-4 py-3 border-b border-hydropi-100">
        <h2 className="text-base font-display text-hydropi-800">Power Outlets</h2>
      </div>

      {isLoading ? (
        <div className="py-8 text-center text-hydropi-400 text-sm">Loading…</div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-xs text-hydropi-500 uppercase tracking-wide border-b border-hydropi-100 bg-hydropi-50/60">
                <th className="py-2 px-4 text-left font-medium">Outlet</th>
                <th className="py-2 px-4 text-left font-medium">State</th>
                <th className="py-2 px-4 text-left font-medium">Mode</th>
                <th className="py-2 px-4 text-left font-medium">Control</th>
              </tr>
            </thead>
            <tbody>
              {data?.relays.map((r) => (
                <RelayCard key={r.id} relay={r} />
              ))}
            </tbody>
          </table>
        </div>
      )}
    </Card>
  );
}
