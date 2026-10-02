// ============================================================================
// Adaptive Smart Glasses — config.scad  (ALL tunable dimensions live here)
// Units: mm.  Assembly coordinates (wearer's view):
//   +X = wearer's LEFT, -X = wearer's RIGHT
//   +Y = backward (toward the head), frame FRONT face is Y = 0
//   +Z = up, Z = 0 is the lens centre line
// Values marked [MEASURE] are datasheet/estimate values: measure your actual
// module with calipers and edit before printing the final version.
// ============================================================================

// ---------- print tolerances (tune with the tolerance_coupon part) ----------
tol          = 0.30;   // general clearance per side for pockets (0.25–0.50)
tol_tight    = 0.15;   // press/crush fits
fn_fine      = 64;     // $fn for round features on export
fn_coarse    = 32;

// ---------- head fit ----------
ipd          = 63;     // inter-pupillary distance; sets HUD combiner X
head_width   = 148;    // head breadth just above the ears (sets temple splay)
ear_y        = 100;    // hinge-axis -> ear-bend distance along temple (temple "A" length)
ear_droop    = 55;     // earpiece angle below horizontal (deg)
earpiece_len = 40;     // bend -> tip length

// ---------- front frame ----------
lens_w       = 52;     // lens opening width
lens_h       = 36;     // lens opening height
lens_r       = 10;     // lens opening corner radius
dbl          = 20;     // distance between lenses (bridge width)
rim          = 3.6;    // rim width around lens opening
frame_depth  = 6.0;    // rim depth (front->back) below the brow
brow_z0      = lens_h/2 - 1;  // brow bar bottom
brow_z1      = 31.0;          // brow bar top (browline style holds sensors + harness)
brow_depth   = 8.0;    // brow + endpiece depth
endpiece_w   = 5.4;    // endpiece width outboard of the rim
endpiece_z0  = -12;    // endpiece bottom
bridge_depth = 11.0;   // centre sensor pod depth (ToF + Qwiic plugs)

// ---------- hinge (hollow brass tube pin, wires run THROUGH the axis) ----------
tz           = 15;     // temple centre-line height (Z) at the hinge
knuckle_r    = 3.3;    // knuckle outer radius
tube_od      = 4.0;    // K&S 9822 brass tube OD (ID ~3.1)
tube_hole_glue = 4.05; // temple knuckle bore (tube is glued here)  [coupon]
tube_hole_run  = 4.35; // frame knuckle bore (tube rotates here)    [coupon]
flare_d      = 6.4;    // counterbore for the flared/washered tube top
tk_z         = [-6.5, -1.5]; // temple knuckle Z range (local)
fk_z         = [-1.2,  7.8]; // frame knuckle Z range (local)
hinge_gap    = 0.25;   // clearance between moving faces

// ---------- temple / pods ----------
bar_in       = -knuckle_r;   // temple inner face (local x). Flat => print face
bar_t        = 5.0;          // temple bar thickness
pod_y0       = 6.0;          // pod start (local y, from hinge axis)
pod_len      = 88.2;         // pod outer length
pod_h        = 23.0;         // pod outer height
pod_cav_t    = 10.0;         // pod cavity depth (x)
pod_wall     = 1.2;          // pod top/bottom walls
pod_inwall   = 1.0;          // inner (head-side) wall
pod_endwall  = 1.6;          // front/rear walls (USB-C needs <=1.6)
lid_t        = 1.4;
rib_w        = 6.0;          // centre rib carrying the lid screw insert
rib_y        = 47.5;         // rib start, measured from cavity start

// ---------- fasteners ----------
insert_hole_d = 3.1;   // ruthex M2 insert (OD 3.6, L 4.0)              [coupon]
insert_depth  = 5.5;
m2_clear      = 2.4;
m2_head_d     = 4.2;
m2_tap        = 1.75;  // M2 self-tap pilot in PETG

// ---------- modules (L along temple / X, H vertical, T thickness) ----------
// SparkFun Qwiic Mini ToF Imager VL53L5CX (SEN-19013): 25.4 x 12.7 (Eagle file)
tof_w = 25.4; tof_h = 12.7; tof_pcb = 1.6; tof_sensor_from_top = 3.8;
tof_back = 7.0;              // Qwiic vertical sockets + plugs behind PCB [MEASURE]
tof_z0   = 16.6;             // PCB bottom edge height
// GY-BME280 3.3 V I2C module (temp/humidity/pressure)                [MEASURE]
bme = [15.5, 12.0, 3.0];     // w(X), h(Z), t(Y)
bme_x0 = 22;                 // left brow
// Adafruit bq25185 charger + 5 V boost (#6106): 29.21 x 19.05 (Eagle file)
chg = [29.21, 19.05, 5.5];   // USB-C at one short end, overhang 3.2
chg_holes = [[2.54,2.54],[26.67,2.54],[2.54,16.51],[26.67,16.51]];
// Protected 1S LiPo 8 x 20 x 46 mm (PKCELL LP802046 class, ~800 mAh) [MEASURE]
batt = [46, 20, 8.0];
// Seeed XIAO ESP32-S3 (non-Sense): 21 x 17.5                          [MEASURE height]
xiao = [21.0, 17.5, 4.2];
// Adafruit LSM6DSOX STEMMA QT (#4438): 25.4 x 17.78 x 4.53 (Eagle/STEP)
imu  = [25.4, 17.78, 4.53];
// Adafruit SPH0645 I2S mic (#3421): ~16.5 x 12.7                       [MEASURE]
mic  = [16.51, 12.7, 2.6];
// Adafruit MAX98357A (#3006): 19.05 x 17.78 x 2.57 (STEP)
amp  = [19.05, 17.78, 2.6];
// 15 mm round 8 ohm micro speaker                                      [MEASURE]
spk_d = 15.2; spk_t = 4.5;
// Adafruit bone conductor transducer (#1674)                           [MEASURE]
bone = [22.0, 14.5, 8.0];
bone_left = false;           // optional 2nd transducer cradle on the left grip
// PTT: 6x6 tactile switch (Omron B3F-1000 class) under a flexure button
ptt = [6.2, 6.2, 4.3];       // footprint x, y, total height incl. plunger
// Main power slide switch: E-Switch 500SSP1S1M6QEA (13.21 x 6.6 x 6.72) [MEASURE actuator]
msw = [13.4, 6.8, 6.9];
msw_slot = [7.5, 3.0];       // actuator slot (length along Z, width)
// Privacy LED: 3 mm, flange 3.8
led_d = 3.1; led_flange_d = 4.0;

// ---------- HUD optics (EXPERIMENTAL, monocular, wearer's RIGHT eye) ----------
hud_side      = -1;          // -1 = right eye, +1 = left eye
comb_d        = 25.0;        // Edmund #35-933 Ø25 x 1 mm 30R/70T (or 25 x 25 plate)
comb_t        = 1.0;
comb_tilt     = 45;          // nominal; adjustable 35..55 on the pivot
comb_cy       = -14.8;       // combiner centre Y (in front of frame)
comb_cz       = 6.0;         // combiner centre Z (slightly above pupil line)
lens_d        = 25.0;        // Edmund #66-008 Ø25 f25 asphere
lens_ct       = 7.4;
lens_bfl      = 20.2;        // approx back focal length — tune with slider
disp_mod      = [15.6, 13.6, 2.0];  // 0.23" 640x400 micro-OLED module  [MEASURE]
disp_active   = [8.2, 6.2];
slider_travel = 12;          // focus adjustment range
tower_wall    = 1.6;
