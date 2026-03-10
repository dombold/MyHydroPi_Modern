import { useState } from "react";
import Card from "../ui/Card";
import Button from "../ui/Button";
import ConfirmDialog from "../ui/ConfirmDialog";
import SensorCard from "./SensorCard";
import { useSensors, usePauseSensors, useDeleteSensorHistory } from "../../hooks/useSensors";

export default function SensorPanel() {
  const { data, isLoading, dataUpdatedAt } = useSensors();
  const pause = usePauseSensors();
  const deleteHistory = useDeleteSensorHistory();

  const [deleteDialog, setDeleteDialog] = useState<{ open: boolean; days: number }>({
    open: false,
    days: 30,
  });

  const lastUpdated = dataUpdatedAt
    ? new Date(dataUpdatedAt).toLocaleTimeString()
    : null;

  return (
    <Card>
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-hydropi-100">
        <h2 className="text-base font-display text-hydropi-800">Sensor Readings</h2>
        <div className="flex items-center gap-2">
          {data?.pause_active && (
            <span className="text-xs text-amber-700 font-semibold">Readings paused</span>
          )}
          {lastUpdated && (
            <span className="text-xs text-hydropi-400">Updated {lastUpdated}</span>
          )}
          <Button
            variant="secondary"
            size="sm"
            loading={pause.isPending}
            onClick={() => pause.mutate()}
            disabled={data?.pause_active}
          >
            Pause
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setDeleteDialog({ open: true, days: 30 })}
          >
            Delete Old
          </Button>
        </div>
      </div>

      {/* Table */}
      {isLoading ? (
        <div className="py-8 text-center text-hydropi-400 text-sm">Loading…</div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-xs text-hydropi-500 uppercase tracking-wide border-b border-hydropi-100 bg-hydropi-50/60">
                <th className="py-2 px-4 text-left font-medium">Sensor</th>
                <th className="py-2 px-4 text-right font-medium">Current</th>
                <th className="py-2 px-4 text-right font-medium">24h Avg</th>
                <th className="py-2 px-4 text-right font-medium">Safe Range</th>
              </tr>
            </thead>
            <tbody>
              {data?.readings.map((r) => (
                <SensorCard key={r.name} reading={r} />
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Delete dialog */}
      <ConfirmDialog
        open={deleteDialog.open}
        danger
        title="Delete Sensor History"
        message={`Delete all records older than ${deleteDialog.days} days? This cannot be undone.`}
        confirmLabel="Delete"
        onConfirm={() => {
          deleteHistory.mutate(deleteDialog.days);
          setDeleteDialog((d) => ({ ...d, open: false }));
        }}
        onCancel={() => setDeleteDialog((d) => ({ ...d, open: false }))}
      />
    </Card>
  );
}
