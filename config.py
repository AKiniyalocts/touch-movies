import logging
import os

log = logging.getLogger(__name__)

_ENV_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")


def _load_env_file(path):
    """Parse a simple KEY=VALUE .env file into a dict."""
    values = {}
    try:
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    continue
                key, value = line.split("=", 1)
                values[key.strip()] = value.strip()
    except FileNotFoundError:
        pass
    return values


def load_config():
    """Return (ha_url, ha_token) from env vars, falling back to .env file."""
    env_file = _load_env_file(_ENV_FILE)

    ha_url = os.environ.get("HA_URL") or env_file.get("HA_URL")
    ha_token = os.environ.get("HA_TOKEN") or env_file.get("HA_TOKEN")

    if not ha_url or not ha_token:
        log.warning("HA_URL or HA_TOKEN not set — HA integration disabled")
        return None, None

    # Strip trailing slash for consistent URL building
    ha_url = ha_url.rstrip("/")
    return ha_url, ha_token
