import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { STLLoader } from 'three/addons/loaders/STLLoader.js';

// ---------- part catalogue (assembly coords: +X wearer-left, +Y toward head, +Z up) ----------
const PARTS = [
  { id: 'frame',          name: 'Slim frame',          visor: false, color: 0x30353d, ex: [0, 0, 0],       status: 'PROTOTYPE-READY', what: 'Rims, nose-pad lands, hollow-pin temple hinges, visor hinge knuckles on the brow, hall-sensor magnet.' },
  { id: 'temple_left',    name: 'Temple L',            visor: false, color: 0x434b57, ex: [30, 30, 0],     status: 'PROTOTYPE-READY', what: 'Slim arm. The earpiece holds a 5 × 10 × 40 mm cell (counterweight).' },
  { id: 'temple_right',   name: 'Temple R',            visor: false, color: 0x434b57, ex: [-30, 30, 0],    status: 'PROTOTYPE-READY', what: 'Slim arm. The earpiece holds the second cell.' },
  { id: 'ear_grip_left',  name: 'Ear grip L (TPU)',    visor: false, color: 0x1b1d20, ex: [30, 60, -30],   status: 'PROTOTYPE-READY', what: 'TPU sleeve that also closes the battery bay.' },
  { id: 'ear_grip_right', name: 'Ear grip R (TPU)',    visor: false, color: 0x1b1d20, ex: [-30, 60, -30],  status: 'PROTOTYPE-READY', what: 'TPU sleeve that also closes the battery bay.' },
  { id: 'visor_shell',    name: 'Visor shell',         visor: true,  color: 0x2a2e35, ex: [0, -75, 18],    status: 'PROTOTYPE-READY', what: 'Two pods (design screens outside, eyepieces inside), centre camera, CAMERA LIVE LED, crest controls, cable entry.' },
  { id: 'visor_back',     name: 'Visor back plate',    visor: true,  color: 0x4a5260, ex: [0, -38, 18],    status: 'EXPERIMENTAL',    what: 'Eyepiece sleeves (set by IPD), driver-board rail, 4 × M2 screws.' },
];
const VIS = { axisY: 3.3, axisZ: 27.5, upDeg: 100, vf: -36, pod: 34.5, podZ: 2, lcd: [32.63, 27.97] };  // mirrors config.scad

// ---------- repo links (works on <user>.github.io/<repo>/) ----------
const host = location.hostname, seg = location.pathname.split('/').filter(Boolean);
const gh = host.endsWith('github.io') ? { user: host.split('.')[0], repo: seg[0] || '' } : null;
const repoURL = gh && gh.repo ? `https://github.com/${gh.user}/${gh.repo}` : null;
const $ = (s, r = document) => r.querySelector(s);
if (repoURL) {
  $('#repoLink').href = repoURL; $('#zipLink').href = `${repoURL}/archive/refs/heads/main.zip`;
  document.querySelectorAll('a.doc').forEach(a => a.href = `${repoURL}/blob/main/${a.dataset.doc}`);
} else { $('#repoLink').hidden = true; $('#zipLink').hidden = true; }

// ---------- scene ----------
const canvas = $('#view');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(35, 1, 1, 5000); camera.up.set(0, 0, 1);
const controls = new OrbitControls(camera, canvas); controls.enableDamping = true;
scene.add(new THREE.HemisphereLight(0xdfe8ff, 0x20242a, 1.6));
const key = new THREE.DirectionalLight(0xffffff, 2.2); key.position.set(-150, -260, 220); scene.add(key);
const rim = new THREE.DirectionalLight(0xffd2c8, 0.9); rim.position.set(200, 250, 120); scene.add(rim);
const grid = new THREE.GridHelper(400, 40, 0x3a414b, 0x262b32); grid.rotation.x = Math.PI / 2; grid.position.set(0, 40, -45);
grid.material.transparent = true; grid.material.opacity = 0.5; scene.add(grid);
function resize() { const r = canvas.parentElement.getBoundingClientRect(); renderer.setSize(r.width, r.height, false); camera.aspect = r.width / r.height; camera.updateProjectionMatrix(); }
new ResizeObserver(resize).observe(canvas.parentElement);
const TARGET = [0, 30, 5];
const VIEWS = { iso: [-230, -260, 170], front: [0, -380, 15], top: [0, 30, 420], side: [-400, 30, 25] };
function setView(v) {
  const p = VIEWS[v]; camera.position.set(...p); controls.target.set(...TARGET); controls.update();
  document.querySelectorAll('.seg button').forEach(b => b.classList.toggle('on', b.dataset.view === v));
}
setView('iso'); document.querySelectorAll('.seg button').forEach(b => b.onclick = () => setView(b.dataset.view));

