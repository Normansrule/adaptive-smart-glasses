// ============================================================================
// Adaptive Smart Glasses v0.2 — camera-passthrough glasses (parametric, P1S-printable)
//
//   openscad -D 'part="visor_shell"' -o visor_shell.stl adaptive_smart_glasses.scad
//   part = assembly | assembly_up | frame | temple_left | temple_right | ear_grip_left
//          | ear_grip_right | visor_shell | visor_back | tolerance_coupon
//   part="asm" + which="<part>"  -> that part in assembly position (web viewer)
//
// Layout: slim FRAME on the face (nose pads, temples, hinges). Batteries sit in the
// EARPIECES (counterweight). A flip-up VISOR hinges on the brow and carries everything
// else: 2 inward micro-OLED eyepieces, 2 outward 1.69" design screens, centre camera,
// XIAO ESP32-S3, IMU, display driver board, power / camera-privacy switches, action button.
// Status: PROTOTYPE-READY mechanics (fit-check first); optics + passthrough EXPERIMENTAL.
// ============================================================================
include <config.scad>

part  = "assembly";
which = "frame";
up_deg = 0;      // visor angle for part="asm" (0 = down, visor_up_deg = up)
$fn   = fn_coarse;

// ---------------- derived ----------------
lens_cx  = dbl/2 + lens_w/2;
half_w   = dbl/2 + lens_w + rim + endpiece_w;
axis_x   = half_w - knuckle_r;
axis_y   = brow_depth + knuckle_r + hinge_gap;
splay    = atan((head_width/2 + 1 - (axis_x + bar_in)) / ear_y);
ear_dir  = [cos(ear_droop), -sin(ear_droop)];
ear_B    = [ear_y, 0];
ear_T    = ear_B + earpiece_len*ear_dir;
function ear_pt(s) = ear_B + s*ear_dir;
vf       = visor_rear_y - visor_depth;   // visor front face (Y)
sb       = visor_rear_y - 2;             // shell back opening (back plate is 2 mm)
pod_mz   = (pod_z[0] + pod_z[1]) / 2;
VA       = [0, visor_axis[0], visor_axis[1]];   // visor axis point (X ignored)

// ---------------- helpers ----------------
module rr2(w, h, r) { offset(r=r) square([max(w-2*r,0.01), max(h-2*r,0.01)], center=true); }
module yz(x0, x1) { multmatrix([[0,0,1,0],[1,0,0,0],[0,1,0,0],[0,0,0,1]]) translate([0,0,x0]) linear_extrude(x1-x0) children(); }
module xz(y0, y1) { translate([0,y1,0]) rotate([90,0,0]) linear_extrude(y1-y0) children(); }
module cubeb(a, b) { translate(a) cube(b - a); }
module cyl_y(d, y0, y1) { translate([0,y0,0]) rotate([-90,0,0]) cylinder(d=d, h=y1-y0, $fn=fn_fine); }
module cyl_x(d, x0, x1) { translate([x0,0,0]) rotate([0,90,0]) cylinder(d=d, h=x1-x0, $fn=fn_fine); }

