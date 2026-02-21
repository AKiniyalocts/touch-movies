# touch-movies — NFC Tag Reader 
Read NFC tag URI using a PN532 module connected to a Raspberry Pi Zero W over I2C.

Send a webhook to a local home assistant server when a specific tag format is read.

Start a home automation on home assistant.

# Specific project goals

Create physical media cards tied to a specific video/show (storing an id for the media on an NFC sticker) hosted on a local media server.

Enable users (mainly my children) to scan the media cards on a physical device (a raspberry pi w/ NFC module) and play the media on the local smart TV.

## Hardware/Software Assumptions
- Home assistant
- Jellyfin server
- Jellyfin for Android TV
- Android/Google TV (something running Android)
- Raspberry pi zero w
- PN532 based NFC module

(there are certainly other options for all of these. This is just what I have available.)

## Hardware recommendations
Below is a list of the actual hardware I used in this project. While I am sure there are other options available, these particular components worked for me!
- [PN532 Module](https://www.amazon.com/gp/aw/d/B09Q89G78M)
- [Raspberry pi zero w](https://www.raspberrypi.com/products/raspberry-pi-zero-w/) (with pins)

> Note: the items below are optional

- [USB Mini OTG cable](https://www.amazon.com/dp/B00N9S9Z0G) (for speaker)
- [USB Speaker](https://www.amazon.com/dp/B075M7FHM1)
- [Enclosure](https://www.amazon.com/dp/B0FHVT1WCQ)

## Hardware Setup

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

1. **Install Raspberry Pi OS lite**

2. **Enable I2C:**
   ```
   sudo raspi-config
   ```
   Navigate to Interface Options → I2C → Enable, then reboot.

3. **Run the setup script:**
   ```
   chmod +x setup.sh
   ./setup.sh
   ```

4. **Verify wiring:**
   ```
   sudo i2cdetect -y 1
   ```
   You should see a device at address `0x24`.

5. **Environment**
A `.env` file is required if scanning home assistant tags. Create a `.env` in the project directory with the following:
   ```
   HA_URL=http://homeassistant.local:8123  // default HA hostname and port
   HA_TOKEN=GENERATE_THIS_TOKEN // generate from your home assistant server
   ```

## Usage

```
source .venv/bin/activate
python main.py
```

Tap an NFC tag to see its UID:
```
Tag detected — UID: DE:AD:BE:EF (4 bytes)
```
When a Home assistant tag is scanned:
```
//TODO
```

Press Ctrl+C to exit.

