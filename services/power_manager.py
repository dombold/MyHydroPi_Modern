"""
GPIO relay control — reads timer_override from DB every second.
Three relay modes: 'on' (forced on), 'off' (forced off), 'auto' (timer-based).
"""

import signal
import sys
from datetime import datetime

from loguru import logger

from services.config import AppConfig

# Conditional GPIO import — not available on dev machines
try:
    import RPi.GPIO as GPIO
    _GPIO_AVAILABLE = True
except ImportError:
    _GPIO_AVAILABLE = False
    logger.warning("RPi.GPIO not available — relay control disabled (dev mode)")


def setup_gpio(config: AppConfig) -> None:
    if not _GPIO_AVAILABLE:
        return
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    for pin in config.output_pins:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.HIGH)  # HIGH = relay off (active-low board)


def set_relay(pin: int, state: bool) -> None:
    """Turn a relay on (True) or off (False)."""
    if not _GPIO_AVAILABLE:
        return
    GPIO.output(pin, GPIO.LOW if state else GPIO.HIGH)


def cleanup_gpio(config: AppConfig) -> None:
    if not _GPIO_AVAILABLE:
        return
    for pin in config.output_pins:
        GPIO.output(pin, GPIO.HIGH)  # Force all relays off before cleanup
    GPIO.cleanup()
    logger.info("GPIO cleaned up — all relays off.")


def install_shutdown_handler(config: AppConfig) -> None:
    """Register SIGTERM + SIGINT handlers that cleanly turn off all relays."""
    def _handler(signum, frame):
        logger.info(f"Shutdown signal received ({signum}), turning relays off.")
        cleanup_gpio(config)
        sys.exit(0)

    signal.signal(signal.SIGTERM, _handler)
    signal.signal(signal.SIGINT, _handler)


def _time_in_window(start: datetime | None, stop: datetime | None) -> bool:
    """Return True if current time is between start and stop."""
    if start is None or stop is None:
        return False
    now = datetime.now()
    return start <= now <= stop


def process_relays(engine, config: AppConfig) -> None:
    """
    Check each relay's timer_override state and update GPIO + DB accordingly.
    Called every second from the main loop.
    """
    from services.database import (
        get_relay_timer_pairs,
        read_timer_overrides,
        update_relay_state,
    )

    overrides = read_timer_overrides(engine)
    if overrides is None:
        logger.warning("Could not read timer_override table")
        return

    for idx, relay_col in enumerate([f"relay_{n}" for n in config.relay_count]):
        pin = config.output_pins[idx]
        override = overrides.get(relay_col, "off")

        if override == "on":
            relay_on = True
        elif override == "off":
            relay_on = False
        else:  # "auto" — check timer schedule
            relay_on = False
            table = f"{relay_col}_timer"
            for pair_pk in range(1, config.num_dt_pairs[idx] + 1):
                pair = get_relay_timer_pairs(engine, table, pair_pk)
                if pair and _time_in_window(pair[1], pair[2]):
                    relay_on = True
                    break

        set_relay(pin, relay_on)
        update_relay_state(engine, relay_col, relay_on)
