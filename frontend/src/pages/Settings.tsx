import { useState } from "react";
import Card from "../components/ui/Card";
import Button from "../components/ui/Button";
import ConfirmDialog from "../components/ui/ConfirmDialog";
import SettingsForm from "../components/settings/SettingsForm";
import { restartSystem, shutdownSystem } from "../api/system";

type SystemAction = "restart" | "shutdown" | null;

export default function Settings() {
  const [pendingAction, setPendingAction] = useState<SystemAction>(null);
  const [actionStatus, setActionStatus] = useState<string | null>(null);

  const handleConfirm = async () => {
    if (!pendingAction) return;
    try {
      const fn = pendingAction === "restart" ? restartSystem : shutdownSystem;
      await fn();
      setActionStatus(
        pendingAction === "restart"
          ? "Restarting… the page will reload shortly."
          : "Shutting down. It is now safe to turn off power."
      );
    } catch {
      setActionStatus("Command failed. Check the connection.");
    } finally {
      setPendingAction(null);
    }
  };

  return (
    <div className="space-y-8">
      <SettingsForm />

      {/* System Controls */}
      <Card className="p-4">
        <h3 className="text-sm font-display text-hydropi-400 uppercase tracking-wider mb-4">
          System Controls
        </h3>
        <div className="flex flex-wrap gap-3">
          <Button variant="secondary" onClick={() => setPendingAction("restart")}>
            Restart HydroPi
          </Button>
          <Button variant="danger" onClick={() => setPendingAction("shutdown")}>
            Shutdown HydroPi
          </Button>
        </div>
        {actionStatus && (
          <p className="mt-3 text-sm text-yellow-300">{actionStatus}</p>
        )}
      </Card>

      {/* Confirm dialogs */}
      <ConfirmDialog
        open={pendingAction === "restart"}
        title="Restart HydroPi?"
        message="The Raspberry Pi will reboot. The web interface will be unavailable for about 60 seconds."
        confirmLabel="Restart"
        onConfirm={handleConfirm}
        onCancel={() => setPendingAction(null)}
      />
      <ConfirmDialog
        open={pendingAction === "shutdown"}
        danger
        title="Shutdown HydroPi?"
        message="The Raspberry Pi will shut down completely. You will need physical access to turn it back on."
        confirmLabel="Shutdown"
        onConfirm={handleConfirm}
        onCancel={() => setPendingAction(null)}
      />
    </div>
  );
}
