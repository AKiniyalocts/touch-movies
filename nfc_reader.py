import logging

import board
import busio
from adafruit_pn532.i2c import PN532_I2C

log = logging.getLogger(__name__)

READ_TIMEOUT = 1.0


class NfcReader:
    def __init__(self):
        self._pn532 = None

    def initialize(self):
        i2c = busio.I2C(board.SCL, board.SDA)
        self._pn532 = PN532_I2C(i2c, debug=False)

        version = self._pn532.firmware_version
        log.info(
            "Found PN532 — firmware %d.%d.%d",
            version[0],
            version[1],
            version[2],
        )

        self._pn532.SAM_configuration()

    def read_uid(self):
        uid = self._pn532.read_passive_target(timeout=READ_TIMEOUT)
        if uid is not None:
            return bytes(uid)
        return None

    def read_ndef_text(self):
        """Read the first NDEF text or URI record from an NTAG tag.
        Call after read_uid() has detected a tag."""
        data = self._read_user_data()
        if data is None:
            return None
        return self._parse_ndef_text(data)

    def _read_user_data(self, start_page=4, max_pages=40):
        """Read user data pages from an NTAG/Ultralight tag."""
        buf = bytearray()
        for page in range(start_page, start_page + max_pages):
            block = self._pn532.ntag2xx_read_block(page)
            if block is None:
                break
            buf.extend(block)
            # Stop if we hit the NDEF terminator TLV
            if 0xFE in block:
                break
        return bytes(buf) if buf else None

    @staticmethod
    def _parse_ndef_text(data):
        """Extract the first text/URI payload from raw NDEF TLV data."""
        i = 0
        while i < len(data):
            tlv_type = data[i]
            if tlv_type == 0x00:  # NULL TLV
                i += 1
                continue
            if tlv_type == 0xFE:  # Terminator
                break
            if i + 1 >= len(data):
                break
            length = data[i + 1]
            i += 2
            if tlv_type == 0x03:  # NDEF Message TLV
                return NfcReader._parse_ndef_record(data[i:i + length])
            i += length
        return None

    @staticmethod
    def _parse_ndef_record(msg):
        """Parse the first record from an NDEF message."""
        if len(msg) < 3:
            return None
        flags = msg[0]
        tnf = flags & 0x07
        sr = flags & 0x10  # Short Record flag
        type_len = msg[1]
        if sr:
            payload_len = msg[2]
            offset = 3
        else:
            if len(msg) < 6:
                return None
            payload_len = int.from_bytes(msg[2:6], "big")
            offset = 6
        rec_type = msg[offset:offset + type_len]
        payload = msg[offset + type_len:offset + type_len + payload_len]

        # Text record (TNF=0x01, type="T")
        if tnf == 0x01 and rec_type == b"T":
            lang_len = payload[0] & 0x3F
            return payload[1 + lang_len:].decode("utf-8")

        # URI record (TNF=0x01, type="U")
        if tnf == 0x01 and rec_type == b"U":
            uri_prefixes = [
                "", "http://www.", "https://www.", "http://", "https://",
            ]
            prefix_idx = payload[0]
            prefix = uri_prefixes[prefix_idx] if prefix_idx < len(uri_prefixes) else ""
            return prefix + payload[1:].decode("utf-8")

        # Fallback: return raw payload as string
        try:
            return payload.decode("utf-8")
        except UnicodeDecodeError:
            return payload.hex()

    @staticmethod
    def format_uid(uid):
        return ":".join(f"{b:02X}" for b in uid)
