"""
Sensor reading module — supports DS18B20 (1-wire) and Atlas Scientific (I2C).
Returns None on error instead of 0 (0 is a valid ORP reading direction).
"""

import fcntl
import io
import time
from typing import Protocol

from loguru import logger

from services.config import AppConfig, SensorConfig

# Atlas Scientific I2C constants
_ATLAS_LONG_TIMEOUT = 1.5
_ATLAS_SHORT_TIMEOUT = 0.3
_DEFAULT_BUS = 1
_MAX_RETRIES = 3


class AtlasI2C:
    """I2C communication helper for Atlas Scientific sensors."""

    def __init__(self, address: int, bus: int = _DEFAULT_BUS) -> None:
        self.address = address
        self.bus = bus
        self._device: io.FileIO | None = None

    def _open(self) -> None:
        self._device = io.open(f"/dev/i2c-{self.bus}", "r+b", buffering=0)
        fcntl.ioctl(self._device, 0x0703, self.address)

    def _close(self) -> None:
        if self._device:
            self._device.close()
            self._device = None

    def query(self, command: str) -> str | None:
        try:
            self._open()
            self._device.write(command.encode("ascii"))  # type: ignore[union-attr]
            if command.upper().startswith("R"):
                time.sleep(_ATLAS_LONG_TIMEOUT)
            else:
                time.sleep(_ATLAS_SHORT_TIMEOUT)
            data = self._device.read(31)  # type: ignore[union-attr]
            self._close()
            if data[0] != 1:
                logger.warning(f"Atlas I2C {self.address:#x}: bad response code {data[0]}")
                return None
            return data[1:].decode("ascii").strip("\x00")
        except (OSError, IOError) as exc:
            logger.warning(f"Atlas I2C {self.address:#x} communication error: {exc}")
            self._close()
            return None


# ── Public sensor read functions ──────────────────────────────────────────────

def read_1wire_temp(sensor: SensorConfig) -> float | None:
    """Read a DS18B20 temperature via the 1-wire filesystem interface."""
    if not sensor.ds18b20_file:
        logger.error("DS18B20 sensor config missing ds18b20_file path")
        return None
    try:
        with open(sensor.ds18b20_file) as fh:
            lines = fh.readlines()
        if lines[0].strip()[-3:] != "YES":
            logger.warning(f"DS18B20 {sensor.name}: CRC check failed")
            return None
        equals_pos = lines[1].find("t=")
        if equals_pos == -1:
            return None
        temp_c = float(lines[1][equals_pos + 2:]) / 1000.0
        return round(temp_c, sensor.accuracy)
    except (FileNotFoundError, IndexError, ValueError, IOError) as exc:
        logger.warning(f"DS18B20 read error ({sensor.name}): {exc}")
        return None


def read_atlas_temp(sensor: SensorConfig, ref_temp: float | None) -> float | None:
    """Read an Atlas Scientific temperature sensor."""
    if sensor.i2c is None:
        return None
    device = AtlasI2C(sensor.i2c)
    raw = device.query("R")
    if raw is None:
        return None
    try:
        return round(float(raw), sensor.accuracy)
    except ValueError as exc:
        logger.warning(f"Atlas temp parse error ({sensor.name}): {exc}")
        return None


def read_atlas_sensor(sensor: SensorConfig, ref_temp: float | None) -> float | None:
    """Read a generic Atlas Scientific sensor (pH, ORP)."""
    if sensor.i2c is None:
        return None
    device = AtlasI2C(sensor.i2c)

    # Set reference temperature if available
    if ref_temp is not None:
        device.query(f"T,{ref_temp}")

    raw = device.query("R")
    if raw is None:
        return None
    try:
        return round(float(raw), sensor.accuracy)
    except ValueError as exc:
        logger.warning(f"Atlas sensor parse error ({sensor.name}): {exc}")
        return None


def read_atlas_ec(sensor: SensorConfig, ref_temp: float | None) -> float | None:
    """Read Atlas Scientific EC sensor and convert to PPM."""
    if sensor.i2c is None:
        return None
    device = AtlasI2C(sensor.i2c)

    if ref_temp is not None:
        device.query(f"T,{ref_temp}")

    raw = device.query("R")
    if raw is None:
        return None
    try:
        ec_value = float(raw)
        if sensor.ppm_multiplier:
            ec_value = ec_value * sensor.ppm_multiplier
        return round(ec_value, sensor.accuracy)
    except ValueError as exc:
        logger.warning(f"Atlas EC parse error ({sensor.name}): {exc}")
        return None


def read_all_sensors(config: AppConfig) -> list[tuple[str, float]]:
    """
    Read every connected sensor in config order.
    Returns a list of (column_name, value) pairs (None values are excluded).
    """
    ref_temp: float | None = None
    results: list[tuple[str, float]] = []

    _readers = {
        "1_wire_temp": lambda s: read_1wire_temp(s),
        "atlas_scientific_temp": lambda s: read_atlas_temp(s, ref_temp),
        "atlas_scientific": lambda s: read_atlas_sensor(s, ref_temp),
        "atlas_scientific_ec": lambda s: read_atlas_ec(s, ref_temp),
    }

    for key, sensor in config.sensors.items():
        if not sensor.is_connected:
            continue
        reader = _readers.get(sensor.sensor_type)
        if reader is None:
            logger.warning(f"Unknown sensor type '{sensor.sensor_type}' for '{key}'")
            continue

        value = reader(sensor)
        if value is not None:
            results.append((sensor.name, value))
            if sensor.is_ref:
                ref_temp = value
                logger.debug(f"Reference temp set to {ref_temp}°C from {sensor.name}")
        else:
            logger.warning(f"No reading from sensor '{sensor.name}' — skipping this cycle")

    return results