// visor pivot: a group whose origin is the hinge axis, so "Visor up" is one rotation
const visorPivot = new THREE.Group(); visorPivot.position.set(0, VIS.axisY, VIS.axisZ); scene.add(visorPivot);
const visorInner = new THREE.Group(); visorInner.position.set(0, -VIS.axisY, -VIS.axisZ); visorPivot.add(visorInner);

// ---------- animated design screens (same designs as the firmware) ----------
const scr = [0, 1].map(eye => {
  const c = document.createElement('canvas'); c.width = 280; c.height = 240;
  const tex = new THREE.CanvasTexture(c); tex.colorSpace = THREE.SRGBColorSpace;
  const m = new THREE.Mesh(new THREE.PlaneGeometry(VIS.lcd[0], VIS.lcd[1]), new THREE.MeshBasicMaterial({ map: tex }));
  m.rotation.x = Math.PI / 2;                                                          // face forward (-Y)
  m.position.set((eye === 0 ? 1 : -1) * VIS.pod, VIS.vf - 0.15, VIS.podZ);
  visorInner.add(m); return { c, ctx: c.getContext('2d'), tex, eye };
});
let design = 0, designText = 'HELLO WORLD', look = [0, 0], lookT = [0, 0], nextLook = 0, nextBlink = 2;
function drawDesign(s, t) {
  const g = s.ctx, W = 280, H = 240; g.fillStyle = '#000'; g.fillRect(0, 0, W, H);
  if (design === 0) {
    const bp = t - nextBlink, blink = bp > 0 && bp < 0.18 ? Math.sin(bp / 0.18 * Math.PI) : 0;
    g.save(); g.beginPath(); g.ellipse(W / 2, H / 2, 118, Math.max(2, 70 * (1 - blink)), 0, 0, 7); g.clip();
    g.fillStyle = '#eceef2'; g.fillRect(0, 0, W, H);
    const ix = W / 2 + look[0] * 38, iy = H / 2 + look[1] * 22;
    const gr = g.createRadialGradient(ix, iy, 10, ix, iy, 46); gr.addColorStop(0, '#1c8fb0'); gr.addColorStop(1, '#3fd0f0');
    g.fillStyle = gr; g.beginPath(); g.arc(ix, iy, 46, 0, 7); g.fill();
    g.fillStyle = '#05070a'; g.beginPath(); g.arc(ix, iy, 17, 0, 7); g.fill();
    g.fillStyle = '#fff'; g.beginPath(); g.arc(ix - 6, iy - 7, 5, 0, 7); g.fill(); g.restore();
  } else if (design === 1) {
    for (let r = 160; r > 0; r -= 6) { const v = 0.5 + 0.5 * Math.sin(r * 0.12 - t * 5); g.fillStyle = `hsl(${200 + r * 0.6},90%,${v * 50}%)`; g.beginPath(); g.arc(W / 2, H / 2, r, 0, 7); g.fill(); }
  } else if (design === 2) {
    for (let x = 0; x < W; x += 4) { g.fillStyle = `hsl(${(x + s.eye * W) * 0.8 + t * 90},85%,55%)`; g.fillRect(x, 0, 4, H); }
  } else if (design === 3) {
    g.font = 'bold 40px ui-monospace,monospace'; g.textBaseline = 'middle'; g.fillStyle = `hsl(${t * 40},70%,60%)`;
    const total = designText.length * 24 + 2 * W, sx = (t * 120) % total - W - s.eye * W;
    g.fillText(designText, -sx, H / 2);
  }
  s.tex.needsUpdate = true;
}

