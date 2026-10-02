import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { STLLoader } from 'three/addons/loaders/STLLoader.js';

// ---------- part catalogue (assembly coords: +X wearer-left, +Y back, +Z up) ----------
const PARTS = [
  { id: 'frame',          name: 'Front frame',         group: 'core', color: 0x30353d, ex: [0, 0, 0],      status: 'PROTOTYPE-READY', what: 'ToF bridge pocket, BME280 vented brow, PTT flexure + privacy LED (right), main switch (left), harness groove, hollow-pin hinge knuckles.' },
  { id: 'temple_left',    name: 'Temple L (power)',    group: 'core', color: 0x434b57, ex: [30, 25, 0],    status: 'PROTOTYPE-READY', what: 'Battery bay + bq25185/5 V boost board on locating pins, USB-C out the rear.' },
  { id: 'temple_right',   name: 'Temple R (compute)',  group: 'core', color: 0x434b57, ex: [-30, 25, 0],   status: 'PROTOTYPE-READY', what: 'XIAO ESP32-S3, IMU, mic, 2× MAX98357A, speaker grille; USB-C out the rear.' },
  { id: 'lid_left',       name: 'Lid L',               group: 'core', color: 0x5d6675, ex: [60, 25, 0],    status: 'PROTOTYPE-READY', what: 'Front hook + 1× M2×5 into heat-set insert; vents over charger.' },
  { id: 'lid_right',      name: 'Lid R',               group: 'core', color: 0x5d6675, ex: [-60, 25, 0],   status: 'PROTOTYPE-READY', what: 'Front hook + 1× M2×5; vents over XIAO; 2 mm mic port.' },
  { id: 'ear_grip_left',  name: 'Ear grip L (TPU)',    group: 'core', color: 0x1b1d20, ex: [25, 50, -25],  status: 'PROTOTYPE-READY', what: 'TPU 95A interference sleeve.' },
  { id: 'ear_grip_right', name: 'Ear grip R (TPU)',    group: 'core', color: 0x1b1d20, ex: [-25, 50, -25], status: 'PROTOTYPE-READY', what: 'TPU sleeve + compliant bone-transducer cradle over the mastoid.' },
  { id: 'optics_tower',   name: 'HUD optics tower',    group: 'hud',  color: 0x1e2024, ex: [0, -45, 30],   status: 'EXPERIMENTAL', what: 'Ø25 f25 asphere seat, focus slot, combiner fork; 2× M2 to brow inserts.' },
  { id: 'display_slider', name: 'Display slider',      group: 'hud',  color: 0x2a2d33, ex: [0, -45, 75],   status: 'EXPERIMENTAL', what: 'Holds the 0.23″ micro-OLED face-down; ±6 mm focus travel.' },
  { id: 'combiner_arm',   name: 'Combiner arm',        group: 'hud',  color: 0x6b778a, ex: [0, -75, -5],   status: 'EXPERIMENTAL', what: 'Holds the 30R/70T Ø25 glass; pivots 35–50°.' },
];
const COMB = { c: [-31.5, -14.8, 6.0], tilt: 45, d: 25 };   // mirrors config.scad

// ---------- repo links (works on <user>.github.io/<repo>/) ----------
const host = location.hostname, seg = location.pathname.split('/').filter(Boolean);
const gh = host.endsWith('github.io') ? { user: host.split('.')[0], repo: seg[0] || '' } : null;
const repoURL = gh && gh.repo ? `https://github.com/${gh.user}/${gh.repo}` : null;
const $ = (s, r = document) => r.querySelector(s);
if (repoURL) {
  $('#repoLink').href = repoURL;
  $('#zipLink').href = `${repoURL}/archive/refs/heads/main.zip`;
  document.querySelectorAll('a.doc').forEach(a => a.href = `${repoURL}/blob/main/${a.dataset.doc}`);
} else { $('#repoLink').hidden = true; $('#zipLink').hidden = true; }

// ---------- scene ----------
const canvas = $('#view');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(35, 1, 1, 5000);
camera.up.set(0, 0, 1);
const controls = new OrbitControls(camera, canvas);
controls.enableDamping = true; controls.target.set(0, 45, 5);
scene.add(new THREE.HemisphereLight(0xdfe8ff, 0x20242a, 1.6));
const key = new THREE.DirectionalLight(0xffffff, 2.2); key.position.set(-150, -220, 260); scene.add(key);
const rim = new THREE.DirectionalLight(0xffd2c8, 0.9); rim.position.set(200, 250, 120); scene.add(rim);
const grid = new THREE.GridHelper(400, 40, 0x3a414b, 0x262b32); grid.rotation.x = Math.PI / 2; grid.position.set(0, 50, -45);
grid.material.transparent = true; grid.material.opacity = 0.5; scene.add(grid);

function resize() {
  const r = canvas.parentElement.getBoundingClientRect();
  renderer.setSize(r.width, r.height, false); camera.aspect = r.width / r.height; camera.updateProjectionMatrix();
}
new ResizeObserver(resize).observe(canvas.parentElement);

