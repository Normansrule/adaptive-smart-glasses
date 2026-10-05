// ============================================================================
// Adaptive Smart Glasses v0.2 — config.scad (ALL tunable dimensions)
// Camera-passthrough glasses: flip-up display visor + slim frame + battery earpieces.
// Assembly coordinates (wearer's view): +X = wearer's LEFT, +Y = toward the head,
// +Z = up. Frame front face is Y = 0, pupils sit at Z = 0.
// [MEASURE] = estimate or vendor drawing not yet confirmed: measure your part, edit, rebuild.
// ============================================================================

// ---------- print tolerances (tune with tolerance_coupon) ----------
tol            = 0.30;
fn_fine        = 64;
fn_coarse      = 32;

// ---------- head fit ----------
ipd            = 63;     // pupil distance: centres both eyepieces
head_width     = 148;    // sets temple splay
ear_y          = 98;     // hinge axis -> ear bend
ear_droop      = 55;     // earpiece angle below horizontal
earpiece_len   = 50;     // bend -> tip (holds the battery)
eye_relief     = 17;     // cornea -> eyepiece exit (sets visor_rear_y)   [MEASURE optics]

// ---------- slim front frame (stays on the face; visor hinges on it) ----------
lens_w = 48; lens_h = 34; lens_r = 9; dbl = 18; rim = 3.0;
frame_depth    = 4.0;
brow_z0        = lens_h/2 - 1;
brow_z1        = 23;
brow_depth     = 6.0;
endpiece_w     = 4.5;
endpiece_z0    = -10;
magnet         = [6.2, 3.2];   // Ø x depth: 6x3 mm N52 disc, brow centre (hall sensor target)

// ---------- temple hinge (hollow brass tube, wires inside) ----------
tz             = 12;
knuckle_r      = 3.3;
tube_hole_glue = 4.05;
tube_hole_run  = 4.35;
flare_d        = 6.4;
tk_z           = [-6.5, -1.5];
fk_z           = [-1.2, 7.8];
hinge_gap      = 0.25;
bar_in         = -knuckle_r;   // temple head-side face (flat = print face)
bar_t          = 5.0;

// ---------- earpiece battery (one protected cell per side) ----------
cell           = [40, 10, 5.0];   // L x W x T: 501040 200 mAh (or LP401235 4x12x36) [MEASURE]
cell_s0        = 4;               // bay starts this far past the ear bend

// ---------- visor (flip-up display unit) ----------
visor_rear_y   = -1.6;            // eyepiece-side face
visor_depth    = 34.4;            // rear -> front
pod_cx         = 34.5;            // pod centre X (LCD centre)
pod_w          = 44;  pod_z = [-16, 20];  pod_r = 7;
bridge_hw      = 12.6;            // centre bridge half width (camera board 24 wide)
crest_hw       = 30;  crest_z = [19, 31];  // top bay: display driver board + controls
nose_apex_z    = 2;  nose_base_hw = 16;    // nose notch (apex height, half width at bottom)
wall           = 1.6;
visor_axis     = [3.3, 27.5];     // visor hinge axis (Y, Z) along X, sits on the brow top (frame prints front-down)
visor_knuckle_x = [50, 56.5];     // visor knuckle span (|X|)
frame_vknuckle_x = [57, 63];      // frame knuckle span (|X|)
visor_tube_run = 4.2;             // frame-side bore: snug = friction holds the visor up [coupon]
visor_up_deg   = 100;

// ---------- visor modules ----------
lcd            = [39.0, 31.5, 4.5];   // Waveshare 1.69" 240x280, landscape (W x H x T) [MEASURE T]
lcd_active     = [32.63, 27.97];
cam_board      = [24, 25, 1.6];       // Arducam IMX708 UVC 102 deg
cam_lens_d     = 12;                  // front aperture for the lens holder        [MEASURE]
cam_z          = 17;                  // camera board centre height
oled_panel     = [24.24, 15.62, 1.54];// Sony ECX335S 0.71" 1920x1080 (FPC exits top)
eyepiece_d     = 26;  eyepiece_len = 22;  // OPE07-10X prism eyepiece            [MEASURE]
hdmi_board     = [45, 28, 7];         // dual micro-OLED HDMI driver board           [MEASURE]
xiao           = [21, 17.5, 4.2];
imu            = [25.4, 17.78, 4.6];
sw_slide       = [7.65, 5.5, 4.5];    // Wurth 452403012014 DPDT body (x2)           [MEASURE]
ptt            = [6.2, 6.2, 4.3];     // 6x6 tact (action button)
cable_slot     = [11, 7];             // HDMI + USB bundle entry (crest left side)

// ---------- fasteners ----------
insert_hole_d  = 3.1;  insert_depth = 5.5;  m2_clear = 2.4;  m2_head_d = 4.2;  m2_tap = 1.75;