// ---------- load meshes ----------
const meshes = {}, loader = new STLLoader(); let loaded = 0;
PARTS.forEach(p => loader.load(`models/${p.id}.stl`, geo => {
  geo.computeVertexNormals();
  const m = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({ color: p.color, roughness: 0.6, metalness: 0.08, flatShading: true }));
  m.userData.part = p; meshes[p.id] = m; (p.visor ? visorInner : scene).add(m);
  if (++loaded === PARTS.length) { $('#loading').hidden = true; applyPose(); }
}, undefined, () => { $('#loading').textContent = 'Could not load models/ — run ./tools/build.sh'; }));

function applyPose() {
  const k = +$('#explode').value;
  PARTS.forEach(p => { const m = meshes[p.id]; if (m) m.position.set(p.ex[0] * k, p.ex[1] * k, p.ex[2] * k); });
  visorPivot.rotation.x = $('#visorUp').checked ? -THREE.MathUtils.degToRad(VIS.upDeg) : 0;
  const shell = PARTS.find(p => p.id === 'visor_shell').ex;
  visorInner.children.filter(o => o.isMesh && !o.userData.part).forEach(o => { o.position.y = VIS.vf - 0.15 + shell[1] * k; o.position.z = VIS.podZ + shell[2] * k; });
}
$('#explode').oninput = applyPose; $('#visorUp').onchange = applyPose;
$('#designPick').onchange = e => { design = +e.target.value; sendBle('design', design); };

// ---------- picking ----------
const ray = new THREE.Raycaster(), ptr = new THREE.Vector2(); let selected = null, downAt = null;
canvas.addEventListener('pointerdown', e => downAt = [e.clientX, e.clientY]);
canvas.addEventListener('pointerup', e => {
  if (!downAt || Math.hypot(e.clientX - downAt[0], e.clientY - downAt[1]) > 4) return;
  const r = canvas.getBoundingClientRect(); ptr.set(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1);
  ray.setFromCamera(ptr, camera); const hit = ray.intersectObjects(Object.values(meshes).filter(m => m.visible))[0];
  select(hit ? hit.object.userData.part.id : null);
});
function select(id) {
  selected = id;
  Object.values(meshes).forEach(m => m.material.emissive.setHex(m.userData.part.id === id ? 0x5a1a12 : 0));
  document.querySelectorAll('#partList li').forEach(li => li.classList.toggle('sel', li.dataset.id === id));
  const box = $('#pick'); if (!id) { box.hidden = true; return; }
  const p = PARTS.find(q => q.id === id), s = stats[id] || {}, mf = manifest[id] || {};
  box.innerHTML = `<h4>${p.name} <span class="chip ${p.status === 'EXPERIMENTAL' ? 'exp' : 'ok'}">${p.status}</span></h4><p>${p.what}</p>
    <p>${mf.material || s.material || ''} · ${(s.bbox_mm || []).join(' × ')} mm · ${s.solid_mass_g ?? '–'} g solid</p><p>Print: ${mf.orientation || '–'}</p>`;
  box.hidden = false;
}

