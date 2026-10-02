# Factory test firmware (ESP-IDF 5.5): EXPERIMENTAL test tool

Checks a hand-built unit against [`../../docs/pinout.md`](../../docs/pinout.md) in about a minute.

| Check | Automatic? |
|---|---|
| MEDIA_EN (D6) held LOW | ✅ |
| ToF VL53L5CX id `F0/02` · IMU LSM6DSOX `0x6C` · BME280 `0x60` | ✅ |
| Battery sense 3.0–4.3 V | ✅ |
| PTT released → mic silent · PTT held → sense high + live mic · released → silent again (**privacy gate**) | ✅ (you press the button) |
| 1 kHz tone on the bone transducer, then on the speaker | 👂 you listen |

This compiles cleanly with ESP-IDF v5.5.1 for the esp32s3. It has **not been run on the finished hardware yet**.

**Option A: no toolchain needed** (prebuilt image):
```bash
pip install esptool
esptool.py --chip esp32s3 write_flash 0x0 prebuilt/asg_factory_test_merged.bin
python3 -m serial.tools.miniterm /dev/ttyACM0 115200     # watch the prompts
```
On WSL2, pass the XIAO's USB through with `usbipd`, or flash from Windows with the same `esptool` command (`COMx`).

**Option B: build from source:**
```bash
. ~/esp/esp-idf/export.sh
idf.py set-target esp32s3 build flash monitor
```
