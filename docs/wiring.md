# Wiring overview

**Every pin is in [`pinout.md`](pinout.md)** (generated from [`../hardware/netlist.csv`](../hardware/netlist.csv)). This page explains *why* it is wired this way.

![Power and privacy](img/wiring_power.svg)

## Three rules the wiring enforces
1. **Mic privacy is physical.** 3V3 → PTT switch → MIC_3V3 is the only supply for the mic and the red LED. The 1N4148 lets the ESP32 *read* PTT but never drive the rail.
2. **One switch kills the system and nothing else.** SW1 sits between the 5 V boost and everything else. The charger and its NTC cut-off keep working with it off.
3. **Media is gated by the ESP32.** D6 = MEDIA_EN is driven LOW at boot. A future Pi only gets video when safety_policy allows it.

## Power path
USB-C → Adafruit 6106 (bq25185 charger with power path → TPS61023 5 V boost) → SW1 → 5V_SW → 1N5817 → XIAO 5V. The two amps take 5V_SW directly.
- Charge at 500 mA (cut ISET). The NTC replaces R16. The protected cell adds over/under-voltage and short protection.
- The boost stalls if the start-up load exceeds about 200 mA, so firmware keeps both amps in shutdown until it is running.

## Through the hinges
| Hinge | Conductors |
|---|---|
| Left (3) | 5V_RAW, GND, VBAT_SENSE |
| Right (7) | 5V_SW, GND, VBAT_SENSE, 3V3, SDA, SCL, MIC_3V3 |

The bundle is 2 × 28 AWG + 5 × 30 AWG silicone wire, about 36% of the 3.1 mm tube bore. See [`img/hinge.svg`](img/hinge.svg).

![Signals](img/wiring_signals.svg)

## Audio
One I²S bus in full duplex: BCLK/WS are shared, D10 goes to both amps, the mic returns on D7. Each amp's SD pin selects BONE / OUTWARD / BOTH / MUTE. The output is mono, so one transducer and one speaker are enough. A second transducer can go in parallel (4 Ω is fine).
