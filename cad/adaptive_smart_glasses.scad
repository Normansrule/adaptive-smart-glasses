// ============================================================================
// Adaptive Smart Glasses — adaptive_smart_glasses.scad
// Parametric prototype frame for dev-module electronics. Edit config.scad.
//
//   openscad -D 'part="frame"'  -o frame.stl adaptive_smart_glasses.scad
//   part = assembly | frame | temple_left | temple_right | lid_left | lid_right
//          | ear_grip_left | ear_grip_right | optics_tower | display_slider
//          | combiner_arm | tolerance_coupon
//   prefix "asm_" (e.g. asm_frame) = that part in assembly position.
//
// Status: frame/temples/lids/grips PROTOTYPE-READY (fit-check first);
//         optics_tower/display_slider/combiner_arm EXPERIMENTAL.
// ============================================================================
include <config.scad>

part = "assembly";
$fn  = fn_coarse;

// ---------------- derived ----------------
lens_cx   = dbl/2 + lens_w/2;
half_w    = dbl/2 + lens_w + rim + endpiece_w;
axis_x    = half_w - knuckle_r;
axis_y    = brow_depth + knuckle_r + hinge_gap;
inner_at_hinge = axis_x + bar_in;
splay     = atan((head_width/2 + 1 - inner_at_hinge) / ear_y);
groove_z  = [19.5, 22.5];           // harness groove on brow back face
groove_y0 = 5.6;
cav_x0    = bar_in + pod_inwall;    // pod cavity inner face (local x)
cav_x1    = cav_x0 + pod_cav_t;     // pod rim / lid seat
cav_y0    = pod_y0 + pod_endwall;
cav_y1    = pod_y0 + pod_len - pod_endwall;
cav_h     = pod_h - 2*pod_wall;
rib_y0    = cav_y0 + rib_y;
rib_y1    = rib_y0 + rib_w;
ear_dir   = [cos(ear_droop), -sin(ear_droop)];       // (y,z)
ear_B     = [ear_y, 0];
ear_T     = ear_B + earpiece_len*ear_dir;
function ear_pt(s) = ear_B + s*ear_dir;
tof_sz    = tof_z0 + tof_h - tof_sensor_from_top;    // sensor centre height
hud_cx    = hud_side*ipd/2;
lens_top  = 18.4 + lens_ct + 0.4;                    // top of lens seat
tower_top = 58;
tower_in  = lens_d + 1.4;
tower_out = tower_in + 2*tower_wall;

// ---------------- helpers ----------------
module rr2(w, h, r) { offset(r=r) square([max(w-2*r,0.01), max(h-2*r,0.01)], center=true); }
module lens2d()     { rr2(lens_w, lens_h, lens_r); }
// 2D (u,v) -> local (y=u, z=v), extruded along x from x0 to x1
module yz(x0, x1) { multmatrix([[0,0,1,0],[1,0,0,0],[0,1,0,0],[0,0,0,1]])
                    translate([0,0,x0]) linear_extrude(x1-x0) children(); }
// 2D (x,z) extruded along +Y from y0 to y1
module xz(y0, y1) { translate([0,y1,0]) rotate([90,0,0]) linear_extrude(y1-y0) children(); }
module cubeb(a, b) { translate(a) cube(b - a); }                    // cube from corner a to b
module teardrop_y(d, l) { rotate([-90,0,0]) cylinder(d=d, h=l, $fn=fn_fine); }

