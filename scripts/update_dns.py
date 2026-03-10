#!/usr/bin/env python3
"""
Dynamic DNS updater — modernised from MyHydroPi-Blog/Miscellaneous/update_dns.py.
Reads credentials from .env; designed to run via systemd timer every 10 minutes.

Required .env keys:
    DDNS_PROVIDER   - "duckdns" | "noip" (add others as needed)
    DDNS_DOMAIN     - your domain/subdomain
    DDNS_TOKEN      - provider API token / password
    DDNS_USERNAME   - provider username (NoIP only)
"""

import os
import sys
import urllib.request
import urllib.error
from pathlib import Path

from dotenv import load_dotenv
from loguru import logger

# Load .env from the project root (two levels up from this script)
load_dotenv(Path(__file__).parent.parent / ".env")

PROVIDER   = os.getenv("DDNS_PROVIDER", "duckdns").lower()
DOMAIN     = os.getenv("DDNS_DOMAIN", "")
TOKEN      = os.getenv("DDNS_TOKEN", "")
USERNAME   = os.getenv("DDNS_USERNAME", "")
LOG_FILE   = os.getenv("LOG_FILE", "/var/log/hydropi/daemon.log")
LOG_LEVEL  = os.getenv("LOG_LEVEL", "INFO")

logger.remove()
logger.add(sys.stderr, level=LOG_LEVEL)
try:
    Path(LOG_FILE).parent.mkdir(parents=True, exist_ok=True)
    logger.add(LOG_FILE, level=LOG_LEVEL, rotation="5 MB", retention="14 days")
except OSError:
    pass


def update_duckdns(domain: str, token: str) -> bool:
    url = f"https://www.duckdns.org/update?domains={domain}&token={token}&ip="
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            body = resp.read().decode()
        if body.startswith("OK"):
            logger.info(f"DuckDNS updated: {domain}")
            return True
        logger.warning(f"DuckDNS returned: {body}")
        return False
    except urllib.error.URLError as exc:
        logger.error(f"DuckDNS request failed: {exc}")
        return False


def update_noip(domain: str, username: str, token: str) -> bool:
    import base64
    credentials = base64.b64encode(f"{username}:{token}".encode()).decode()
    url = f"https://dynupdate.no-ip.com/nic/update?hostname={domain}"
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Basic {credentials}")
    req.add_header("User-Agent", "HydroPi/2.0 hydropi@example.com")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode()
        if body.startswith(("good", "nochg")):
            logger.info(f"No-IP updated: {domain} → {body}")
            return True
        logger.warning(f"No-IP returned: {body}")
        return False
    except urllib.error.URLError as exc:
        logger.error(f"No-IP request failed: {exc}")
        return False


def main() -> None:
    if not DOMAIN:
        logger.error("DDNS_DOMAIN not set in .env — aborting.")
        sys.exit(1)
    if not TOKEN:
        logger.error("DDNS_TOKEN not set in .env — aborting.")
        sys.exit(1)

    if PROVIDER == "duckdns":
        success = update_duckdns(DOMAIN, TOKEN)
    elif PROVIDER == "noip":
        success = update_noip(DOMAIN, USERNAME, TOKEN)
    else:
        logger.error(f"Unknown DDNS_PROVIDER '{PROVIDER}'. Supported: duckdns, noip")
        sys.exit(1)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
