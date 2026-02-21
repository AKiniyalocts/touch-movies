import logging
import time

from config import load_config
from ha_client import fire_tag_scanned
from nfc_reader import NfcReader
from sound import ensure_sound_file, play_scan_sound

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

DEBOUNCE_DELAY = 1.0
POLL_INTERVAL = 0.1
ERROR_RECOVERY_DELAY = 3.0

HA_TAG_PREFIX = "https://www.home-assistant.io/tag/"


def parse_tag_id(url):
    """Extract the tag ID from an HA NFC tag URL, or return None."""
    if url and url.startswith(HA_TAG_PREFIX):
        return url[len(HA_TAG_PREFIX):]
    return None


def main():
    ha_url, ha_token = load_config()
    ha_enabled = ha_url is not None
    ensure_sound_file()

    reader = NfcReader()
    reader.initialize()
    log.info("Waiting for NFC tags...")

    last_uid = None

    while True:
        try:
            uid = reader.read_uid()

            if uid is not None:
                if uid != last_uid:
                    play_scan_sound()
                    formatted = NfcReader.format_uid(uid)
                    text = reader.read_ndef_text()
                    if text:
                        log.info("Tag detected — NDEF: %s", text)
                        tag_id = parse_tag_id(text)
                        if tag_id and ha_enabled:
                            fire_tag_scanned(ha_url, ha_token, tag_id)
                        elif tag_id and not ha_enabled:
                            log.warning("Tag %s scanned but HA integration is disabled", tag_id)
                    else:
                        log.info("Tag detected — UID: %s (%d bytes)", formatted, len(uid))
                last_uid = uid
                time.sleep(DEBOUNCE_DELAY)
            else:
                last_uid = None
                time.sleep(POLL_INTERVAL)

        except OSError as e:
            log.error("Communication error: %s — retrying in %ds", e, int(ERROR_RECOVERY_DELAY))
            time.sleep(ERROR_RECOVERY_DELAY)
            try:
                reader.initialize()
                log.info("Reconnected to PN532")
            except Exception:
                log.error("Re-initialization failed, will retry")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped by user")
        raise SystemExit(0)
