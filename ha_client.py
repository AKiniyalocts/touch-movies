import logging

import requests

log = logging.getLogger(__name__)

TIMEOUT = 5


def fire_tag_scanned(base_url, token, tag_id):
    """Fire a tag_scanned event on Home Assistant. Returns True on success."""
    url = f"{base_url}/api/events/tag_scanned"
    headers = {"Authorization": f"Bearer {token}"}
    body = {"tag_id": tag_id}

    try:
        resp = requests.post(url, json=body, headers=headers, timeout=TIMEOUT)
        resp.raise_for_status()
        log.info("Triggered HA tag_scanned for tag %s", tag_id)
        return True
    except requests.RequestException as e:
        log.error("Failed to fire HA event: %s", e)
        return False