// ---------- data ----------
let stats = {}, manifest = {};
const csv = t => { const rows = []; let row = [], f = '', q = false;
  for (let i = 0; i < t.length; i++) { const c = t[i];
    if (q) { if (c === '"' && t[i + 1] === '"') { f += '"'; i++; } else if (c === '"') q = false; else f += c; }
    else if (c === '"') q = true; else if (c === ',') { row.push(f); f = ''; } else if (c === '\n') { row.push(f); rows.push(row); row = []; f = ''; } else if (c !== '\r') f += c; }
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
    const s = stats[p.id] || {}, li = document.createElement('li'); li.dataset.id = p.id;
    li.innerHTML = `<span class="sw" style="background:#${p.color.toString(16).padStart(6, '0')}"></span><span class="nm">${p.name}</span>
      <span class="dl"><a href="cad/stl/${p.id}.stl" download>STL</a><a href="cad/3mf/${p.id}.3mf" download>3MF</a><input type="checkbox" checked aria-label="show ${p.name}"></span>
      <span class="meta"><span class="chip ${p.status === 'EXPERIMENTAL' ? 'exp' : 'ok'}">${p.status}</span> ${esc((manifest[p.id] || {}).material || s.material || '')} · ${s.solid_mass_g ?? '–'} g</span>`;
    const cb = li.querySelector('input'); cb.onchange = e => { if (meshes[p.id]) meshes[p.id].visible = e.target.checked; }; cb.onclick = e => e.stopPropagation();
    li.querySelectorAll('a').forEach(a => a.onclick = e => e.stopPropagation()); li.onclick = () => select(selected === p.id ? null : p.id);
    ul.appendChild(li);
  });
}
function renderBom(rows) {
  const sum = t => rows.filter(r => r.tier === t).reduce((a, r) => a + (+r.qty) * (+r.approx_unit_usd), 0);
  const g = sum('GLASSES'), b = sum('BRICK');
  $('#bomTotals').innerHTML = `<div><b>$${g.toFixed(0)}</b><span>Glasses</span></div><div><b>$${b.toFixed(0)}</b><span>Pocket brick</span></div><div><b>$${(g + b).toFixed(0)}</b><span>Total</span></div>`;
  $('#bomTable').innerHTML = ['GLASSES', 'BRICK', 'OPTION'].map(t => `<div class="bom-tier">${t}</div>` + rows.filter(r => r.tier === t).map(r => `
    <div class="bom-row"><div class="top"><b>${r.source_url ? `<a href="${esc(r.source_url)}" target="_blank" rel="noopener">${esc(r.item)}</a>` : esc(r.item)}</b>
    <span class="px">${r.qty} × $${(+r.approx_unit_usd).toFixed(2)}</span></div><p>${esc(r.part_or_example)} · <span class="chip ${r.status === 'EXPERIMENTAL' ? 'exp' : 'ok'}">${esc(r.status)}</span></p></div>`).join('')).join('');
}

// ---------- tabs ----------
document.querySelectorAll('.tabs button').forEach(b => b.onclick = () => {
  document.querySelectorAll('.tabs button').forEach(x => x.classList.toggle('on', x === b));
  document.querySelectorAll('.tab').forEach(t => t.hidden = t.id !== `tab-${b.dataset.tab}`);
});

