> **Note:** this is the original v0.1 master brief (camera-free). v0.2 deliberately changes direction: camera passthrough, outward design screens, flip-up visor. See [design_changes.md](design_changes.md) and [requirements.md](requirements.md).

# ADAPTIVE SMART GLASSES — MASTER BUILD BRIEF (paste into a new chat; attach CAD + BOM files)

You are continuing a real, buildable wearable prototype — not a rendering. Read all of this
before changing anything, and review every supplied file first. Act as the combined senior
product, embedded, optical-mechanical, firmware, mobile, industrial-design, electrical,
battery/power, and safety engineer. GOAL: a system that can actually be printed, wired,
programmed, tested, iterated, and worn, that looks far closer to normal eyewear than a headset.

## 0. Non-negotiable invariants (never weaken without an explicit, deliberate design change)
PRIVACY
- CAMERA-FREE. Depth/proximity only, via multi-zone Time-of-Flight (ToF). No image capture.
- NO wake word. NO always-on microphone. NO rolling audio buffer. NO face recognition.
- Microphone receives electrical power ONLY while the physical push-to-talk (PTT) switch is
  held. Firmware has NO other route capable of powering the mic.
- Privacy LED is wired to the switched mic power rail; software cannot drive it independently.
  Mic powered = red LED lit, always.
SAFETY
- The ESP32-S3 is the safety authority even if a media processor is added.
- DRIVE_SAFE disables distracting media at the HARDWARE/control layer (MEDIA_EN = LOW), not by
  hiding video in the app. The phone app can NEVER bypass DRIVE_SAFE.
- Entertainment never overrides driving, battery, thermal, visual, or privacy safety.
- Invalid ToF data must NOT be read as "clear path." GNSS loss while already moving must NOT
  immediately restore media. Fail conservative.
HONESTY
- Never claim a feature works unless the actual hardware/software supports it. The ToF gives
  "object ~0.6 m ahead," NOT "that is a bicycle / a red light" — no semantic vision claimed.

## 1. Architecture at a glance
Phone (heavy AI/ASR/translation/TTS) ⇄ BLE (control/status) + Wi-Fi (audio/media/firmware) ⇄
ESP32-S3 (safety authority, sensors, PTT, audio routing, HUD control) → optional media
processor (Pi-class) for video, gated by MEDIA_EN. Core functions run offline/disconnected.

## 2. Core controller
Seeed Studio XIAO ESP32-S3, NON-Sense version (avoids an unwanted camera). Owns BLE, Wi-Fi,
IMU/ToF/pressure/temperature acquisition, PTT sensing, mic interface, audio routing, HUD
control, battery/power management, driving-safety logic, flight-mode logic, obstacle warnings,
phone link, and final safety-state authority.

## 3. Sensors & environment
- Depth: VL53L5CX 8×8 multi-zone ToF (64 zones), bridge/front-center. Obstacles ahead,
  left/right clearance, closing distance, rapidly-approaching detection. No photographs.
- IMU: ICM-42688-P 6-axis. Head motion, movement classification, driving-detection assist.
  IMU alone never concludes "driving."
- Pressure: BMP390 as CONTEXT only. < ~820 hPa for ~120 s → prompt "Enable Flight Mode?"
  (user confirms). Normal ~820–1080 hPa. Weird readings → diagnostics, not assumptions.
- Ambient temp/humidity: SHT40, in a ventilated outer pod away from skin, battery, regulators,
  and processor heat; calibrate before display.

## 4. Driving detection & DRIVE_SAFE
Fuse PHONE GNSS SPEED + GLASSES IMU. Candidate: speed ≥ ~8.0 m/s (~18 mph) for ~10 s with
motion evidence → DRIVE_SAFE. DRIVE_SAFE disables video, movies, feeds, games, large images,
long visual AI answers, heavy animation (MEDIA_EN LOW). Allows clock, short safety messages,
essential status, basic nav cues, battery warnings, audio interaction, obstacle warnings.
Exit only after speed < ~2.5 m/s (~5.6 mph) for ~30 s. GNSS loss while moving does NOT restore
media. Vehicle testing is done by a passenger/test operator — never debug while driving.

## 5. Flight mode (user-confirmed)
Disable Wi-Fi/media streaming as appropriate; keep local clock, sensors, offline HUD,
downloaded translation, and essential local safety. Follow airline/user Bluetooth rules
rather than assuming Bluetooth must be off.

## 6. Audio (two independent paths)
Bone conduction: 2× ~8 Ω 1 W transducers near mastoid on compliant TPU mounts (no hard clamp).
Open/outward: 2× ~8 Ω 1–2 W micro speakers, directional/open-ear. Amps: 2× MAX98357A I2S
(one bone, one outward), independent enables → BONE / OUTWARD / BOTH / MUTE. App controls the
mix; firmware enforces a safe maximum volume. Safety cues use short recognizable patterns, not
long speech: LOW visual-only → MEDIUM visual+tone → HIGH visual+bone cue → URGENT distinct
bone cue + concise spoken warning.

