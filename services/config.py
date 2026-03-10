"""
Typed configuration for the HydroPi daemon services.
Replaces hydropi_variables.py — all secrets read from .env.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


# ── Sensor config ─────────────────────────────────────────────────────────────

@dataclass
class SensorConfig:
    sensor_type: str       # "1_wire_temp" | "atlas_scientific_temp" | "atlas_scientific" | "atlas_scientific_ec"
    name: str              # DB column name
    is_connected: bool
    is_ref: bool           # True = reference temperature sensor
    accuracy: int          # decimal places to round to
    test_for_alert: bool
    upper_alert_name: str  # settings table column
    upper_alert_value: float
    lower_alert_name: str
    lower_alert_value: float
    i2c: int | None = None
    ds18b20_file: str | None = None
    ppm_multiplier: float | None = None  # EC → PPM conversion factor


# ── App-level config ──────────────────────────────────────────────────────────

@dataclass
class AppConfig:
    db_host: str = field(default_factory=lambda: os.getenv("DB_HOST", "localhost"))
    db_user: str = field(default_factory=lambda: os.getenv("DB_USER", "hydropi_user"))
    db_password: str = field(default_factory=lambda: os.getenv("DB_PASSWORD", ""))
    db_name: str = field(default_factory=lambda: os.getenv("DB_NAME", "hydropidb"))

    email_from: str = field(default_factory=lambda: os.getenv("EMAIL_FROM", ""))
    email_password: str = field(default_factory=lambda: os.getenv("EMAIL_PASSWORD", ""))
    email_server: str = field(default_factory=lambda: os.getenv("EMAIL_SERVER", "smtp.gmail.com"))
    email_port: int = field(default_factory=lambda: int(os.getenv("EMAIL_PORT", "587")))
    email_to: str = field(default_factory=lambda: os.getenv("EMAIL_TO", ""))

    log_file: str = field(default_factory=lambda: os.getenv("LOG_FILE", "/var/log/hydropi/daemon.log"))
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))

    # Pool settings (can be overridden in DB, but defaults here for first run)
    pool_size: int = 27000
    read_sensor_delay: int = 300    # seconds between sensor reads
    email_reset_delay: int = 172800 # 2 days
    pause_reset_delay: int = 1800   # 30 minutes
    offset_percent: float = 2.0     # alert threshold buffer

    # Hardware
    output_pins: list[int] = field(default_factory=lambda: [22, 23, 24, 25])
    num_dt_pairs: list[int] = field(default_factory=lambda: [4, 3, 2, 1])

    # Sensor registry (key = logical name, value = SensorConfig)
    sensors: dict[str, SensorConfig] = field(default_factory=dict)

    @property
    def relay_count(self) -> list[int]:
        return list(range(1, len(self.output_pins) + 1))

    @property
    def relay_timer_names(self) -> list[str]:
        return [f"relay_{n}_timer" for n in self.relay_count]

    @property
    def sensor_column_whitelist(self) -> set[str]:
        """Safe set of column names — used to prevent SQL injection in dynamic queries."""
        return {s.name for s in self.sensors.values() if s.is_connected}


def build_default_config() -> AppConfig:
    """
    Returns a default AppConfig pre-populated with the standard sensor set.
    Edit sensor types / I2C addresses / GPIO pins here for your hardware.
    """
    config = AppConfig()
    config.sensors = {
        "temp_1": SensorConfig(
            sensor_type="1_wire_temp",
            name="ds18b20_temp",
            is_connected=True,
            is_ref=False,
            ds18b20_file="/sys/bus/w1/devices/28-XXXXXXXXXXXX/w1_slave",
            accuracy=1,
            test_for_alert=False,
            upper_alert_name="ds18b20_temp_hi",
            upper_alert_value=50.0,
            lower_alert_name="ds18b20_temp_low",
            lower_alert_value=10.0,
        ),
        "atlas_sensor_1": SensorConfig(
            sensor_type="atlas_scientific_temp",
            name="atlas_temp",
            is_connected=True,
            is_ref=True,
            i2c=102,
            accuracy=1,
            test_for_alert=False,
            upper_alert_name="atlas_temp_hi",
            upper_alert_value=40.0,
            lower_alert_name="atlas_temp_low",
            lower_alert_value=25.0,
        ),
        "atlas_sensor_3": SensorConfig(
            sensor_type="atlas_scientific_ec",
            name="ec",
            is_connected=True,
            is_ref=False,
            i2c=100,
            accuracy=0,
            ppm_multiplier=0.67,
            test_for_alert=True,
            upper_alert_name="ec_hi",
            upper_alert_value=6000.0,
            lower_alert_name="ec_low",
            lower_alert_value=4500.0,
        ),
        "atlas_sensor_4": SensorConfig(
            sensor_type="atlas_scientific",
            name="ph",
            is_connected=True,
            is_ref=False,
            i2c=99,
            accuracy=2,
            test_for_alert=True,
            upper_alert_name="ph_hi",
            upper_alert_value=7.4,
            lower_alert_name="ph_low",
            lower_alert_value=7.0,
        ),
        "atlas_sensor_5": SensorConfig(
            sensor_type="atlas_scientific",
            name="orp",
            is_connected=True,
            is_ref=False,
            i2c=98,
            accuracy=0,
            test_for_alert=True,
            upper_alert_name="orp_hi",
            upper_alert_value=700.0,
            lower_alert_name="orp_low",
            lower_alert_value=550.0,
        ),
    }
    return config
