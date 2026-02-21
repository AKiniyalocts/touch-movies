#!/usr/bin/env bash
set -euo pipefail

echo "=== movie-cards NFC reader setup ==="

# Check I2C
if ! grep -q '^dtparam=i2c_arm=on' /boot/config.txt 2>/dev/null &&
   ! grep -q '^dtparam=i2c_arm=on' /boot/firmware/config.txt 2>/dev/null; then
    echo "WARNING: I2C may not be enabled."
    echo "  Run: sudo raspi-config → Interface Options → I2C → Enable"
    echo "  Then reboot before continuing."
    echo ""
fi

# System packages
echo "Installing system packages..."
sudo apt-get update -qq
sudo apt-get install -y -qq i2c-tools python3-venv python3-dev

# I2C group
if ! groups "$USER" | grep -q '\bi2c\b'; then
    echo "Adding $USER to i2c group (log out and back in to take effect)..."
    sudo usermod -aG i2c "$USER"
fi

# Virtual environment
echo "Creating virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

echo "Installing Python dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt

echo ""
echo "=== Setup complete ==="
echo "Verify wiring: sudo i2cdetect -y 1  (expect device at 0x24)"
echo "Run:           source .venv/bin/activate && python main.py"
