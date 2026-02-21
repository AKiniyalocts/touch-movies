import logging
import math
import os
import struct
import subprocess
import wave

log = logging.getLogger(__name__)

SOUND_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scan.wav")


def _generate_chime(path, amplitude=1.0, sample_rate=44100):
    """Generate a warm, music-box style chime."""
    # Three-note ascending major triad in a lower, warmer register
    notes = [
        (392.00, 120),  # G4, 120ms
        (493.88, 120),  # B4, 120ms
        (587.33, 200),  # D5, 200ms — linger on the last note
    ]

    with wave.open(path, "w") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sample_rate)

        for freq, duration_ms in notes:
            n_samples = int(sample_rate * duration_ms / 1000)
            fade_in = int(sample_rate * 0.005)
            fade_out = int(sample_rate * 0.08)  # long fade-out for bell-like decay

            for i in range(n_samples):
                t = i / sample_rate
                # Exponential decay for a natural bell feel
                decay = math.exp(-3.0 * i / n_samples)
                # Soft fade in/out on top of the decay
                edge = 1.0
                if i < fade_in:
                    edge = i / fade_in
                elif i > n_samples - fade_out:
                    edge = (n_samples - i) / fade_out
                # Fundamental + soft octave above for warmth
                tone = math.sin(2 * math.pi * freq * t)
                overtone = 0.3 * math.sin(2 * math.pi * freq * 2 * t)
                sample = amplitude * decay * edge * (tone + overtone)
                clamped = max(-1.0, min(1.0, sample))
                f.writeframes(struct.pack("<h", int(clamped * 32767)))


def ensure_sound_file():
    """Generate the beep WAV if it doesn't already exist."""
    if not os.path.exists(SOUND_FILE):
        _generate_chime(SOUND_FILE)
        log.info("Generated scan sound: %s", SOUND_FILE)


def play_scan_sound():
    """Play the scan beep asynchronously (non-blocking)."""
    try:
        subprocess.Popen(
            ["aplay", "-q", SOUND_FILE],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except FileNotFoundError:
        log.warning("aplay not found — install alsa-utils for scan sounds")
    except Exception as e:
        log.error("Failed to play sound: %s", e)
