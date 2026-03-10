"""
Thread-safe runtime state for the HydroPi daemon.
Replaces the module-level mutable globals in the original hydropi_variables.py.
"""

import threading
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class AppState:
    _lock: threading.Lock = field(default_factory=threading.Lock, init=False, repr=False)

    # Set to True if any sensor reading is outside its alert thresholds
    alert_check: bool = False

    # Set to True once an alert email has been dispatched for the current incident
    email_sent: bool = False

    # True when sensor readings are not currently paused
    new_pause: bool = True

    # Reference time used to track sensor read intervals
    sensor_ref_time: datetime = field(default_factory=datetime.now)

    # Mirrors read_sensor_delay from settings; updated from DB at runtime
    time_between_readings: int = 300

    # When the last alert email was sent (None = never)
    email_sent_time: datetime | None = None

    # When the current pause period started (None = not paused)
    pause_start_time: datetime | None = None

    # ── Thread-safe setters ───────────────────────────────────────────────────

    def set_alert_check(self, value: bool) -> None:
        with self._lock:
            self.alert_check = value

    def set_email_sent(self, value: bool, sent_time: datetime | None = None) -> None:
        with self._lock:
            self.email_sent = value
            if sent_time is not None:
                self.email_sent_time = sent_time

    def set_new_pause(self, value: bool, start_time: datetime | None = None) -> None:
        with self._lock:
            self.new_pause = value
            if start_time is not None:
                self.pause_start_time = start_time

    def set_time_between_readings(self, value: int) -> None:
        with self._lock:
            self.time_between_readings = value

    def set_sensor_ref_time(self, value: datetime) -> None:
        with self._lock:
            self.sensor_ref_time = value

    # ── Thread-safe readers ───────────────────────────────────────────────────

    def snapshot(self) -> dict:
        """Return a consistent copy of state for logging / inspection."""
        with self._lock:
            return {
                "alert_check": self.alert_check,
                "email_sent": self.email_sent,
                "new_pause": self.new_pause,
                "time_between_readings": self.time_between_readings,
                "email_sent_time": self.email_sent_time,
                "pause_start_time": self.pause_start_time,
            }