// ============================================================================
// FRONT FRAME  (print: front face down)
// ============================================================================
module frame_outline_rims() {
    for (s=[-1,1]) translate([s*lens_cx,0]) offset(r=rim) lens2d();
    translate([-9, 6]) square([18, brow_z0 - 6 + 1]);               // bridge
}
module frame_outline_brow() {
    offset(r=3) offset(delta=-3) union() {
        translate([-half_w, brow_z0]) square([2*half_w, brow_z1-brow_z0]);
        for (s=[-1,1]) translate([s>0 ? half_w-endpiece_w-rim-1 : -half_w, endpiece_z0])
            square([endpiece_w+rim+1, brow_z1-endpiece_z0]);
    }
}
module hinge_lug_local() {
    hull() {   // inner side tapered so the folding temple clears it
        cubeb([-1.5, -(axis_y-brow_depth)-0.5, fk_z[0]], [knuckle_r, -(axis_y-brow_depth), fk_z[1]]);
        translate([0,0,fk_z[0]]) cylinder(r=knuckle_r, h=fk_z[1]-fk_z[0], $fn=fn_fine);
    }
}
module hinge_lug_cuts_local() {
    translate([0,0,fk_z[0]-1]) cylinder(d=tube_hole_run, h=20, $fn=fn_fine);
    translate([0,0,fk_z[1]-1.5]) cylinder(d=flare_d, h=5, $fn=fn_fine);           // flare/washer seat
    cubeb([-1.25, -6, fk_z[1]-2.5], [1.25, 0, fk_z[1]+1]);                       // wire exit -> brow groove
}
module frame_body() {
    xz(0, frame_depth) frame_outline_rims();
    xz(0, brow_depth)  frame_outline_brow();
    // centre sensor pod (ToF), behind the brow
    hull() for (x=[-13,13]) for (z=[brow_z0+0.5, brow_z1-2])
        translate([x,0,z]) rotate([-90,0,0]) cylinder(r=2, h=bridge_depth);
    // nose-pad lands for stick-on silicone pads
    for (s=[-1,1]) translate([s*8.3, frame_depth+1.0, 1]) rotate([0,0,s*25])
        cube([3.0, 3.0, 13], center=true);
    // hinge lugs
    for (s=[-1,1]) translate([s*axis_x, axis_y, tz]) mirror([s<0?1:0,0,0]) hinge_lug_local();
}
module frame_cuts() {
    // lens openings
    for (s=[-1,1]) translate([s*lens_cx,0,0]) xz(-1, 30) lens2d();
    // hinge bores + wire exits
    for (s=[-1,1]) translate([s*axis_x, axis_y, tz]) mirror([s<0?1:0,0,0]) hinge_lug_cuts_local();
    // harness groove along brow back face (open, wires press in; tape/silicone over)
    cubeb([-axis_x, groove_y0, groove_z[0]], [axis_x, bridge_depth+1, groove_z[1]]);
    // ---- ToF (SparkFun Mini VL53L5CX), sensor flush with front face ----
    hull() { cubeb([-4.5, -0.01, tof_sz-3.0], [4.5, 0.01, tof_sz+3.0]);       // flared window
             cubeb([-3.4, 1.9, tof_sz-1.7], [3.4, 1.91, tof_sz+1.7]); }
    cubeb([-3.4, 0.3, tof_sz-1.7], [3.4, 2.0, tof_sz+1.7]);                    // sensor package
    cubeb([-tof_w/2-tol, 1.9, tof_z0-tol], [tof_w/2+tol, 1.9+tof_pcb+0.2, tof_z0+tof_h+tol]);
    cubeb([-tof_w/2-tol, 1.9+tof_pcb, tof_z0-tol], [tof_w/2+tol, bridge_depth+1, tof_z0+tof_h+tol]);
    // ---- BME280 in LEFT brow, vented front + top, open back ----
    cubeb([bme_x0, 1.2, 18.0], [bme_x0+bme[0]+2*tol, brow_depth+1, 18.0+bme[1]+2*tol]);
    for (i=[0:3]) {
        translate([bme_x0+2.6+i*3.4, 0, 0]) {
            cubeb([-0.6, -1, 20.0], [0.6, 1.3, 28.6]);                          // front vents
            cubeb([-0.6, 1.6, 29.5], [0.6, 6.6, brow_z1+1]);                    // top vents
        }
    }
    // ---- RIGHT endpiece: PTT tact switch under a flexure tongue + privacy LED ----
    ex = -(half_w - 4.2);                                                     // endpiece cavity centre X
    pz1 = brow_z1 - 1.2;
    cubeb([ex-ptt[0]/2-tol/2, 0.9, pz1-ptt[2]], [ex+ptt[0]/2+tol/2, brow_depth+1, pz1]);
    difference() {                                                            // U-slot -> flexure button
        cubeb([ex-2.9, 0.9, pz1-0.1], [ex+2.9, 7.0, brow_z1+1]);
        cubeb([ex-2.3, 0.0, pz1-0.2], [ex+2.3, 6.4, brow_z1+2]);
    }
    translate([ex, -1, 23.4]) teardrop_y(led_d, 5.3);                          // LED lens hole
    translate([ex, 4.3, 23.4]) teardrop_y(led_flange_d, 5);                    // LED flange, open back
    // ---- LEFT endpiece: main power slide switch, actuator out the side ----
    sx0 = half_w - 1.0 - msw[2];
    cubeb([sx0, 0.8, -10.8], [half_w-1.0, brow_depth+1, -10.8+msw[0]]);
    cubeb([half_w-1.2, 4.4-msw_slot[1]/2, -4.1-msw_slot[0]/2], [half_w+1, 4.4+msw_slot[1]/2, -4.1+msw_slot[0]/2]);
    cubeb([sx0+0.2, groove_y0, -10.8+msw[0]-1], [sx0+2.2, brow_depth+1, groove_z[1]]);   // riser groove
    // ---- HUD tower mount: 2x M2 heat-set inserts in brow front (above HUD eye) ----
    for (dx=[-9,9]) translate([hud_cx+dx, -0.1, 27]) teardrop_y(insert_hole_d, insert_depth);
}
module frame() { difference() { frame_body(); frame_cuts(); } }

