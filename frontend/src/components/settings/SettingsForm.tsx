import { useState, useEffect } from "react";
import Button from "../ui/Button";
import { useSettings, useUpdateSettings } from "../../hooks/useSettings";
import type { AppSettings } from "../../api/settings";

// Field definitions for the dynamic form
const ALERT_FIELDS: Array<{ key: keyof AppSettings; label: string }> = [
  { key: "ds18b20_temp_hi", label: "Air Temp High (°C)" },
  { key: "ds18b20_temp_low", label: "Air Temp Low (°C)" },
  { key: "atlas_temp_hi", label: "Pool Temp High (°C)" },
  { key: "atlas_temp_low", label: "Pool Temp Low (°C)" },
  { key: "ec_hi", label: "Salinity High (ppm)" },
  { key: "ec_low", label: "Salinity Low (ppm)" },
  { key: "ph_hi", label: "pH High" },
  { key: "ph_low", label: "pH Low" },
  { key: "orp_hi", label: "ORP High (mV)" },
  { key: "orp_low", label: "ORP Low (mV)" },
];

const SYSTEM_FIELDS: Array<{ key: keyof AppSettings; label: string }> = [
  { key: "read_sensor_delay", label: "Sensor Interval (s)" },
  { key: "email_reset_delay", label: "Email Reset Delay (s)" },
  { key: "pause_reset_delay", label: "Pause Duration (s)" },
  { key: "pool_size", label: "Pool Size (L)" },
  { key: "to_email", label: "Alert Email Address" },
];

export default function SettingsForm() {
  const { data, isLoading } = useSettings();
  const updateMutation = useUpdateSettings();

  const [values, setValues] = useState<Partial<AppSettings>>({});

  useEffect(() => {
    if (data) setValues(data);
  }, [data]);

  const handleChange = (key: keyof AppSettings, raw: string) => {
    const field = [...ALERT_FIELDS, ...SYSTEM_FIELDS].find((f) => f.key === key);
    if (!field) return;
    if (key === "to_email") {
      setValues((v) => ({ ...v, [key]: raw }));
    } else {
      const num = parseFloat(raw);
      setValues((v) => ({ ...v, [key]: isNaN(num) ? undefined : num }));
    }
  };

  const handleSave = () => {
    updateMutation.mutate(values);
  };

  if (isLoading) {
    return <p className="text-hydropi-400 text-sm">Loading settings…</p>;
  }

  return (
    <div className="space-y-8">
      <Section title="Alert Thresholds" fields={ALERT_FIELDS} values={values} onChange={handleChange} />
      <Section title="System Settings" fields={SYSTEM_FIELDS} values={values} onChange={handleChange} />

      <div className="flex items-center gap-3">
        <Button onClick={handleSave} loading={updateMutation.isPending}>
          Save Settings
        </Button>
        {updateMutation.isSuccess && (
          <span className="text-sm text-green-700 font-medium">Saved.</span>
        )}
        {updateMutation.isError && (
          <span className="text-sm text-red-700 font-medium">Save failed.</span>
        )}
      </div>
    </div>
  );
}

function Section({
  title,
  fields,
  values,
  onChange,
}: {
  title: string;
  fields: Array<{ key: keyof AppSettings; label: string }>;
  values: Partial<AppSettings>;
  onChange: (key: keyof AppSettings, val: string) => void;
}) {
  return (
    <div>
      <h3 className="text-sm font-display text-hydropi-700 uppercase tracking-wider mb-3">
        {title}
      </h3>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {fields.map(({ key, label }) => (
          <div key={key as string}>
            <label className="block text-xs font-medium text-hydropi-700 mb-1">{label}</label>
            <input
              type={key === "to_email" ? "email" : "number"}
              step="any"
              value={values[key] != null ? String(values[key]) : ""}
              onChange={(e) => onChange(key, e.target.value)}
              className={[
                "w-full bg-white border border-hydropi-300 rounded-lg px-3 py-2",
                "text-hydropi-900 text-sm",
                "focus:outline-none focus:ring-2 focus:ring-hydropi-500 focus:border-hydropi-500",
                "placeholder:text-hydropi-400",
                "shadow-[0_1px_2px_rgba(3,60,115,0.06)]",
              ].join(" ")}
            />
          </div>
        ))}
      </div>
    </div>
  );
}
