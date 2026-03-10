#!/usr/bin/env python3
"""
Standalone email alert sender — modernised from MyHydroPi-Blog/Website_Code/Email/*.py.
Consolidates all email variants into one script with CLI arguments.

Usage:
    python scripts/email/send_alert.py --subject "Test" --body "Hello"
    python scripts/email/send_alert.py --subject "Test" --html-file templates/body.html --text-file templates/body.txt
    python scripts/email/send_alert.py --subject "Test" --body "Hello" --attach /path/to/file.csv

Required .env keys:
    EMAIL_FROM, EMAIL_PASSWORD, EMAIL_TO, EMAIL_SERVER, EMAIL_PORT
"""

import argparse
import os
import smtplib
import sys
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from dotenv import load_dotenv
from loguru import logger

load_dotenv(Path(__file__).parent.parent.parent / ".env")

EMAIL_FROM   = os.getenv("EMAIL_FROM", "")
EMAIL_PASS   = os.getenv("EMAIL_PASSWORD", "")
EMAIL_TO     = os.getenv("EMAIL_TO", "")
EMAIL_SERVER = os.getenv("EMAIL_SERVER", "smtp.gmail.com")
EMAIL_PORT   = int(os.getenv("EMAIL_PORT", "587"))

logger.remove()
logger.add(sys.stderr, level="INFO")


def build_message(
    subject: str,
    body_text: str,
    body_html: str | None = None,
    attachments: list[str] | None = None,
) -> MIMEMultipart:
    msg = MIMEMultipart("mixed")
    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO

    alt = MIMEMultipart("alternative")
    alt.attach(MIMEText(body_text, "plain"))
    if body_html:
        alt.attach(MIMEText(body_html, "html"))
    msg.attach(alt)

    for path_str in (attachments or []):
        path = Path(path_str)
        if not path.exists():
            logger.warning(f"Attachment not found: {path}")
            continue
        with path.open("rb") as fh:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(fh.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", "attachment", filename=path.name)
        msg.attach(part)

    return msg


def send(msg: MIMEMultipart) -> bool:
    try:
        with smtplib.SMTP(EMAIL_SERVER, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_FROM, EMAIL_PASS)
            server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
        logger.info(f"Email sent to {EMAIL_TO}: {msg['Subject']}")
        return True
    except smtplib.SMTPException as exc:
        logger.error(f"SMTP error: {exc}")
        return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Send an alert email from HydroPi")
    parser.add_argument("--subject", required=True)
    parser.add_argument("--body", help="Plain text body")
    parser.add_argument("--text-file", help="Path to plain text body file")
    parser.add_argument("--html-file", help="Path to HTML body file")
    parser.add_argument("--attach", nargs="*", help="File paths to attach", default=[])
    args = parser.parse_args()

    if not EMAIL_FROM or not EMAIL_TO:
        logger.error("EMAIL_FROM and EMAIL_TO must be set in .env")
        sys.exit(1)

    body_text = args.body or ""
    if args.text_file:
        body_text = Path(args.text_file).read_text()

    body_html = None
    if args.html_file:
        try:
            body_html = Path(args.html_file).read_text()
        except FileNotFoundError:
            logger.warning(f"HTML template not found: {args.html_file}")

    if not body_text:
        logger.error("Provide --body or --text-file")
        sys.exit(1)

    msg = build_message(args.subject, body_text, body_html, args.attach)
    success = send(msg)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