// ============================================================================
// TEMPLES (local frame: origin on hinge axis at z=tz; +y back; +x OUTWARD;
//          inner/head face is the flat plane x = bar_in -> print face)
// side: +1 = LEFT (battery + charger pod), -1 = RIGHT (compute + audio pod)
// ============================================================================
module temple_profile_bar() {
    translate([0,-9]) square([pod_y0+3, 16]);                                 // neck
    hull() { translate([pod_y0+pod_len-4, 0]) circle(r=4); translate(ear_B) circle(r=3); }
    hull() { translate(ear_B) circle(r=3); translate(ear_T) circle(r=2.3); }
}
module earpiece_solid(grow=0) {
    yz(bar_in-grow, bar_in+bar_t+grow) offset(delta=grow)
        hull() { translate(ear_B) circle(r=3); translate(ear_T) circle(r=2.3); }
}
module pod_outline2d() { translate([pod_y0+pod_len/2, 0]) rr2(pod_len, pod_h, 4); }
module cavity_outline2d(g=0) { translate([(cav_y0+cav_y1)/2, 0]) rr2(cav_y1-cav_y0-2*g, cav_h-2*g, 2); }

module temple_body() {
    yz(bar_in, bar_in+bar_t) temple_profile_bar();
    yz(bar_in, knuckle_r) translate([0,-9]) square([pod_y0+1, 16]);           // full-width neck
    hull() {                                                                  // pod, outer edges chamfered
        yz(bar_in, cav_x1-0.8) pod_outline2d();
        yz(bar_in, cav_x1) offset(delta=-0.8) pod_outline2d();
    }
}
module temple_hinge_part() {      // NOT splayed: knuckle, wire cup, open-stop
    translate([0,0,-9]) cylinder(r=knuckle_r, h=tk_z[1]+9, $fn=fn_fine);
    cubeb([0.3, -(axis_y-brow_depth)+0.1, -9], [knuckle_r, 0, -6.8]);       // open stop (~1.5 deg past splay)
}
module pod_cuts(side) {
    // cavity
    yz(cav_x0, cav_x1+1) cavity_outline2d();
    // lid tab pocket under the front-wall lip
    cubeb([cav_x1-1.6, cav_y0-0.9, -5], [cav_x1-0.65, cav_y0+0.1, 5]);
    // wire entry from hinge groove (front wall, low, head side)
    cubeb([bar_in-0.1, pod_y0-0.1, -8.6], [cav_x0+1.8, cav_y0+0.1, -6.6]);
    // wire exit to earpiece groove (rear wall, head side)
    cubeb([bar_in-0.1, cav_y1-0.1, -2.0], [cav_x0+1.0, pod_y0+pod_len+0.1, 0.0]);
    // USB-C through rear wall
    ux = side>0 ? cav_x0+0.6+1.6+1.6 : cav_x0+5.1+1.0+1.6;                 // charger / XIAO
    translate([ux, cav_y1-1, 0]) rotate([-90,0,0]) linear_extrude(pod_endwall+2) rr2(3.9, 9.8, 1.6);
    if (side<0) {   // speaker grille through inner wall
        for (a=[0:60:300], r=[2.6, 5.0]) translate([bar_in-0.1, 74 + r*cos(a+ (r>3?30:0)), -2 + r*sin(a+(r>3?30:0))])
            rotate([0,90,0]) cylinder(d=1.3, h=pod_inwall+0.2, $fn=12);
        translate([bar_in-0.1, 74, -2]) rotate([0,90,0]) cylinder(d=1.3, h=pod_inwall+0.2, $fn=12);
    }
}
module pod_adds(side) {
    // centre rib (lid screw boss), wire notches top & bottom
    difference() {
        cubeb([cav_x0, rib_y0, -cav_h/2+2], [cav_x1-0.2, rib_y1, cav_h/2-2]);
        translate([cav_x1-0.2-insert_depth, (rib_y0+rib_y1)/2, 0]) rotate([0,90,0])
            cylinder(d=insert_hole_d, h=insert_depth+1, $fn=fn_fine);
    }
    if (side>0) {   // charger locating standoffs (board USB end at rear wall)
        bx = cav_y1 + pod_endwall - 3.2;    // board rear edge (USB-C flush with outer wall)
        for (h=chg_holes) translate([cav_x0, bx - h[0], h[1]-chg[1]/2]) rotate([0,90,0]) {
            cylinder(d=4.0, h=0.6, $fn=24); cylinder(d=2.1, h=1.8, $fn=16);
        }
    } else {        // amp end-fence + speaker ring
        cubeb([cav_x0, cav_y0+0.3+2*amp[0]+0.8, -8], [cav_x0+1.2, cav_y0+0.3+2*amp[0]+1.8, 8]);
        translate([cav_x0, 74, -2]) rotate([0,90,0]) difference() {
            cylinder(d=spk_d+2.4, h=1.4, $fn=48); translate([0,0,-1]) cylinder(d=spk_d+0.4, h=3, $fn=48);
        }
    }
}
module temple_wire_grooves() {
    // hinge cup chamber -> inner-face groove -> pod
    translate([0,0,-8.6]) cylinder(d=3.4, h=2.2, $fn=24);
    cubeb([bar_in-0.1, -0.5, -8.6], [bar_in+2.0, pod_y0+0.5, -6.6]);
    // pod rear -> earpiece groove to the bone transducer position (s = 20)
    yz(bar_in-0.1, bar_in+1.4) {
        hull() { translate([pod_y0+pod_len-1, -1]) circle(d=1.8, $fn=12); translate(ear_B+[0,-1]) circle(d=1.8, $fn=12); }
        hull() { translate(ear_B+[0,-1]) circle(d=1.8, $fn=12); translate(ear_pt(21)) circle(d=1.8, $fn=12); }
    }
}
module temple_local(side, splayed=true) {
    difference() {
        union() {
            rotate([0,0, splayed ? -splay : 0]) difference() {
                union() { temple_body(); pod_adds(side); }
                pod_cuts(side);
                temple_wire_grooves();
                translate([0,0,fk_z[0]-hinge_gap]) cylinder(r=knuckle_r+hinge_gap+0.2, h=20, $fn=fn_fine);
                translate([-10,-10,fk_z[0]-hinge_gap]) cube([20, 10, 20]);
            }
            temple_hinge_part();
        }
        translate([0,0,-8.6]) cylinder(d=3.4, h=2.2, $fn=24);                  // cup chamber (bottom closed)
        translate([0,0,tk_z[0]-0.1]) cylinder(d=tube_hole_glue, h=tk_z[1]-tk_z[0]+0.2, $fn=fn_fine);
        rotate([0,0, splayed ? -splay : 0]) cubeb([bar_in-0.1, -0.5, -8.6], [bar_in+2.0, 2, -6.6]);
    }
}