## 7. Microphone privacy wiring (build exactly this)
DPST momentary PTT button. Pole A: 3.3 V → physical switch → MIC_3V3 → microphone.
Pole B: switch → ESP32 PTT input. Red privacy LED + ~1k resistor powered directly from MIC_3V3.
Voice flow: hold PTT → mic powered → speak → release → mic power removed → captured audio to
phone/local → ASR → AI/translation → response to HUD and/or audio. No wake word.

## 8. Translation
Online: phone/cloud does ASR, translation, AI, TTS. Offline: phone uses downloaded ASR +
translation + TTS packs (English, Spanish, French, German, Italian, Japanese, Korean, Mandarin,
extensible). Never promise every language works fully offline; ship downloadable language packs.

## 9. Display / HUD (optics stay experimental until §12 passes)
Real near-eye optics, NOT an LCD behind mirrored plastic:
MICRO-OLED → collimating/aspheric optic → partially reflective combiner (~30% reflect /
~70% transmit) → eye. Combiner is purchased optical-grade material — never FDM-transparent
plastic. HUD shows time, temp, battery, phone/Wi-Fi state, translation, AI responses, nav,
mic status, audio path, drive-safe + flight-mode indicators, obstacle warnings, notifications,
optional media. Minimal, non-obstructive; never permanently cover central vision.
MONOCULAR FIRST: build one eye, validate focus, eyebox, brightness, combiner angle, display
distance, collimator position, comfort, peripheral vision, alignment — before buying a second
microdisplay. Prototype target 640×400-class micro-OLED in an adjustable housing whose focal
spacing can be changed experimentally.

## 10. Power
Battery: protected 1S LiPo ~1200 mAh, removable/serviceable, away from heat and hard skin
pressure, puncture-protected, reputable cell. Charging: USB-C BQ24074 load-sharing power-path
charger + 10k NTC thermistor bonded to the pack; safe to operate while powered. Regulation:
5 V boost ≥ ~1 A core; media module gets its OWN supply ≥ ~2 A (never run media current through
ESP32-class traces). Real mechanical SPST/DPST main power switch isolating the system from the
battery/load path except circuitry required for safe charging/protection.

## 11. Optional media subsystem (only after core works)
Raspberry Pi Zero 2 W (or a justified better low-power part) for H.264/video, high-res graphics,
image decode, streaming, advanced UI. Target 720p/1080p-class micro-OLED. Path: phone → Wi-Fi →
media computer → micro-OLED controller → display → optics. If ESP32 says MEDIA_EN LOW, video
stops regardless of what the media computer requests.

## 12. Bill of materials (priced; CORE ≈ $172, +HUD ≈ $341 total, +MEDIA ≈ $540 total)
CORE — XIAO ESP32-S3 (~$7.49) · VL53L5CX / SparkFun Qwiic Mini ToF (~$25.95) · ICM-42688-P
(~$15) · BMP390 (~$10.99) · SHT40 (~$5.95) · SPH0645LM4H I2S mic (~$6.95) · 2× MAX98357A
(~$5.95 ea) · 2× 8 Ω 1 W bone transducer (~$8 ea) · 2× 8 Ω 1–2 W micro speaker (~$4 ea) ·
BQ24074 USB-C charger (~$14.95) · protected 1S LiPo 1200 mAh (~$9.95) · TPS61023-class 5 V
boost (~$6) · 10k NTC (~$1) · DPST momentary PTT (~$4) · SPST/DPST main slide switch (~$2) ·
red LED + 1k resistor (~$0.25) · 28–32 AWG silicone wire + JST-SH/Qwiic pigtails (~$10) ·
M2 5/6 mm screws + M2 heat-set inserts (~$8) · 95A TPU + 1–2 mm silicone/foam tape (~$8).
HUD — 2× ~30R/70T optical combiner (~$25 ea) · 640×400-class micro-OLED + driver (~$99;
confirm controller compatibility BEFORE purchase) · 20–25 mm collimating/aspheric lens +
adjustable holder (~$20). Buy second-eye parts only after monocular optics succeed.
MEDIA (optional) — Pi Zero 2 W (~$14.99) · 720p/1080p micro-OLED + controller (~$150) ·
2000–3000 mAh LiPo + 5 V ≥2 A (~$25) · 32 GB A1/A2 microSD (~$7).
Sourcing: keep the priced source URLs from bom.csv; deliver the final BOM as a table with
live links. Confirm every module's real datasheet dimensions before CAD pockets are sized.