const VIEWS = { iso: [-300, -250, 190], front: [0, -420, 20], top: [0, 45, 470], side: [-430, 45, 30] };
function setView(v) {
  const p = VIEWS[v]; camera.position.set(p[0], p[1], p[2]); controls.target.set(0, 45, 5); controls.update();
  document.querySelectorAll('.seg button').forEach(b => b.classList.toggle('on', b.dataset.view === v));
}
setView('iso');
document.querySelectorAll('.seg button').forEach(b => b.onclick = () => setView(b.dataset.view));

// ---------- load meshes ----------
const meshes = {}, loader = new STLLoader();
let loaded = 0;
const glass = new THREE.Mesh(new THREE.CylinderGeometry(COMB.d / 2, COMB.d / 2, 1, 64),
  new THREE.MeshPhysicalMaterial({ color: 0x9fdcff, transparent: true, opacity: 0.35, roughness: 0.05, metalness: 0.1 }));
glass.rotation.x = Math.PI / 2 - THREE.MathUtils.degToRad(COMB.tilt);
glass.position.set(...COMB.c); glass.userData.base = glass.position.clone(); scene.add(glass);

PARTS.forEach(p => {
  loader.load(`models/${p.id}.stl`, geo => {
    geo.computeVertexNormals();
    const m = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({ color: p.color, roughness: 0.62, metalness: 0.08, flatShading: true }));
    m.userData.part = p; meshes[p.id] = m; scene.add(m);
    if (++loaded === PARTS.length) { $('#loading').hidden = true; applyExplode(); }
  }, undefined, () => { $('#loading').textContent = 'Could not load models/ — run ./tools/build.sh'; });
});

function applyExplode() {
  const k = +$('#explode').value;
  PARTS.forEach(p => { const m = meshes[p.id]; if (m) m.position.set(p.ex[0] * k, p.ex[1] * k, p.ex[2] * k); });
  const a = PARTS.find(p => p.id === 'combiner_arm').ex;
  glass.position.set(COMB.c[0] + a[0] * k, COMB.c[1] + a[1] * k, COMB.c[2] + a[2] * k);
}
$('#explode').oninput = applyExplode;
$('#showHud').onchange = e => {
  PARTS.filter(p => p.group === 'hud').forEach(p => { if (meshes[p.id]) meshes[p.id].visible = e.target.checked; syncChecks(); });
  glass.visible = e.target.checked;
};

// ---------- picking ----------
const ray = new THREE.Raycaster(), ptr = new THREE.Vector2();
let selected = null, downAt = null;
canvas.addEventListener('pointerdown', e => downAt = [e.clientX, e.clientY]);
canvas.addEventListener('pointerup', e => {
  if (!downAt || Math.hypot(e.clientX - downAt[0], e.clientY - downAt[1]) > 4) return;
  const r = canvas.getBoundingClientRect();
  ptr.set(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1);
  ray.setFromCamera(ptr, camera);
  const hit = ray.intersectObjects(Object.values(meshes).filter(m => m.visible))[0];
  select(hit ? hit.object.userData.part.id : null);
});
function select(id) {
  selected = id;
  Object.values(meshes).forEach(m => m.material.emissive.setHex(m.userData.part.id === id ? 0x5a1a12 : 0x000000));
  document.querySelectorAll('#partList li').forEach(li => li.classList.toggle('sel', li.dataset.id === id));
  const box = $('#pick');
  if (!id) { box.hidden = true; return; }
  const p = PARTS.find(q => q.id === id), s = stats[id] || {}, mf = manifest[id] || {};
  box.innerHTML = `<h4>${p.name} <span class="chip ${p.status === 'EXPERIMENTAL' ? 'exp' : 'ok'}">${p.status}</span></h4>
    <p>${p.what}</p>
    <p>${mf.material || s.material || ''} · ${(s.bbox_mm || []).join(' × ')} mm · ${s.solid_mass_g ?? '–'} g solid</p>
    <p>Print: ${mf.orientation || '–'} · supports: ${mf.supports || '–'}</p>`;
  box.hidden = false;
}

// ---------- data: stats, manifest, BOM ----------
let stats = {}, manifest = {};
const csv = t => { const rows = []; let row = [], f = '', q = false;
  for (let i = 0; i < t.length; i++) { const c = t[i];
    if (q) { if (c === '"' && t[i + 1] === '"') { f += '"'; i++; } else if (c === '"') q = false; else f += c; }
    else if (c === '"') q = true; else if (c === ',') { row.push(f); f = ''; }
    else if (c === '\n') { row.push(f); rows.push(row); row = []; f = ''; } else if (c !== '\r') f += c; }
  if (f || row.length) { row.push(f); rows.push(row); }
  const h = rows.shift(); return rows.filter(r => r.length > 1).map(r => Object.fromEntries(h.map((k, i) => [k, r[i] ?? ''])));
};
const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

Promise.all([
  fetch('cad/part_stats.json').then(r => r.json()).catch(() => ({})),
  fetch('cad/print_manifest.csv').then(r => r.text()).then(csv).catch(() => []),
  fetch('bom.csv').then(r => r.text()).then(csv).catch(() => []),
]).then(([s, m, bom]) => { stats = s; m.forEach(r => manifest[r.part] = r); renderParts(); renderBom(bom); });

