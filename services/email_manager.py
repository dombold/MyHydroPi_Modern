"""
Email alert manager — sends SMTP alerts when sensor values breach thresholds.
Replaces email_manager.py with type hints and loguru.
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from loguru import logger

from services.config import AppConfig


def _build_message(
    subject: str,
    body_text: str,
    body_html: str | None,
    from_addr: str,
    to_addr: str,
) -> MIMEMultipart:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to_addr
    msg.attach(MIMEText(body_text, "plain"))
    if body_html:
        msg.attach(MIMEText(body_html, "html"))
    return msg


def send_alert(
    config: AppConfig,
    subject: str,
    body_text: str,
    body_html: str | None = None,
) -> bool:
    """
    Send an alert email via SMTP.
    Returns True on success, False on failure.
    """
    if not config.email_from or not config.email_to:
        logger.warning("Email not configured — skipping alert.")
        return False

    msg = _build_message(subject, body_text, body_html, config.email_from, config.email_to)

    try:
        with smtplib.SMTP(config.email_server, config.email_port) as server:
            server.starttls()
            server.login(config.email_from, config.email_password)
            server.sendmail(config.email_from, config.email_to, msg.as_string())
        logger.info(f"Alert email sent to {config.email_to}: {subject}")
        return True
    except smtplib.SMTPException as exc:
        logger.error(f"Failed to send alert email: {exc}")
        return False


def send_alert_from_templates(
    config: AppConfig,
    subject: str,
    text_file: Path | str,
    html_file: Path | str | None = None,
) -> bool:
    """Send an alert email using pre-built template files."""
    try:
        body_text = Path(text_file).read_text()
    except (FileNotFoundError, OSError) as exc:
        logger.error(f"Cannot read text template {text_file}: {exc}")
        return False

    body_html = None
    if html_file:
        try:
            body_html = Path(html_file).read_text()
        except (FileNotFoundError, OSError) as exc:
            logger.warning(f"Cannot read HTML template {html_file}: {exc}")

    return send_alert(config, subject, body_text, body_html)


def check_and_alert(
    config: AppConfig,
    readings: list[tuple[str, float]],
    settings: dict,
    app_state,
) -> None:
    """
    Compare readings against alert thresholds.
    Sends one email per alert incident; resets after email_reset_delay.
    """
    from datetime import datetime

    # Check if main pump is off — suppress alerts when pump is off
    main_pump_relay = f"relay_1"  # Relay 1 = main pump by convention
    # (In real system: check timer_override for relay_1 state)

    any_alert = False
    alert_lines = []

    for name, value in readings:
        sensor_cfg = next(
            (s for s in config.sensors.values() if s.name == name and s.test_for_alert),
            None,
        )
        if sensor_cfg is None:
            continue

        hi = settings.get(sensor_cfg.upper_alert_name)
        lo = settings.get(sensor_cfg.lower_alert_name)
        offset = settings.get("offset_percent", 0.02)

        if hi is not None and value > hi * (1 - offset):
            any_alert = True
            alert_lines.append(f"{name}: {value} (HIGH > {hi})")
        elif lo is not None and value < lo * (1 + offset):
            any_alert = True
            alert_lines.append(f"{name}: {value} (LOW < {lo})")

    app_state.set_alert_check(any_alert)

    if not any_alert:
        if app_state.email_sent:
            logger.info("Sensor readings returned to normal — resetting alert state.")
            app_state.set_email_sent(False)
        return

    now = datetime.now()
    if app_state.email_sent and app_state.email_sent_time is not None:
        elapsed = (now - app_state.email_sent_time).total_seconds()
        if elapsed < config.email_reset_delay:
            return  # Still within cooldown period

    subject = "HydroPi Alert: Sensor readings out of range"
    body = "The following sensor readings are outside acceptable limits:\n\n"
    body += "\n".join(alert_lines)
    body += f"\n\nTimestamp: {now.strftime('%Y-%m-%d %H:%M:%S')}"

    if send_alert(config, subject, body):
        app_state.set_email_sent(True, sent_time=now)
