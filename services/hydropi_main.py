"""
HydroPi daemon main loop.
Replaces Hydropi_Main.py with proper signal handling, typed config, and loguru logging.

Run as:
    python -m services.hydropi_main
"""

import sys
import time
from datetime import datetime
from pathlib import Path

from loguru import logger

from services.app_state import AppState
from services.config import build_default_config
from services.database import (
    build_engine,
    create_database,
    create_tables,
    get_settings,
    log_sensor_readings,
    remove_excess_entries,
    reset_pause_readings,
)
from services.email_manager import check_and_alert
from services.power_manager import install_shutdown_handler, process_relays, setup_gpio
from services.sensor_manager import read_all_sensors


def _configure_logging(log_file: str, log_level: str) -> None:
    logger.remove()
    logger.add(sys.stderr, level=log_level, format="{time} | {level} | {message}")
    try:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        logger.add(log_file, level=log_level, rotation="10 MB", retention="30 days")
    except OSError as exc:
        logger.warning(f"Cannot write to log file {log_file}: {exc}")


def main() -> None:
    config = build_default_config()
    _configure_logging(config.log_file, config.log_level)
    logger.info("HydroPi daemon starting...")

    # Install signal handlers before GPIO setup
    install_shutdown_handler(config)

    # Initialise database
    create_database(config)
    engine = build_engine(config)
    create_tables(engine, config)
    remove_excess_entries(engine, config)

    # Setup GPIO
    setup_gpio(config)

    # Runtime state
    state = AppState()
    state.set_time_between_readings(config.read_sensor_delay)
    state.set_sensor_ref_time(datetime.now())

    logger.info("Startup complete. Entering main loop.")

    loop_count = 0

    while True:
        time.sleep(1)
        loop_count += 1

        # ── Relay control (every second) ──────────────────────────────────────
        try:
            process_relays(engine, config)
        except Exception as exc:
            logger.error(f"Relay processing error: {exc}")

        # ── Sensor reading (every read_sensor_delay seconds) ──────────────────
        elapsed = (datetime.now() - state.sensor_ref_time).total_seconds()
        if elapsed < state.time_between_readings:
            continue

        state.set_sensor_ref_time(datetime.now())

        # Load current settings from DB (may have been updated via web UI)
        db_settings = get_settings(engine)
        if db_settings:
            new_delay = db_settings.get("read_sensor_delay", config.read_sensor_delay)
            state.set_time_between_readings(int(new_delay))

        # Check pause flag
        if db_settings.get("pause_readings"):
            if state.new_pause:
                logger.info("Sensor readings paused by web UI.")
                state.set_new_pause(False, start_time=datetime.now())
            # Check if pause duration has expired
            if state.pause_start_time is not None:
                pause_elapsed = (datetime.now() - state.pause_start_time).total_seconds()
                if pause_elapsed >= config.pause_reset_delay:
                    reset_pause_readings(engine)
                    state.set_new_pause(True)
                    logger.info("Pause period expired — resuming sensor readings.")
            continue

        state.set_new_pause(True)

        # Read sensors
        logger.debug("Reading sensors...")
        try:
            readings = read_all_sensors(config)
        except Exception as exc:
            logger.error(f"Sensor read error: {exc}")
            continue

        if not readings:
            logger.warning("No sensor readings obtained this cycle.")
            continue

        # Log to database
        try:
            log_sensor_readings(engine, readings, config.sensor_column_whitelist)
        except Exception as exc:
            logger.error(f"Failed to log sensor readings: {exc}")

        # Check alert thresholds and send email if needed
        try:
            check_and_alert(config, readings, db_settings, state)
        except Exception as exc:
            logger.error(f"Alert check error: {exc}")

        logger.info(
            f"Cycle complete | "
            f"{len(readings)} readings | "
            f"alert={'YES' if state.alert_check else 'no'}"
        )


if __name__ == "__main__":
    main()