// ---------------- pod lid ----------------
module lip2d(g) { translate([(cav_y0+0.25 + cav_y1-1.25)/2, 0])
    rr2((cav_y1-1.25)-(cav_y0+0.25), cav_h-0.5, 1.75); }
module lid_local(side) {
    difference() {
        union() {
            hull() {
                yz(cav_x1, cav_x1+lid_t-0.6) pod_outline2d();
                yz(cav_x1, cav_x1+lid_t) offset(delta=-0.6) pod_outline2d();
            }
            yz(cav_x1-0.8, cav_x1+0.01) difference() {                       // locating lip (1 mm slide room at rear)
                lip2d(0); offset(delta=-1.0) lip2d(0);
            }
            cubeb([cav_x1-1.5, cav_y0-0.8, -4.6], [cav_x1-0.7, cav_y0+2.2, 4.6]);  // front tab
        }
        // screw (slotted 1.2 mm so the lid can slide its tab under the front lip)
        hull() for (dy=[-0.6,0.6]) translate([cav_x1-1, (rib_y0+rib_y1)/2+dy, 0]) rotate([0,90,0]) cylinder(d=m2_clear, h=5, $fn=24);
        hull() for (dy=[-0.6,0.6]) translate([cav_x1+lid_t-0.8, (rib_y0+rib_y1)/2+dy, 0]) rotate([0,90,0]) cylinder(d=m2_head_d, h=2, $fn=24);
        // vents over the warm board (charger on L, XIAO on R)
        for (i=[0:4]) translate([cav_x1-1, rib_y1+5+i*4.5, -6]) cube([4, 1.6, 12]);
        // mic port (right lid)
        if (side<0) translate([cav_x1-1, cav_y0+0.7+mic[0]/2, 0]) rotate([0,90,0]) cylinder(d=2.0, h=5, $fn=16);
        // side mark
        translate([cav_x1-0.5, cav_y0+40, -3]) rotate([90,0,90]) linear_extrude(1)
            text(side>0 ? "L" : "R", size=5, halign="center", valign="center");
    }
}