// ============================================================================
// FRAME — slim carrier (print: front face down). Visor knuckles sit on the brow top.
// ============================================================================
module lens2d() { rr2(lens_w, lens_h, lens_r); }
module frame_rims2d() {
    for (s=[-1,1]) translate([s*lens_cx,0]) offset(r=rim) lens2d();
    translate([-8, 6]) square([16, brow_z0 - 5]);
}
module frame_brow2d() {
    offset(r=2.5) offset(delta=-2.5) union() {
        translate([-half_w, brow_z0]) square([2*half_w, brow_z1-brow_z0]);
        for (s=[-1,1]) translate([s>0 ? half_w-endpiece_w-rim-1 : -half_w, endpiece_z0]) square([endpiece_w+rim+1, brow_z1-endpiece_z0]);
    }
}
module temple_lug_local() {
    hull() {
        cubeb([-1.5, -(axis_y-brow_depth)-0.5, fk_z[0]], [knuckle_r, -(axis_y-brow_depth), fk_z[1]]);
        translate([0,0,fk_z[0]]) cylinder(r=knuckle_r, h=fk_z[1]-fk_z[0], $fn=fn_fine);
    }
}
module temple_lug_cuts_local() {
    translate([0,0,fk_z[0]-1]) cylinder(d=tube_hole_run, h=20, $fn=fn_fine);
    translate([0,0,fk_z[1]-1.5]) cylinder(d=flare_d, h=5, $fn=fn_fine);
    cubeb([-1.25, -6, fk_z[1]-2.5], [1.25, 0, fk_z[1]+1]);
}
module frame_body() {
    xz(0, frame_depth) frame_rims2d();
    xz(0, brow_depth)  frame_brow2d();
    for (s=[-1,1]) translate([s*8.0, frame_depth+1.0, 1]) rotate([0,0,s*25]) cube([3, 3, 13], center=true);  // nose-pad lands
    for (s=[-1,1]) translate([s*axis_x, axis_y, tz]) mirror([s<0?1:0,0,0]) temple_lug_local();
    for (s=[-1,1]) mirror([s<0?1:0,0,0]) {                                      // visor knuckles on brow top
        translate([frame_vknuckle_x[0], visor_axis[0], visor_axis[1]]) cyl_x(2*knuckle_r, 0, frame_vknuckle_x[1]-frame_vknuckle_x[0]);
        cubeb([frame_vknuckle_x[0], max(0, visor_axis[0]-knuckle_r), brow_z1-2], [frame_vknuckle_x[1], visor_axis[0]+knuckle_r, visor_axis[1]]);
    }
}
module frame_cuts() {
    for (s=[-1,1]) translate([s*lens_cx,0,0]) xz(-1, 30) lens2d();
    for (s=[-1,1]) translate([s*axis_x, axis_y, tz]) mirror([s<0?1:0,0,0]) temple_lug_cuts_local();
    for (s=[-1,1]) mirror([s<0?1:0,0,0]) {
        translate([frame_vknuckle_x[0]-1, visor_axis[0], visor_axis[1]]) cyl_x(visor_tube_run, 0, 20);   // visor tube (turns, snug)
        translate([frame_vknuckle_x[1]-1.5, visor_axis[0], visor_axis[1]]) cyl_x(flare_d, 0, 5);         // flare / washer seat
        // wire path: temple knuckle top -> endpiece -> visor knuckle outer end
        cubeb([axis_x-1.25, 2.0, tz+fk_z[1]-2.5], [axis_x+1.25, axis_y, tz+fk_z[1]]);
        cubeb([frame_vknuckle_x[1]-0.8, 2.0, tz+fk_z[1]-2.5], [frame_vknuckle_x[1]+1.5, 4.6, visor_axis[1]]);
        cubeb([axis_x-1.25, 2.0, tz+fk_z[1]-2.5], [frame_vknuckle_x[1]+1.5, 4.6, tz+fk_z[1]]);
    }
    cubeb([-axis_x+1, 3.6, brow_z0+1.5], [axis_x-1, brow_depth+1, brow_z0+4.0]);     // cross-brow groove (right cell)
    translate([0, -0.01, brow_z0+3.8]) cyl_y(magnet[0], 0, magnet[1]);                // hall-sensor magnet
}
module frame() { difference() { frame_body(); frame_cuts(); } }

