# Bill of Materials (BOM)

Generated from [`../bom.csv`](../bom.csv) by `tools/bom_md.py`. Prices are approximate USD, so verify before ordering.
Status labels: **FINISHED / PROTOTYPE-READY / EXPERIMENTAL**.

## GLASSES ≈ $853.74

| Item | Part | Qty | ≈ $ each | Status | Notes | Change vs brief |
|---|---|---:|---:|---|---|---|
| [0.71in 1920x1080 micro-OLED 3D dual kit: 2 panels + 1 HDMI board for both + 2 OPE07-10X prism eyepieces](https://www.tindie.com/products/microdisplays/micro-oled-dual-display-071-fhd-1080p-1920x1080/) | Sony ECX335S dual kit | 1 | 659.50 | EXPERIMENTAL | One HDMI input drives both eyes, side by side. Panel is 24.24 x 15.62 x 1.54 mm. Measure the optics and board, then set eyepiece_d, eyepiece_len and hdmi_board in config.scad. | NEW: passthrough view |
| [1.69in 240x280 IPS LCD, ST7789V2, SPI](https://www.waveshare.com/1.69inch-lcd-module.htm) | Waveshare 1.69inch LCD Module | 2 | 9.49 | PROTOTYPE-READY | Shows the designs on the front of each lens. 39 x 31.5 mm outline, about 90 mA each. | NEW: designs screens |
| [12MP IMX708 USB UVC camera, 102 deg (120 deg diagonal), fixed focus](https://www.arducam.com/12mp-imx708-usb-uvc-102-wide-angle-fixed-focus-camera-module-3.html) | Arducam IMX708 UVC 102 | 1 | 71.98 | PROTOTYPE-READY | 24 x 25 mm board in the centre bridge. 1080p30 MJPEG for passthrough, 12 MP stills. For 60 fps you need a 38 mm board. | NEW: centre camera |
| [Seeed XIAO ESP32-S3 (non-Sense)](https://wiki.seeedstudio.com/xiao_esp32s3_getting_started/) | XIAO ESP32-S3 | 1 | 7.49 | PROTOTYPE-READY | Drives the outward LCDs, IMU, hall sensor, button, battery sense and LiPo charging. BLE to the phone, Wi-Fi to the brick. | kept |
| [LSM6DSOX 6-DoF IMU, STEMMA QT](https://www.adafruit.com/product/4438) | Adafruit 4438 | 1 | 11.95 | PROTOTYPE-READY | Mounted in the visor bridge, rigid with the displays. | kept |
| [Hall switch, omnipolar, 1.65-5.5 V](https://www.lcsc.com/product-detail/hall-switches_ti-drv5032fadbzr_C140921.html) | TI DRV5032FA (SOT-23) on a SOT-23 adapter | 1 | 1.20 | PROTOTYPE-READY | Detects visor up or down using a magnet in the brow. Visor up turns the inner displays off and blanks the designs. | NEW |
| Neodymium disc magnet 6 x 3 mm N52 | 6x3 N52 | 1 | 0.30 | PROTOTYPE-READY | Press-fit into the brow centre. | NEW |
| [Protected 1S LiPo 5 x 10 x 40 mm, ~200 mAh (or LP401235 4x12x36)](https://www.ebay.com/itm/254701205905) | 501040 PCM | 2 | 6.00 | PROTOTYPE-READY | One per earpiece, as a counterweight. Wired in parallel: charge both to 4.2 V before joining them. Standby only; passthrough runs on cable power. | 1 big cell -> 2 earpiece cells |
| [DPDT slide switch, 300 mA](https://www.mouser.com/c/?q=452403012014) | Wurth 452403012014 | 2 | 2.67 | PROTOTYPE-READY | Switch 1 is main battery power. Switch 2 is the camera power kill: it physically cuts the camera's 5 V supply. | NEW (camera privacy) |
| 3 mm red LED + 1k resistor on the camera 5 V (after the switch) | CAMERA LIVE | 1 | 0.25 | PROTOTYPE-READY | Hardware-tied, so software cannot hide it. It faces forward beside the camera. | NEW |
| [6 x 6 mm tactile switch](https://www.digikey.com/en/products/filter/pushbutton-switches/199) | Omron B3F-1000 | 1 | 0.25 | PROTOTYPE-READY | Action button under the crest flexure: cycle designs, long-press to capture. | kept |
| 2 x 100k (battery sense divider) | 100k | 2 | 0.03 | PROTOTYPE-READY |  | kept |
| [Brass tube 4 mm OD (ID 3.1), 300 mm](https://ksmetals.com/products/br45mm-4) | K&S 9822 | 1 | 9.99 | EXPERIMENTAL | Four 12-13.5 mm pins: 2 temple hinges, 2 visor hinges. Wires run through them. | kept |
| [M2 heat-set inserts + M2x6 screws](https://www.3djake.com/ruthex/threaded-insert-m2-70-pieces) | ruthex M2 x 4 | 1 | 8.50 | PROTOTYPE-READY | 4 inserts hold the back plate. | kept |
| Thin micro-HDMI to HDMI (1.5 m) + USB-A to bare-wire 4-core (1.5 m), braided sleeve |  | 1 | 18.00 | PROTOTYPE-READY | Video in to the HDMI board, plus USB carrying camera data and 5 V for the glasses. Enters the crest on the left side. | NEW |
| [Stick-on silicone nose pads](https://eyeglasssupplystore.com/products/adhesive-silicone-nose-pads) | adhesive D-pads | 1 | 15.95 | PROTOTYPE-READY |  | kept |
| Silicone wire 30 AWG, 1 mm foam tape, Kapton, filament (PETG ~80 g, TPU ~6 g) |  | 1 | 12.00 | PROTOTYPE-READY |  | kept |

## BRICK ≈ $220.00

| Item | Part | Qty | ≈ $ each | Status | Notes | Change vs brief |
|---|---|---:|---:|---|---|---|
| [Raspberry Pi 5 (8 GB) + active cooler](https://www.raspberrypi.com/products/raspberry-pi-5/) | Raspberry Pi 5 | 1 | 175.00 | EXPERIMENTAL | Runs camera passthrough plus the AR overlay, outputs side-by-side 3840x1080 over HDMI, and does local AI. A Pi 5 4 GB also works. | NEW (Vision Pro-style pocket brick) |
| USB-C power bank, 2 outputs, at least 5V/3A |  | 1 | 35.00 | PROTOTYPE-READY | Port 1 powers the Pi. Port 2 powers the glasses 5 V through the USB lead (keeps load off the Pi's 600 mA USB limit). | NEW |
| microSD 64 GB A2 |  | 1 | 10.00 | PROTOTYPE-READY | Raspberry Pi OS 64-bit + brick/ software. | kept |

## PHONE

| Item | Part | Qty | ≈ $ each | Status | Notes | Change vs brief |
|---|---|---:|---:|---|---|---|
| Any phone with Chrome (Android) for the Web Bluetooth controls |  | 0 | 0.00 | PROTOTYPE-READY | Designs, brightness, text and status via the web app's Glasses tab. Heavy AI can run on the phone or the brick. | NEW |

## OPTION

| Item | Part | Qty | ≈ $ each | Status | Notes | Change vs brief |
|---|---|---:|---:|---|---|---|
| [0.49in 1920x1080 micro-OLED + Dual HDMI or Dual Type-C board, x2](https://www.tindie.com/products/oled-modules/049-micro-oled-display-1920x1080-3000nits/) | SeeYA SY049-class | 0 | 135.00 | EXPERIMENTAL | Panel is 15.68 x 9.09 mm. The Dual Type-C board could take video straight from a DisplayPort-capable phone. Board price and size are unconfirmed. | option |

Totals: glasses ≈ $854 · pocket brick ≈ $220 · together ≈ $1074.
Most of the glasses cost is the micro-OLED dual kit ($660). The budget 0.49-inch option is listed under OPTION.