// ---------------- TPU ear grip (slides over earpiece; right holds the bone transducer) ----------------
module ear_frame() { translate([0, ear_B[0], ear_B[1]]) rotate([-ear_droop,0,0]) children(); }
module ear_grip_local(side) {
    cradle = (side<0) || bone_left;
    bx = bar_in + bar_t/2;
    difference() {
        union() {
            intersection() {
                hull() {
                    translate([bx, ear_pt(6)[0], ear_pt(6)[1]]) scale([1, 1.05, 1.05]) sphere(r=4.4, $fn=40);
                    translate([bx, ear_T[0], ear_T[1]]) sphere(r=3.9, $fn=40);
                }
                ear_frame() translate([-50, 6, -50]) cube(100);
            }
            if (cradle) ear_frame()                                           // transducer cradle, flat on the bed
                translate([-11.2, 6, -bone[1]/2-1.6]) cube([8.1, 20+bone[0]/2+1.6-6, bone[1]+3.2]);
        }
        earpiece_solid(-0.1);                                                 // interference bore
        ear_frame() translate([-50, -94, -50]) cube(100);                     // open entry
        if (cradle) ear_frame() {
            // open-face pocket, 0.1/side interference (TPU grips); transducer face stands 0.8 proud
            translate([-11.3, 20-(bone[0]-0.2)/2, -(bone[1]-0.2)/2]) cube([7.3, bone[0]-0.2, bone[1]-0.2]);
            translate([-6.3, 20, -1]) rotate([0,90,0]) cylinder(d=2.0, h=4, $fn=16);   // wire pass to bore
        }
    }
}