## 13. CAD (delivered as parametric OpenSCAD; 17 parts; PETG/ASA structure, TPU 95A grips)
Source: adaptive_smart_glasses.scad + config.scad (all tunable dims) + README_CAD.md +
customization.md + print_manifest.csv. Parts (STL + 3MF): front_frame, temple_left/right,
temple_cover_left/right, ear_grip_left/right, sensor_pod, optics_pod_left/right,
optics_pod_cover, combiner_blank, rear_battery_pod/cover, rear_compute_pod/cover,
decorative_brow_insert. Decorative pieces separate from structural — cosmetics swap without
replacing the frame.
Improvement priorities: reduce frame/temple thickness and mass; size every pocket from REAL
measured modules; FDM tolerance 0.25–0.50 mm/side tuned with coupons; connector + wire
clearance; wire channels + strain relief; stronger hinges with cabling that survives repeated
folding; better balance, nose fit, ear fit, optical adjustment, cover retention; easier
assembly; cooling; serviceability. Do NOT trap dev boards behind rigid rear walls when
Dupont/Qwiic connectors must exit — use edge retention, open-backed supports, rails, clips, or
standoffs with generous clearance. Fasteners M2×5/6 mm + heat-set inserts for repeatedly-opened
covers. Print on Bambu Lab P1S (parts should also fit A1 / A1 Mini where dimensions allow);
minimize supports, choose print orientation intentionally.

## 14. Firmware (modular; ESP-IDF on ESP32-S3)
Modules: power_manager, sensor_manager, imu_service, tof_service, pressure_service,
ambient_service, ptt_audio_service, audio_router, display_service, ble_service, wifi_service,
phone_link, safety_policy, drive_state_machine, flight_mode, hazard_detector, thermal_manager,
battery_manager, diagnostics, firmware_update. Obstacle thresholds: forward object < ~0.8 m →
brief warning; < ~0.45 m → urgent; < ~1.5 m and rapidly closing → urgent; give LEFT/CENTER/
RIGHT when possible; invalid reading ≠ clear path. safety_policy and drive_state_machine are
authoritative over media_enable. Keep host-testable logic separate from hardware drivers.

## 15. Phone app
Pairing, BLE, Wi-Fi session mgmt, battery level, sensor health, temperature, HUD brightness/
themes/color/layout, audio mix (bone/outward/both/mute), AI voice on/off, translation config +
language packs, media casting, firmware update, diagnostics, drive-safe indication, flight-mode
control, privacy + data-retention controls. The app must NEVER bypass DRIVE_SAFE.

## 16. Build phases (bench before frame; monocular before binocular; media last)
1 Bench electronics: ESP32-S3 + IMU + VL53L5CX + BMP390 + SHT40 + PTT mic + one MAX98357A +
  one bone transducer; verify I2C, I2S, sensor detection, PTT, physical mic power gating,
  privacy LED, BLE, basic safety state machine. 2 Power: BQ24074 + protected battery + NTC +
  boost + main switch; test charging, battery temp, current, brownout, power-off, load sharing,
  max audio demand. 3 Frame: print + fit electronics WITHOUT optics; test fit/comfort/balance/
  routing/clearance/PTT location/USB-C access/heat/ear+nose pressure. 4 Depth: mount ToF, zone
  map, test wall/door/person/chair/left/right/dark/reflective/glass/approaching/failure; log
  false pos/neg. 5 One-eye display: tune focus, eyebox, combiner angle, virtual image, bright-
  ness, pupil position. 6 AI/translation: PTT audio → ASR → AI → translation → TTS → HUD + bone,
  then offline packs. 7 Driving safety: fuse GNSS+IMU; verify DRIVE_SAFE, MEDIA_EN low, app
  can't re-enable. 8 Flight/altitude: low pressure only prompts. 9 Media: add processor +
  hi-res display; verify video dies instantly on MEDIA_EN low; measure heat/runtime/Wi-Fi/
  latency. 10 Custom PCB (rigid-flex or small rigid boards + flex) after modules prove out.

## 17. Validation gates (must all pass)
PTT released ⇒ mic physically unpowered. Privacy LED can't activate independent of mic rail.
Battery stays within safe temp/current/voltage. Visual media can't bypass DRIVE_SAFE. GNSS loss
has explicit defined safe behavior. Invalid depth ≠ clear path. Optics don't dangerously obscure
central vision. Audio at safe listening levels. No sharp edges on skin. Hinge cabling survives
repeated folding. Battery never flexes/pinches/punctures/overheats. Frame survives realistic
handling and small drops.

## 18. Deliverable status labels (use on everything)
Mark each subsystem FINISHED / PROTOTYPE-READY / EXPERIMENTAL. Distinguish what the hardware
actually supports today from what is aspirational. Optics and media are EXPERIMENTAL until their
bench tests pass.

## 19. Cost discipline
Low-cost sensors + ESP32 for core; PHONE does expensive AI; no cloud-class compute on the
glasses; Pi/media only if video is needed; one display first; dev modules first, custom PCB
after validation. Optics will remain the most expensive subsystem.