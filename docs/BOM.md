# Bill of Materials (BOM)

Generated from [`../bom.csv`](../bom.csv) by `tools/bom_md.py`. Prices are approximate USD, so verify before ordering.
Status labels: **FINISHED / PROTOTYPE-READY / EXPERIMENTAL**.

## CORE ≈ $166.83

| Item | Part | Qty | ≈ $ each | Status | Notes | Change vs brief |
|---|---|---:|---:|---|---|---|
| [Seeed Studio XIAO ESP32-S3 (NON-Sense)](https://wiki.seeedstudio.com/xiao_esp32s3_getting_started/) | XIAO ESP32-S3 | 1 | 7.49 | PROTOTYPE-READY | BLE/Wi-Fi safety authority. Non-Sense = no camera. Powered from 5V_SW through 1N5817 into the 5V pin (Seeed's recommended diode). | kept |
| [SparkFun Qwiic Mini ToF Imager](https://www.sparkfun.com/sparkfun-qwiic-mini-tof-imager-vl53l5cx.html) | VL53L5CX / SEN-19013 | 1 | 25.95 | PROTOTYPE-READY | 8x8 zones, 25.4 x 12.7 mm. In the bridge pocket, sensor flush with the front face. Open window, no cover glass. | kept |
| [Adafruit LSM6DSOX 6-DoF IMU (STEMMA QT/Qwiic)](https://www.adafruit.com/product/4438) | Adafruit 4438 | 1 | 11.95 | PROTOTYPE-READY | 25.4 x 17.78 mm. Plug-in Qwiic cables, no soldering. No major vendor sells a Qwiic ICM-42688-P board. | REPLACES ICM-42688-P breakout |
| [BME280 module, 3.3 V I2C (temp + humidity + pressure)](https://www.bosch-sensortec.com/en/products/environmental-sensors/humidity-sensors-bme280/) | GY-BME280-3.3 class | 1 | 6.00 | PROTOTYPE-READY | One board replaces BMP390 + SHT40. Sits in the vented left-brow pocket, about 20 mm from the ToF. Check the chip ID is 0x60 (BME280), not 0x58 (BMP280 clone). Measure the board: the pocket is 15.5 x 12 mm. | REPLACES BMP390 + SHT40 |
| [I2S MEMS microphone breakout](https://www.adafruit.com/product/3421) | Adafruit 3421 SPH0645LM4H | 1 | 6.95 | PROTOTYPE-READY | VDD = MIC_3V3 only. Power comes through the PTT switch and nothing else. | kept |
| [I2S class-D amplifier](https://www.adafruit.com/product/3006) | Adafruit 3006 MAX98357A | 2 | 5.95 | PROTOTYPE-READY | One amp for bone, one for outward. Each SD pin goes to its own GPIO, giving BONE / OUTWARD / BOTH / MUTE. Firmware caps the volume. | kept |
| [Bone-conductor transducer 8 ohm 1 W](https://www.adafruit.com/product/1674) | Adafruit 1674 | 1 | 8.00 | PROTOTYPE-READY | Sits in the right TPU ear-grip cradle over the mastoid, face 0.8 mm proud. The 2nd unit is optional (set bone_left=true). | 2 -> 1 (2nd optional; amp output is mono anyway) |
| [15 mm round 8 ohm 0.5-1 W micro speaker](https://www.adafruit.com/category/271) | 15 mm 8R | 1 | 3.00 | PROTOTYPE-READY | Right pod, rear inner layer, fires through the inner-wall grille. Measure it: the pocket is 15.2 x 4.5 mm. | 2 -> 1 (2nd optional) |
| [USB-C charger + power path + 5 V 1 A boost on one board](https://www.adafruit.com/product/6106) | Adafruit 6106 (bq25185 + TPS61023) | 1 | 10.00 | PROTOTYPE-READY | 29.21 x 19.05 mm, left pod. Cut the ISET jumper for 500 mA charge. Replace R16 (THERM) with the 10k NTC. Keep boost start-up load under 200 mA (see the Adafruit notes). Price unconfirmed. | REPLACES BQ24074 board + TPS61023 board |
| [Protected 1S LiPo 8 x 20 x 46 mm, ~800 mAh, JST-PH](https://www.adafruit.com/category/574) | PKCELL LP802046 class | 1 | 9.00 | PROTOTYPE-READY | A temple-shaped cell. The 34 mm-wide 1200 mAh pack does not fit any temple. For the 802060 (1100 mAh) option, make the pod 16 mm longer. | 1200 mAh 34 mm-wide -> 800 mAh 20 mm-wide (fits temple) |
| [10k NTC thermistor, B~3435 (103AT)](https://www.adafruit.com/category/66) | 10k NTC | 1 | 1.00 | PROTOTYPE-READY | Kapton-taped to the cell and wired to the charger THERM/TS pads. The charger then stops on over- or under-temperature in hardware. | kept (now wired to bq25185 TS) |
| [6 x 6 mm tactile switch (SPST momentary)](https://www.digikey.com/en/products/filter/pushbutton-switches/199) | Omron B3F-1000 class | 1 | 0.25 | PROTOTYPE-READY | Right frame corner, under the printed flexure button. Switches 3V3 to MIC_3V3. This is the only path that powers the mic and LED. | REPLACES DPST momentary (see diode below) |
| 1N4148 diode + 100k pulldown (PTT sense) | 1N4148 | 1 | 0.10 | PROTOTYPE-READY | MIC_3V3 goes through the diode to D1. The diode blocks the GPIO from ever powering MIC_3V3, so it keeps the invariant that pole B gave. | NEW (replaces DPST pole B) |
| [Slide switch, SPDT, 5 A (main power)](https://www.digikey.com/en/products/detail/e-switch/500SSP1S1M6QEA/378947) | E-Switch 500SSP1S1M6QEA | 1 | 3.19 | PROTOTYPE-READY | Left frame endpiece, actuator out the side. Breaks the 5 V system rail. The charger keeps charging while it is off. | kept (rated part chosen) |
| 3 mm red LED + 1k resistor | MIC ON | 1 | 0.25 | PROTOTYPE-READY | Front of the right endpiece, wired directly to MIC_3V3. | kept |
| 1N5817 Schottky (5V_SW -> XIAO 5V pin) | 1N5817 | 1 | 0.30 | PROTOTYPE-READY | Stops backfeed when the XIAO USB-C is plugged in. | NEW |
| 2 x 100k resistors (VBAT sense divider -> D0) | 100k | 2 | 0.03 | PROTOTYPE-READY | Battery level for battery_manager. | NEW |
| [Brass tube 4 mm OD x 0.45 wall (ID ~3.1), 300 mm](https://ksmetals.com/products/br45mm-4) | K&S 9822 | 1 | 9.99 | EXPERIMENTAL | Two 13.5 mm hollow hinge pins. The wires run through the axis and only twist when folding. Run the fold-cycle test first. | NEW (hollow-pin hinge) |
| [M2 heat-set inserts (OD 3.6, L 4)](https://www.3djake.com/ruthex/threaded-insert-m2-70-pieces) | ruthex M2 x 4 | 1 | 8.50 | PROTOTYPE-READY | 2 for the lids, 2 for the HUD mount. Hole 3.1 x 5.5 mm (tune on the coupon). | kept |
| M2 screw assortment (x4, x5, x6 pan/button head) | M2 | 1 | 8.00 | PROTOTYPE-READY | Lids M2x5 (2). HUD mount M2x6 (2). Pivots M2x4 (2). Focus clamp M2x6 (1). | kept |
| Silicone wire 28 AWG (power) + 30 AWG (signal), 2 Qwiic cables + 1 Qwiic pigtail | Harness | 1 | 10.00 | PROTOTYPE-READY | Right hinge: 7 wires. Left hinge: 3. About 36% fill in a 3.1 mm ID tube. | kept |
| [Stick-on silicone nose pads (12 pairs)](https://eyeglasssupplystore.com/products/adhesive-silicone-nose-pads) | adhesive D-pads | 1 | 15.95 | PROTOTYPE-READY | Stick onto the printed pad lands. | NEW (replaces printed pads) |
| 1 mm foam tape + Kapton tape |  | 1 | 6.00 | PROTOTYPE-READY | Board retention in the pods, harness covering, battery padding. | kept |
| PETG (~65 g core) + TPU 95A (~5 g) | Bambu PETG HF / TPU 95A HF | 1 | 3.00 | PROTOTYPE-READY | Print the HUD tower in black PETG. | kept |

## HUD ≈ $398.95

| Item | Part | Qty | ≈ $ each | Status | Notes | Change vs brief |
|---|---|---:|---:|---|---|---|
| [30R/70T plate beamsplitter, 25 mm dia x 1 mm, N-BK7](https://www.edmundoptics.com/p/25mm-dia-30-70rt-vis-plate-beamsplitter/37187/) | Edmund Optics #35-933 | 1 | 149.00 | EXPERIMENTAL | Optical grade, never printed. A budget 30/70 teleprompter glass cut to 25 mm also fits the arm, but check the ratio. | priced from a real part (brief: ~$25) |
| [25 mm dia, f = 25 mm plastic asphere](https://www.edmundoptics.com/p/25mm-diameter-x-25mm-fl-uncoated-plastic-aspheric-lens/20531/) | Edmund Optics #66-008 | 1 | 34.95 | EXPERIMENTAL | Press-fit in the tower lens seat. Focus with the sliding display carrier (about +/-6 mm). | priced from a real part |
| [0.23 in 640x400 micro-OLED + HDMI controller kit](https://www.tindie.com/products/oled-modules/microdisplay-023-inch-micro-oled-display-640x400/) | Display Components 0.23in kit | 1 | 215.00 | EXPERIMENTAL | The panel takes parallel RGB, normally through the HDMI board, so it needs an HDMI source (the MEDIA Pi). An ESP32-S3 cannot drive it directly. Measure the module and set disp_mod. | priced from a real part (brief: ~$99) |

## MEDIA ≈ $46.99

| Item | Part | Qty | ≈ $ each | Status | Notes | Change vs brief |
|---|---|---:|---:|---|---|---|
| [Raspberry Pi Zero 2 W](https://www.raspberrypi.com/products/raspberry-pi-zero-2-w/) | SC0510 | 1 | 14.99 | EXPERIMENTAL | Optional. Also drives the HDMI micro-OLED. The ESP32 stays the safety authority via MEDIA_EN (D6). | kept (not modeled in CAD yet) |
| Protected 1S 2000-3000 mAh + 5 V >= 2 A regulator | rear media pack | 1 | 25.00 | EXPERIMENTAL | Separate supply. Never route media current through ESP32-class wiring. | kept (not modeled) |
| microSD 32 GB A1/A2 |  | 1 | 7.00 | EXPERIMENTAL |  | kept |

## OPTION

| Item | Part | Qty | ≈ $ each | Status | Notes | Change vs brief |
|---|---|---:|---:|---|---|---|
| [Protected 1S LiPo 8 x 20 x 62 mm 1100 mAh](https://www.dnkpower.com/products/3-7v-802060-1100mah-lithium-polymer-battery/) | DNK Power 802060 | 0 | 0.00 | PROTOTYPE-READY | Use with pod_len +16 and only if the ear clearance allows it. Manufacturer listing, request a quote. | option |

Totals: CORE ≈ $167 · CORE + HUD ≈ $566 · + MEDIA ≈ $613.
The HUD is priced from real optical parts. A budget 30/70 glass combiner instead of the Edmund plate saves about $130.