// ============================================================================
// TEMPLES (local: origin on hinge axis at z = tz, +y back, +x outward, head face x = bar_in)
// The earpiece holds one protected cell, covered by the TPU grip.
// ============================================================================
module bar2d() {
    translate([0,-9]) square([7, 16]);
    hull() { translate([8,0]) circle(r=4); translate(ear_B) circle(r=4); }
}
module earpiece2d(g=0) {
    offset(delta=g) hull() {
        translate(ear_B) circle(r=4);
        translate(ear_pt(cell_s0+3)) circle(r=cell[1]/2+1.6);
        translate(ear_pt(cell_s0+cell[0]-3)) circle(r=cell[1]/2+1.6);
        translate(ear_T) circle(r=4.6);
    }
}
ear_t1 = bar_in + cell[2] + 0.4 + 1.4;   // earpiece outer face
module ear_frame() { translate([0, ear_B[0], ear_B[1]]) rotate([-ear_droop,0,0]) children(); }
module temple_body() {
    yz(bar_in, bar_in+bar_t) bar2d();
    yz(bar_in, knuckle_r) translate([0,-9]) square([5, 16]);
    hull() { yz(bar_in, ear_t1-0.8) earpiece2d(); yz(bar_in, ear_t1) earpiece2d(-0.8); }
}
module temple_hinge_part() {
    translate([0,0,-9]) cylinder(r=knuckle_r, h=tk_z[1]+9, $fn=fn_fine);
    cubeb([0.3, -(axis_y-brow_depth)+0.1, -9], [knuckle_r, 0, -6.8]);       // open stop
}
module temple_cuts() {
    ear_frame() cubeb([bar_in-0.1, cell_s0, -(cell[1]/2+0.2)], [bar_in+cell[2]+0.4, cell_s0+cell[0]+0.5, cell[1]/2+0.2]);  // cell bay
    yz(bar_in-0.1, bar_in+1.4) {                                             // wire groove, head side
        hull() { translate(ear_pt(cell_s0+1)) circle(d=1.8, $fn=12); translate(ear_B+[0,-1]) circle(d=1.8, $fn=12); }
        hull() { translate(ear_B+[0,-1]) circle(d=1.8, $fn=12); translate([5,-1]) circle(d=1.8, $fn=12); }
        hull() { translate([5,-1]) circle(d=1.8, $fn=12); translate([5,-7.2]) circle(d=1.8, $fn=12); }
    }
    cubeb([bar_in-0.1, -0.5, -8.6], [bar_in+2.0, 5.9, -6.6]);
}
module temple_local(side, splayed=true) {
    difference() {
        union() {
            rotate([0,0, splayed ? -splay : 0]) difference() {
                temple_body();
                temple_cuts();
                translate([0,0,fk_z[0]-hinge_gap]) cylinder(r=knuckle_r+hinge_gap+0.2, h=20, $fn=fn_fine);
                translate([-10,-10,fk_z[0]-hinge_gap]) cube([20, 10, 20]);
            }
            temple_hinge_part();
        }
        translate([0,0,-8.6]) cylinder(d=3.4, h=2.2, $fn=24);
        translate([0,0,tk_z[0]-0.1]) cylinder(d=tube_hole_glue, h=tk_z[1]-tk_z[0]+0.2, $fn=fn_fine);
        rotate([0,0, splayed ? -splay : 0]) cubeb([bar_in-0.1, -0.5, -8.6], [bar_in+2.0, 2, -6.6]);
    }
}
module ear_grip_local(side) {        // TPU sleeve: holds the cell in, comfortable behind the ear
    difference() {
        intersection() {
            hull() { yz(bar_in-1.2, ear_t1+0.4) earpiece2d(1.2); yz(bar_in-0.6, ear_t1+1.2) earpiece2d(0.6); }
            ear_frame() translate([-50, 1, -50]) cube(100);
        }
        hull() { yz(bar_in-0.1+0.1, ear_t1-0.8) earpiece2d(-0.1); yz(bar_in+0.1, ear_t1-0.1) earpiece2d(-0.9); }
        ear_frame() translate([-50, -99, -50]) cube(100);
    }
}