// ============================================================================
// HUD OPTICS — EXPERIMENTAL (assembly coordinates; screws to brow inserts)
// micro-OLED (slider, focus) -> Ø25 asphere -> 30R/70T combiner (pivot) -> eye
// ============================================================================
module optics_tower() {
    cy = comb_cy; cz = comb_cz;
    difference() {
        union() {
            translate([hud_cx-tower_out/2, cy-tower_out/2, 17.4]) cube([tower_out, tower_out, tower_top-17.4]);
            translate([hud_cx-18.6, cy-tower_out/2, 17.4]) cube([37.2, tower_out-3.8, 2.0]);    // fork flange
            for (s=[-1,1]) translate([hud_cx+s*17.8-0.8, cy-11, cz-11]) cube([1.6, 22, 19.4-(cz-11)]);
        }
        translate([hud_cx-tower_in/2, cy-tower_in/2, lens_top]) cube([tower_in, tower_in, 100]); // slider bore
        translate([hud_cx, cy, 18.4]) cylinder(d=lens_d+0.3, h=lens_ct+0.4+0.01, $fn=96);       // lens seat
        translate([hud_cx, cy, 10]) cylinder(d=lens_d-2, h=20, $fn=96);                         // aperture
        for (s=[-1,1]) translate([hud_cx+s*20, cy, cz]) rotate([0,90,0]) cylinder(d=m2_clear, h=10, center=true, $fn=20);
        for (dx=[-9,9]) {                                                                         // mount to brow
            translate([hud_cx+dx, -5, 27]) teardrop_y(m2_clear, 6);
            translate([hud_cx+dx, -9, 27]) teardrop_y(m2_head_d+0.4, 7.4);
        }
        // focus clamp slot (outer side wall)
        translate([hud_cx + hud_side*(tower_out/2), cy, 0]) hull() for (z=[lens_top+14.5, tower_top-3.5])
            translate([0,0,z]) rotate([0,90,0]) cylinder(d=m2_clear, h=6, center=true, $fn=20);
        // cable exit notch at top (front wall)
        translate([hud_cx-7, cy-tower_out/2-1, tower_top-6]) cube([14, 4, 7]);
    }
}
module display_slider_local() {   // origin = slider centre, bottom face z=0 (display face)
    s = tower_in - 0.4;
    difference() {
        translate([-s/2, -s/2, 0]) cube([s, s, 4]);
        translate([-(disp_mod[0]+0.3)/2, -(disp_mod[1]+0.3)/2, -0.01]) cube([disp_mod[0]+0.3, disp_mod[1]+0.3, disp_mod[2]+0.1]);
        translate([-6, -(disp_mod[1]+0.3)/2 - 3.2, -1]) cube([12, 2.6, 6]);  // flex cable slot
        translate([-6, -(disp_mod[1]+0.3)/2 - 1.0, disp_mod[2]]) cube([12, 1.2, 3]);
        translate([hud_side*(s/2), 0, 2]) rotate([0,90,0]) cylinder(d=m2_tap, h=12, center=true, $fn=16);
    }
}
module combiner_arm_local() {     // ring in XY, glass pocket on +z face, pivots on X
    od = comb_d + 4;
    difference() {
        union() {
            translate([0,0,-1.2]) cylinder(d=od, h=2.4, $fn=96);
            for (s=[-1,1]) translate([s>0 ? od/2-0.5 : -(od/2+2.3), -2.5, -1.2]) cube([2.8, 5, 4.5]);
        }
        translate([0,0,1.2-comb_t-0.1]) cylinder(d=comb_d+0.3, h=2, $fn=96);   // glass pocket
        translate([0,0,-2]) cylinder(d=comb_d-1.5, h=5, $fn=96);               // clear aperture
        for (s=[-1,1]) translate([s*(od/2+1.5), 0, 1.05]) rotate([0,90,0]) cylinder(d=m2_tap, h=4, center=true, $fn=16);
    }
}

