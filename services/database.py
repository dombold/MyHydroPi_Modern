"""
SQLAlchemy Core database layer for the HydroPi daemon.
Replaces database_manager.py — uses a connection pool instead of per-call connects.
"""

from datetime import datetime
from functools import lru_cache

from loguru import logger
from sqlalchemy import create_engine, pool, text
from sqlalchemy.engine import Engine

from services.config import AppConfig


def build_engine(config: AppConfig) -> Engine:
    url = (
        f"mysql+mysqlconnector://{config.db_user}:{config.db_password}"
        f"@{config.db_host}/{config.db_name}"
    )
    return create_engine(
        url,
        poolclass=pool.QueuePool,
        pool_size=3,
        max_overflow=1,
        pool_pre_ping=True,
        pool_recycle=3600,
    )


# ── Schema initialisation ─────────────────────────────────────────────────────

def create_database(config: AppConfig) -> None:
    url = f"mysql+mysqlconnector://{config.db_user}:{config.db_password}@{config.db_host}/"
    engine = create_engine(url)
    try:
        with engine.connect() as conn:
            conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{config.db_name}`"))
            conn.commit()
        logger.info(f"Database '{config.db_name}' ready.")
    except Exception as exc:
        logger.error(f"Failed to create database: {exc}")
    finally:
        engine.dispose()


def create_tables(engine: Engine, config: AppConfig) -> None:
    """Create all required tables and seed default data if absent."""
    with engine.connect() as conn:
        _create_relay_tables(conn, config)
        _create_timer_override(conn, config)
        _create_sensors_table(conn, config)
        _create_settings_table(conn, config)
        conn.commit()
    logger.info("Database tables verified / created.")


def _create_relay_tables(conn, config: AppConfig) -> None:
    for idx, table in enumerate(config.relay_timer_names):
        conn.execute(text(
            f"CREATE TABLE IF NOT EXISTS `{table}` "
            "(pk INT UNSIGNED PRIMARY KEY, "
            "starttime DATETIME DEFAULT NULL, "
            "stoptime DATETIME DEFAULT NULL)"
        ))
        for pk in range(1, config.num_dt_pairs[idx] + 1):
            conn.execute(text(
                f"INSERT IGNORE INTO `{table}` (pk, starttime, stoptime) VALUES (:pk, NULL, NULL)"
            ), {"pk": pk})


def _create_timer_override(conn, config: AppConfig) -> None:
    conn.execute(text(
        "CREATE TABLE IF NOT EXISTS timer_override (pk INT UNSIGNED PRIMARY KEY)"
    ))
    conn.execute(text("INSERT IGNORE INTO timer_override (pk) VALUES (1)"))
    conn.execute(text("INSERT IGNORE INTO timer_override (pk) VALUES (2)"))

    for n in config.relay_count:
        col = f"relay_{n}"
        result = conn.execute(text(
            f"SELECT `{col}` FROM timer_override WHERE pk = 1"
        ))
        if result.fetchone() is None:
            conn.execute(text(f"ALTER TABLE timer_override ADD `{col}` VARCHAR(5)"))
            conn.execute(text(
                f"UPDATE IGNORE timer_override SET `{col}` = 'off' WHERE pk = 1"
            ))
        result2 = conn.execute(text(
            f"SELECT `{col}` FROM timer_override WHERE pk = 2"
        ))
        if result2.fetchone() is None:
            conn.execute(text(
                f"UPDATE IGNORE timer_override SET `{col}` = 'False' WHERE pk = 2"
            ))


def _create_sensors_table(conn, config: AppConfig) -> None:
    conn.execute(text(
        "CREATE TABLE IF NOT EXISTS sensors (timestamp DATETIME)"
    ))
    for sensor in config.sensors.values():
        if sensor.is_connected:
            result = conn.execute(text(
                f"SELECT `{sensor.name}` FROM sensors LIMIT 1"
            ))
            if result.fetchone() is None:
                conn.execute(text(
                    f"ALTER TABLE sensors ADD `{sensor.name}` DECIMAL(10,2)"
                ))


def _create_settings_table(conn, config: AppConfig) -> None:
    conn.execute(text(
        "CREATE TABLE IF NOT EXISTS settings (pk TINYINT(1) UNSIGNED PRIMARY KEY)"
    ))
    conn.execute(text("INSERT IGNORE INTO settings (pk) VALUES (1)"))

    for sensor in config.sensors.values():
        result = conn.execute(text(
            f"SELECT `{sensor.upper_alert_name}` FROM settings LIMIT 1"
        ))
        if result.fetchone() is None:
            conn.execute(text(
                f"ALTER TABLE settings ADD (`{sensor.upper_alert_name}` DECIMAL(10,2), "
                f"`{sensor.lower_alert_name}` DECIMAL(10,2))"
            ))
            conn.execute(text(
                f"UPDATE IGNORE settings "
                f"SET `{sensor.upper_alert_name}` = :hi, `{sensor.lower_alert_name}` = :lo "
                "WHERE pk = 1"
            ), {"hi": sensor.upper_alert_value, "lo": sensor.lower_alert_value})

    _ensure_settings_misc(conn, config)


def _ensure_settings_misc(conn, config: AppConfig) -> None:
    misc = {
        "read_sensor_delay": ("INT(10)", config.read_sensor_delay),
        "email_reset_delay": ("INT(10)", config.email_reset_delay),
        "pause_reset_delay": ("INT(10)", config.pause_reset_delay),
        "offset_percent":    ("DECIMAL(10,2)", config.offset_percent),
        "pause_readings":    ("BOOLEAN", 0),
        "pool_size":         ("INT(10)", config.pool_size),
        "to_email":          ("VARCHAR(254)", config.email_to),
    }
    for col, (col_type, default) in misc.items():
        result = conn.execute(text(f"SELECT `{col}` FROM settings LIMIT 1"))
        if result.fetchone() is None:
            conn.execute(text(f"ALTER TABLE settings ADD `{col}` {col_type}"))
            if isinstance(default, str):
                conn.execute(text(
                    f"UPDATE IGNORE settings SET `{col}` = :v WHERE pk = 1"
                ), {"v": default})
            else:
                conn.execute(text(
                    f"UPDATE IGNORE settings SET `{col}` = {default} WHERE pk = 1"
                ))


def remove_excess_entries(engine: Engine, config: AppConfig) -> None:
    """Remove DB columns/rows that no longer exist in config."""
    with engine.connect() as conn:
        # Remove excess relay columns
        result = conn.execute(text(
            "SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS "
            "WHERE TABLE_NAME = 'timer_override'"
        ))
        col_count = int(result.scalar()) - 1  # minus pk
        while col_count > len(config.output_pins):
            col = f"relay_{col_count}"
            conn.execute(text(f"ALTER TABLE timer_override DROP `{col}`"))
            conn.execute(text(f"DROP TABLE IF EXISTS `{col}_timer`"))
            col_count -= 1

        # Remove excess timer pairs
        for idx, table in enumerate(config.relay_timer_names):
            conn.execute(text(
                f"DELETE FROM `{table}` WHERE pk > :max_pairs"
            ), {"max_pairs": config.num_dt_pairs[idx]})

        # Remove disconnected sensor columns
        for sensor in config.sensors.values():
            if not sensor.is_connected:
                try:
                    conn.execute(text(f"ALTER TABLE sensors DROP `{sensor.name}`"))
                    conn.execute(text(
                        f"ALTER TABLE settings "
                        f"DROP COLUMN `{sensor.upper_alert_name}`, "
                        f"DROP COLUMN `{sensor.lower_alert_name}`"
                    ))
                except Exception as exc:
                    logger.warning(f"Could not remove column {sensor.name}: {exc}")

        conn.commit()


# ── Runtime queries ───────────────────────────────────────────────────────────

def log_sensor_readings(engine: Engine, readings: list[tuple[str, float]], whitelist: set[str]) -> None:
    """Insert a new sensor row with timestamp then update each column value."""
    with engine.connect() as conn:
        conn.execute(text("INSERT INTO sensors (timestamp) VALUES (now())"))
        result = conn.execute(text("SELECT MAX(timestamp) FROM sensors"))
        last_ts = result.scalar().strftime("%Y-%m-%d %H:%M:%S")

        for name, value in readings:
            if name not in whitelist:
                logger.warning(f"Column '{name}' not in whitelist — skipping")
                continue
            conn.execute(
                text(f"UPDATE sensors SET `{name}` = :val WHERE timestamp = :ts"),
                {"val": value, "ts": last_ts},
            )
        conn.commit()
    logger.debug(f"Logged {len(readings)} sensor readings at {last_ts}")


def get_settings(engine: Engine) -> dict:
    with engine.connect() as conn:
        row = conn.execute(text("SELECT * FROM settings WHERE pk = 1")).mappings().first()
    if row is None:
        return {}
    data = dict(row)
    if data.get("offset_percent") is not None:
        data["offset_percent"] = float(data["offset_percent"]) / 100
    return data


def reset_pause_readings(engine: Engine) -> None:
    with engine.connect() as conn:
        conn.execute(text("UPDATE IGNORE settings SET pause_readings = 0 WHERE pk = 1"))
        conn.commit()


def read_timer_overrides(engine: Engine) -> dict | None:
    with engine.connect() as conn:
        row = conn.execute(text("SELECT * FROM timer_override WHERE pk = 1")).mappings().first()
    return dict(row) if row else None


def get_relay_timer_pairs(engine: Engine, table: str, row_pk: int) -> tuple | None:
    with engine.connect() as conn:
        row = conn.execute(
            text(f"SELECT * FROM `{table}` WHERE pk = :pk"),
            {"pk": row_pk},
        ).first()
    return row


def update_relay_state(engine: Engine, relay_col: str, state: bool) -> None:
    with engine.connect() as conn:
        conn.execute(
            text(f"UPDATE IGNORE timer_override SET `{relay_col}` = :state WHERE pk = 2"),
            {"state": str(state)},
        )
        conn.commit()