// ============================================================================
// VISOR — flip-up display unit (print shell front-face down, back plate back-face down)
// ============================================================================
module visor2d(g=0) {
    offset(r=g) difference() {
        union() {
            for (s=[-1,1]) translate([s*pod_cx, pod_mz]) rr2(pod_w, pod_z[1]-pod_z[0], pod_r);
            translate([-bridge_hw, pod_z[0]]) square([2*bridge_hw, crest_z[1]-pod_z[0]]);
            translate([-(bridge_hw+pod_r), pod_z[1]-pod_r]) square([2*(bridge_hw+pod_r), pod_r+1]);   // fill pod/bridge notch
            translate([0, (crest_z[0]+crest_z[1])/2]) rr2(2*crest_hw, crest_z[1]-crest_z[0], 4);
        }
        polygon([[-nose_base_hw, pod_z[0]-1], [nose_base_hw, pod_z[0]-1], [0, nose_apex_z]]);
    }
}
module visor_knuckle_arm(s) {        // links pod top to the hinge knuckle above the brow
    mirror([s<0?1:0,0,0]) {
        cubeb([visor_knuckle_x[0], vf+12, pod_z[1]-8], [visor_knuckle_x[1], sb, visor_axis[1]+knuckle_r]);
        cubeb([visor_knuckle_x[0], sb-1, visor_axis[1]-1.5], [visor_knuckle_x[1], visor_axis[0], visor_axis[1]+knuckle_r]);
        translate([visor_knuckle_x[0], visor_axis[0], visor_axis[1]]) cyl_x(2*knuckle_r, 0, visor_knuckle_x[1]-visor_knuckle_x[0]);
    }
}
module visor_shell() {
    difference() {
        union() {
            xz(vf+1.0, sb) visor2d();
            xz(vf+0.5, vf+1.0) visor2d(-0.5);
            xz(vf, vf+0.5) visor2d(-1.0);
            for (s=[-1,1]) visor_knuckle_arm(s);
        }
        xz(vf+wall, sb+1) visor2d(-wall);                                     // cavity, open at back
        for (s=[-1,1]) translate([s*pod_cx, 0, pod_mz])                       // outward LCD windows
            xz(vf-1, vf+wall+0.1) rr2(lcd_active[0]+0.6, lcd_active[1]+0.6, 3);
        translate([0, 0, cam_z]) xz(vf-1, vf+wall+0.1) circle(d=cam_lens_d, $fn=fn_fine);   // camera
        translate([16, 0, 25]) xz(vf-1, vf+wall+0.1) circle(d=3.1, $fn=24);  // CAMERA-LIVE LED (on camera power)
        // crest top: main switch, camera-privacy switch (slots) + action button flexure, on wearer's left
        for (y=[vf+8, vf+17]) translate([22.5, y, crest_z[1]-wall-0.1]) cube([2.4, 4.2, wall+0.2], center=false);
        translate([22.5-2.9+1.2, vf+23, crest_z[1]-wall-0.1]) difference() {
            cube([5.8, 7.0, wall+0.2]); translate([0.6, -0.1, -0.1]) cube([4.6, 6.4, wall+0.4]);
        }
        translate([crest_hw-wall-1, -20-cable_slot[0]/2, 25-cable_slot[1]/2]) cube([wall+2, cable_slot[0], cable_slot[1]]);  // cable in
        for (s=[-1,1]) mirror([s<0?1:0,0,0]) {                                 // visor tube (glued) + wire channel (left)
            translate([visor_knuckle_x[0]-0.1, visor_axis[0], visor_axis[1]]) cyl_x(tube_hole_glue, 0, visor_knuckle_x[1]-visor_knuckle_x[0]+0.2);
            cubeb([visor_knuckle_x[0]-4, visor_axis[0]-1.7, pod_z[1]-9], [visor_knuckle_x[0]+1, visor_axis[0]+1.7, visor_axis[1]+1.7]);
        }
    }
    // inside: LCD corner stops, HDMI-board front rail, back-plate screw bosses
    for (s=[-1,1]) for (dx=[-1,1], dz=[-1,1]) translate([s*pod_cx + dx*(lcd[0]/2+0.3+0.5) - 0.5, vf+wall, pod_mz + dz*(lcd[1]/2-4) - 2])
        cube([1, lcd[2]+0.6, 4]);
    cubeb([-crest_hw+wall+2.6, vf+wall, crest_z[0]+1.2], [crest_hw-12, vf+wall+3, crest_z[0]+2.4]);
    for (s=[-1,1], z=[-12, 8]) translate([s*53, 0, z]) difference() {
        cyl_y(6, sb-7, sb); cyl_y(insert_hole_d, sb-insert_depth, sb+0.1);
    }
}
module visor_back() {
    difference() {
        union() {
            xz(sb, visor_rear_y) visor2d();
            xz(sb-1.5, sb) difference() { visor2d(-wall-0.3); visor2d(-wall-1.5); }                 // locating lip
            for (s=[-1,1]) translate([s*ipd/2, 0, 0]) xz(sb-eyepiece_len, sb) circle(d=eyepiece_d+2.2, $fn=96);  // eyepiece sleeves
            cubeb([-crest_hw+wall+3, sb-3, crest_z[0]+1.2], [crest_hw-12, sb, crest_z[0]+2.4]);  // HDMI-board rear rail
        }
        for (s=[-1,1]) translate([s*ipd/2, 0, 0]) {
            xz(sb-eyepiece_len-1, sb-1.2) circle(d=eyepiece_d+0.4, $fn=96);
            xz(sb-2, visor_rear_y+1) circle(d=eyepiece_d-4, $fn=96);                                 // exit pupil aperture
            for (a=[90, 210, 330]) rotate([0,a,0]) translate([0, sb-eyepiece_len-1, eyepiece_d/2+0.2]) cube([2.4, 2*eyepiece_len, 1.2], center=true);  // FPC/flex reliefs
        }
        for (s=[-1,1], z=[-12, 8]) translate([s*53, 0, z]) {
            cyl_y(m2_clear, sb-2, visor_rear_y+1); cyl_y(m2_head_d, visor_rear_y-1.2, visor_rear_y+1);
            cyl_y(6.8, sb-2, sb);                                                  // lip clears the bosses
        }
        for (s=[-1,1]) mirror([s<0?1:0,0,0]) cubeb([visor_knuckle_x[0]-0.4, sb-2, pod_z[1]-8.4], [visor_knuckle_x[1]+1, sb, crest_z[1]+5]);  // lip clears knuckle arms
    }
    // eyepiece crush ribs
    for (s=[-1,1], a=[0,120,240]) translate([s*ipd/2, 0, 0]) rotate([0,a,0]) translate([-0.6, sb-eyepiece_len, (eyepiece_d+0.4)/2-0.35]) cube([1.2, eyepiece_len-1.5, 0.5]);
}