function renderParts() {
  const ul = $('#partList'); ul.innerHTML = '';
  PARTS.forEach(p => {
    const s = stats[p.id] || {}, li = document.createElement('li');
    li.dataset.id = p.id;
    li.innerHTML = `<span class="sw" style="background:#${p.color.toString(16).padStart(6, '0')}"></span>
      <span class="nm">${p.name}</span>
      <span class="dl"><a href="cad/stl/${p.id}.stl" download>STL</a><a href="cad/3mf/${p.id}.3mf" download>3MF</a>
      <input type="checkbox" checked aria-label="show ${p.name}"></span>
      <span class="meta"><span class="chip ${p.status === 'EXPERIMENTAL' ? 'exp' : 'ok'}">${p.status}</span>
      ${esc((manifest[p.id] || {}).material || s.material || '')} · ${s.solid_mass_g ?? '–'} g · ${esc((manifest[p.id] || {}).orientation || '')}</span>`;
    li.querySelector('input').onchange = e => { if (meshes[p.id]) meshes[p.id].visible = e.target.checked; if (p.id === 'combiner_arm') glass.visible = e.target.checked; };
    li.querySelector('input').onclick = e => e.stopPropagation();
    li.querySelectorAll('a').forEach(a => a.onclick = e => e.stopPropagation());
    li.onclick = () => select(selected === p.id ? null : p.id);
    ul.appendChild(li);
  });
}
function syncChecks() {
  document.querySelectorAll('#partList li').forEach(li => { const m = meshes[li.dataset.id]; if (m) li.querySelector('input').checked = m.visible; });
}
function renderBom(rows) {
  const tiers = ['CORE', 'HUD', 'MEDIA'], sum = t => rows.filter(r => r.tier === t).reduce((a, r) => a + (+r.qty) * (+r.approx_unit_usd), 0);
  const c = sum('CORE'), h = sum('HUD'), m = sum('MEDIA');
  $('#bomTotals').innerHTML = `<div><b>$${c.toFixed(0)}</b><span>Core</span></div><div><b>$${(c + h).toFixed(0)}</b><span>+ HUD (exp.)</span></div><div><b>$${(c + h + m).toFixed(0)}</b><span>+ Media</span></div>`;
  $('#bomTable').innerHTML = tiers.map(t => `<div class="bom-tier">${t}</div>` + rows.filter(r => r.tier === t).map(r => `
    <div class="bom-row"><div class="top"><b>${r.source_url ? `<a href="${esc(r.source_url)}" target="_blank" rel="noopener">${esc(r.item)}</a>` : esc(r.item)}</b>
    <span class="px">${r.qty} × $${(+r.approx_unit_usd).toFixed(2)}</span></div>
    <p>${esc(r.part_or_example)}${r.change_vs_brief && r.change_vs_brief !== 'kept' ? ` · <span class="chg">${esc(r.change_vs_brief)}</span>` : ''}</p></div>`).join('')).join('');
}

// ---------- tabs ----------
document.querySelectorAll('.tabs button').forEach(b => b.onclick = () => {
  document.querySelectorAll('.tabs button').forEach(x => x.classList.toggle('on', x === b));
  document.querySelectorAll('.tab').forEach(t => t.hidden = t.id !== `tab-${b.dataset.tab}`);
});

// ---------- PWA (installable, works offline) ----------
let deferred = null;
addEventListener('beforeinstallprompt', e => { e.preventDefault(); deferred = e; $('#installBtn').hidden = false; });
$('#installBtn').onclick = async () => { if (!deferred) return; deferred.prompt(); await deferred.userChoice; deferred = null; $('#installBtn').hidden = true; };
if ('serviceWorker' in navigator && location.protocol !== 'file:') navigator.serviceWorker.register('sw.js').catch(() => {});

(function loop() { requestAnimationFrame(loop); controls.update(); renderer.render(scene, camera); })();
window.__ready = () => loaded === PARTS.length;

// ---------- helpers used by tools/renders.py (README images) ----------
window.__project = pts => {
  const r = canvas.getBoundingClientRect();
  return pts.map(p => { const v = new THREE.Vector3(...p).project(camera); return [(v.x + 1) / 2 * r.width, (1 - v.y) / 2 * r.height]; });
};
window.__partCenters = () => Object.fromEntries(Object.entries(meshes).filter(([, m]) => m.visible).map(([k, m]) => {
  const b = new THREE.Box3().setFromObject(m), c = b.getCenter(new THREE.Vector3()); return [k, [c.x, c.y, c.z]];
}));
window.__setView = (v, k = 0, hud = true, pos = null) => {
  setView(v); if (pos) { camera.position.set(...pos); controls.update(); }
  document.querySelector('.hud-tools').style.visibility = 'hidden'; $('#explode').value = k; applyExplode();
  $('#showHud').checked = hud; $('#showHud').dispatchEvent(new Event('change'));
};
window.__ghost = on => Object.values(meshes).forEach(m => { m.material.transparent = on; m.material.opacity = on ? 0.45 : 1; m.material.depthWrite = !on; });
