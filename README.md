# movie-cards — NFC Tag Reader

Read NFC tag UIDs using a PN532 module connected to a Raspberry Pi Zero W over I2C.

## Hardware

### PN532 DIP Switch Settings (I2C mode)

| Switch | Position |
|--------|----------|
| 1      | ON       |
| 2      | OFF      |

### Wiring

| PN532 Pin | RPi Zero W Pin | Function |
|-----------|----------------|----------|
| GND       | Pin 6          | Ground   |
| VCC       | Pin 4 (5V)     | Power    |
| SDA       | Pin 3 (GPIO 2) | I2C data |
| SCL       | Pin 5 (GPIO 3) | I2C clock |

Use the 5V pin for power — the PN532 V3 board has an onboard 3.3V regulator, and the Pi's 3.3V rail can't reliably supply the ~150mA the PN532 draws.

## Setup

1. **Enable I2C:**
   ```
   sudo raspi-config
   ```
   Navigate to Interface Options → I2C → Enable, then reboot.

2. **Run the setup script:**
   ```
   chmod +x setup.sh
   ./setup.sh
   ```

3. **Verify wiring:**
   ```
   sudo i2cdetect -y 1
   ```
   You should see a device at address `0x24`.

## Usage

```
source .venv/bin/activate
python main.py
```

Tap an NFC tag to see its UID:
```
Tag detected — UID: DE:AD:BE:EF (4 bytes)
```

Press Ctrl+C to exit.

## Troubleshooting

### Device not detected at 0x24
- Verify DIP switches are set to I2C mode (1=ON, 2=OFF).
- Check all four wires are connected to the correct pins.
- Make sure I2C is enabled and you've rebooted.

### Flaky communication / frequent I2C errors
The BCM2835 has a known I2C clock stretching bug. Reduce the bus speed:
```
# Add to /boot/config.txt (or /boot/firmware/config.txt):
dtparam=i2c_arm_baudrate=50000
```
Then reboot.

### Power issues
If the PN532 resets or behaves erratically, try powering it from an external 5V supply. Connect GND of the external supply to a Pi GND pin.