// ---------- Web Bluetooth phone control (firmware/glasses_mcu/main/ble.c) ----------
const U = n => `7a1e00${n}-5c3b-4c55-9b1d-a5e0a5e0a5e0`;
const SVC = U('00'), CH = { design: U('01'), brightness: U('02'), text: U('03'), ar: U('04'), status: U('05') };
let chars = null;
async function connect() {
  if (!navigator.bluetooth) { $('#bleStatus').textContent = 'This browser has no Web Bluetooth. Use Chrome on Android or desktop.'; return; }
  try {
    const dev = await navigator.bluetooth.requestDevice({ filters: [{ name: 'ASG-Glasses' }], optionalServices: [SVC] });
    dev.addEventListener('gattserverdisconnected', () => { chars = null; $('#bleStatus').textContent = 'Disconnected'; $('#bleBtn').textContent = 'Connect to ASG-Glasses'; });
    const srv = await (await dev.gatt.connect()).getPrimaryService(SVC);
    chars = {}; for (const [k, u] of Object.entries(CH)) chars[k] = await srv.getCharacteristic(u);
    chars.status.addEventListener('characteristicvaluechanged', e => showStatus(e.target.value));
    await chars.status.startNotifications(); showStatus(await chars.status.readValue());
    $('#bleBtn').textContent = 'Connected ✓';
  } catch (err) { $('#bleStatus').textContent = 'Connection failed: ' + err.message; }
}
function showStatus(v) {
  const mv = v.getUint16(0, true), up = v.getUint8(2), d = v.getUint8(3), ar = v.getUint8(4), wifi = v.getUint8(5), roll = v.getInt16(6, true) / 10;
  $('#bleStatus').innerHTML = `Battery <b>${(mv / 1000).toFixed(2)} V</b> · visor <b>${up ? 'UP' : 'DOWN'}</b> · brick link <b>${wifi ? 'OK' : 'off'}</b> · roll ${roll.toFixed(0)}°`;
  design = d; $('#designPick').value = String(d);
  document.querySelectorAll('#arBtns button').forEach(b => b.classList.toggle('on', +b.dataset.a === ar));
}
async function sendBle(k, v) {
  if (!chars) return;
  try { await chars[k].writeValue(typeof v === 'string' ? new TextEncoder().encode(v) : Uint8Array.of(v)); } catch (e) { console.warn(e); }
}
$('#bleBtn').onclick = connect;
document.querySelectorAll('#designBtns button').forEach(b => b.onclick = () => { design = +b.dataset.d; $('#designPick').value = b.dataset.d; sendBle('design', design); });
document.querySelectorAll('#arBtns button').forEach(b => b.onclick = () => { sendBle('ar', +b.dataset.a); document.querySelectorAll('#arBtns button').forEach(x => x.classList.toggle('on', x === b)); });
$('#bright').oninput = e => sendBle('brightness', +e.target.value);
$('#textForm').onsubmit = e => { e.preventDefault(); designText = ($('#textIn').value || 'HELLO').toUpperCase(); design = 3; $('#designPick').value = '3'; sendBle('text', designText); };

// ---------- PWA ----------
let deferred = null;
addEventListener('beforeinstallprompt', e => { e.preventDefault(); deferred = e; $('#installBtn').hidden = false; });
$('#installBtn').onclick = async () => { if (!deferred) return; deferred.prompt(); await deferred.userChoice; deferred = null; $('#installBtn').hidden = true; };
if ('serviceWorker' in navigator && location.protocol !== 'file:') navigator.serviceWorker.register('sw.js').catch(() => {});

// ---------- loop ----------
(function loop() {
  requestAnimationFrame(loop);
  const t = performance.now() / 1000;
  if (t > nextLook) { lookT = [Math.random() * 2 - 1, Math.random() * 1.2 - 0.6]; nextLook = t + 0.6 + Math.random() * 1.8; }
  look = look.map((v, i) => v + (lookT[i] - v) * 0.2);
  if (t - nextBlink > 0.18) nextBlink = t + 2.5 + Math.random() * 3;
  scr.forEach(s => drawDesign(s, t));
  controls.update(); renderer.render(scene, camera);
})();

// ---------- hooks for tools/renders.py ----------
window.__ready = () => loaded === PARTS.length;
window.__project = pts => { const r = canvas.getBoundingClientRect(); return pts.map(p => { const v = new THREE.Vector3(...p).project(camera); return [(v.x + 1) / 2 * r.width, (1 - v.y) / 2 * r.height]; }); };
window.__partCenters = () => (scene.updateMatrixWorld(true), Object.fromEntries(Object.entries(meshes).filter(([, m]) => m.visible).map(([k, m]) => { const c = new THREE.Box3().setFromObject(m).getCenter(new THREE.Vector3()); return [k, [c.x, c.y, c.z]]; })));
window.__setView = (v, k = 0, up = false, pos = null, d = 0) => {
  setView(v); if (pos) { camera.position.set(...pos); controls.update(); }
  document.querySelector('.hud-tools').style.visibility = 'hidden';
  $('#explode').value = k; $('#visorUp').checked = !!up; design = d; applyPose();
};
window.__ghost = on => Object.values(meshes).forEach(m => { m.material.transparent = on; m.material.opacity = on ? 0.4 : 1; m.material.depthWrite = !on; });