// ============================================================================
// TOLERANCE COUPON — print first, tune tol/insert/tube values in config.scad
// ============================================================================
module tolerance_coupon() {
    difference() {
        cube([78, 30, 6]);
        for (i=[0:3]) translate([6+i*8, 7, 0.5]) cylinder(d=[3.0,3.1,3.2,3.3][i], h=6, $fn=48);
        for (i=[0:5]) translate([42+i*6, 7, -1]) cylinder(d=[4.0,4.05,4.1,4.2,4.35,4.5][i], h=8, $fn=64);
        for (i=[0:3]) translate([6+i*8, 18, 2]) cube([[1.7,1.8,1.9,2.0][i], 10, 5]);
        for (i=[0:3]) let(w=[6.0,6.2,6.4,6.6][i]) translate([46+i*8-w/2, 17-w/2+3, 2]) cube([w, w, 5]);
        translate([2, 0.6, 5.4]) linear_extrude(1) text("INS 3.0 3.1 3.2 3.3   TUBE 4.0 .05 .1 .2 .35 .5", size=1.9);
    }
}

// ============================================================================
// placement + print orientation
// ============================================================================
module place_temple(side) {
    translate([side*axis_x, axis_y, tz]) mirror([side<0?1:0,0,0]) children();
}
module place_body(side) {   // children in temple-body frame (splayed)
    place_temple(side) rotate([0,0,-splay]) children();
}
comb_c = [hud_cx, comb_cy, comb_cz];
slider_z = lens_top + lens_bfl;   // nominal display face height

module asm(p) {
    if (p=="frame") frame();
    if (p=="temple_left")  place_temple( 1) temple_local( 1);
    if (p=="temple_right") place_temple(-1) temple_local(-1);
    if (p=="lid_left")     place_body( 1) lid_local( 1);
    if (p=="lid_right")    place_body(-1) lid_local(-1);
    if (p=="ear_grip_left")  place_body( 1) ear_grip_local( 1);
    if (p=="ear_grip_right") place_body(-1) ear_grip_local(-1);
    if (p=="optics_tower")   optics_tower();
    if (p=="display_slider") translate([hud_cx, comb_cy, slider_z]) display_slider_local();
    if (p=="combiner_arm")   translate(comb_c) rotate([-comb_tilt,0,0]) combiner_arm_local();
}
module printed(p) {
    if (p=="frame") rotate([90,0,0]) frame();
    if (p=="temple_left")  rotate([0,-90,0]) temple_local( 1, false);
    if (p=="temple_right") rotate([0, 90,0]) mirror([1,0,0]) temple_local(-1, false);
    if (p=="lid_left")     rotate([0, 90,0]) lid_local( 1);
    if (p=="lid_right")    rotate([0,-90,0]) mirror([1,0,0]) lid_local(-1);
    if (p=="ear_grip_left")  rotate([145,0,0]) translate([0,-ear_B[0],-ear_B[1]]) ear_grip_local( 1);
    if (p=="ear_grip_right") rotate([145,0,0]) translate([0,-ear_B[0],-ear_B[1]]) mirror([1,0,0]) ear_grip_local(-1);
    if (p=="optics_tower")   rotate([180,0,0]) optics_tower();
    if (p=="display_slider") rotate([180,0,0]) display_slider_local();
    if (p=="combiner_arm")   combiner_arm_local();
    if (p=="tolerance_coupon") tolerance_coupon();
}
all_parts = ["frame","temple_left","temple_right","lid_left","lid_right","ear_grip_left",
             "ear_grip_right","optics_tower","display_slider","combiner_arm"];
module assembly(with_hud=true) {
    color("#2b2f36") asm("frame");
    color("#3a4049") { asm("temple_left"); asm("temple_right"); }
    color("#4a5260") { asm("lid_left"); asm("lid_right"); }
    color("#1d1f22") { asm("ear_grip_left"); asm("ear_grip_right"); }
    if (with_hud) {
        color("#202226") { asm("optics_tower"); asm("display_slider"); }
        color("#5a6578") asm("combiner_arm");
        color([0.6,0.85,1,0.35]) translate(comb_c) rotate([-comb_tilt,0,0]) translate([0,0,0.1]) cylinder(d=comb_d, h=comb_t, $fn=64);
    }
}

echo(str("DERIVED: half_w=", half_w, " axis=[", axis_x, ",", axis_y, "] splay=", splay, " deg"));
which = "frame";
if (part=="assembly") assembly();
else if (part=="assembly_core") assembly(false);
else if (part=="asm") asm(which);
else printed(part);
