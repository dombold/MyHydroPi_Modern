import SensorPanel from "../components/dashboard/SensorPanel";
import RelayPanel from "../components/dashboard/RelayPanel";

export default function Dashboard() {
  return (
    <div className="space-y-6">
      <SensorPanel />
      <RelayPanel />
    </div>
  );
}
