# Visor firmware: XIAO ESP32-S3 (ESP-IDF 5.5)

| Feature | File |
|---|---|
| Two outward design screens (eyes, rings, rainbow, scrolling text, off), rendered in 40-line bands over SPI | `main/designs.c` |
| Phone control over BLE: GATT service `7a1e0000-5c3b-4c55-9b1d-a5e0a5e0a5e0` | `main/ble.c` |
| Head pose and state to the brick: Wi-Fi to the `ASG-BRICK` hotspot, UDP 44-byte packets at 100 Hz | `main/net.c` |
| IMU (LSM6DSOX), visor hall switch, action button, battery sense, boot self-test | `main/main.c` |

**Status:** compiles cleanly against ESP-IDF v5.5.1 for the esp32s3. Not yet run on finished hardware. The screen mirroring (`esp_lcd_panel_mirror`) and IMU axis signs need checking on the bench.

**Flash the prebuilt image** (no toolchain needed):
```bash
pip install esptool
esptool.py --chip esp32s3 write_flash 0x0 prebuilt/asg_glasses_mcu_merged.bin
```

**Build from source:**
```bash
. ~/esp/esp-idf-v5.5.5/export.sh          # or your ESP-IDF 5.5 path
idf.py set-target esp32s3
idf.py menuconfig    # optional: "Adaptive Smart Glasses" menu (hotspot SSID/password, brick IP/port)
idf.py build flash monitor
```

**Button:** a short press cycles designs. Hold it for at least 1 s to turn the designs off.