// ============================================================================
// TOLERANCE COUPON
// ============================================================================
module tolerance_coupon() {
    difference() {
        cube([82, 30, 6]);
        for (i=[0:3]) translate([6+i*8, 7, 0.5]) cylinder(d=[3.0,3.1,3.2,3.3][i], h=6, $fn=48);
        for (i=[0:5]) translate([42+i*6, 7, -1]) cylinder(d=[4.0,4.05,4.1,4.2,4.35,4.5][i], h=8, $fn=64);
        for (i=[0:2]) translate([8+i*10, 20, 3]) cylinder(d=[6.0,6.2,6.4][i], h=4, $fn=48);   // magnet
        for (i=[0:3]) let(w=[6.0,6.2,6.4,6.6][i]) translate([46+i*8-w/2, 20-w/2, 2]) cube([w, w, 5]);
        translate([2, 0.6, 5.4]) linear_extrude(1) text("INS 3.0-3.3  TUBE 4.0 .05 .1 .2 .35 .5  MAG 6.0-6.4", size=1.8);
    }
}

// ============================================================================
// placement, print orientation, assembly
// ============================================================================
module place_temple(side) { translate([side*axis_x, axis_y, tz]) mirror([side<0?1:0,0,0]) children(); }
module place_body(side)   { place_temple(side) rotate([0,0,-splay]) children(); }
module visor_pose(up=0)   { translate(VA) rotate([-up,0,0]) translate(-VA) children(); }

module asm(p, up=0) {
    if (p=="frame") frame();
    if (p=="temple_left")    place_temple( 1) temple_local( 1);
    if (p=="temple_right")   place_temple(-1) temple_local(-1);
    if (p=="ear_grip_left")  place_body( 1) ear_grip_local( 1);
    if (p=="ear_grip_right") place_body(-1) ear_grip_local(-1);
    if (p=="visor_shell")    visor_pose(up) visor_shell();
    if (p=="visor_back")     visor_pose(up) visor_back();
}
module printed(p) {
    if (p=="frame")          rotate([90,0,0]) frame();
    if (p=="temple_left")    rotate([0,-90,0]) temple_local( 1, false);
    if (p=="temple_right")   rotate([0, 90,0]) mirror([1,0,0]) temple_local(-1, false);
    if (p=="ear_grip_left")  rotate([145,0,0]) translate([0,-ear_B[0],-ear_B[1]]) ear_grip_local( 1);
    if (p=="ear_grip_right") rotate([145,0,0]) translate([0,-ear_B[0],-ear_B[1]]) mirror([1,0,0]) ear_grip_local(-1);
    if (p=="visor_shell")    rotate([-90,0,0]) visor_shell();
    if (p=="visor_back")     rotate([90,0,0]) visor_back();
    if (p=="tolerance_coupon") tolerance_coupon();
}
module assembly(up=0) {
    color("#2b2f36") asm("frame");
    color("#3a4049") { asm("temple_left"); asm("temple_right"); }
    color("#1d1f22") { asm("ear_grip_left"); asm("ear_grip_right"); }
    color("#30353d") asm("visor_shell", up);
    color("#4a5260") asm("visor_back", up);
    visor_pose(up) for (s=[-1,1]) color([0.25,0.55,0.95]) translate([s*pod_cx, vf-0.01, pod_mz]) xz(0, 0.2) rr2(lcd_active[0], lcd_active[1], 3);
}

echo(str("DERIVED: half_w=", half_w, " splay=", splay, " visor front Y=", vf, " eye relief(mm)=", 16 - visor_rear_y));
if (part=="assembly") assembly(0);
else if (part=="assembly_up") assembly(visor_up_deg);
else if (part=="asm") asm(which, up_deg);
else printed(part);
