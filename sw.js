// Offline cache for the installable viewer app. Bump VERSION after rebuilding models.
const VERSION = 'asg-v2';
const CORE = ['./', 'index.html', 'style.css', 'app.js', 'manifest.webmanifest', 'icons/icon.svg',
  'icons/icon-192.png', 'icons/icon-512.png', 'vendor/three/three.module.min.js',
  'vendor/three/addons/controls/OrbitControls.js', 'vendor/three/addons/loaders/STLLoader.js',
  'bom.csv', 'docs/img/wiring_power.svg', 'docs/img/wiring_signals.svg', 'docs/img/hinge.svg', 'cad/part_stats.json', 'cad/print_manifest.csv',
  ...['frame','temple_left','temple_right','lid_left','lid_right','ear_grip_left','ear_grip_right',
      'optics_tower','display_slider','combiner_arm'].map(p => `models/${p}.stl`)];
self.addEventListener('install', e => e.waitUntil(caches.open(VERSION).then(c => c.addAll(CORE)).then(() => self.skipWaiting())));
self.addEventListener('activate', e => e.waitUntil(caches.keys().then(ks =>
  Promise.all(ks.filter(k => k !== VERSION).map(k => caches.delete(k)))).then(() => self.clients.claim())));
self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET' || new URL(e.request.url).origin !== location.origin) return;
  e.respondWith(fetch(e.request).then(r => {            // network first, cache fallback (always fresh online)
    const copy = r.clone(); caches.open(VERSION).then(c => c.put(e.request, copy)); return r;
  }).catch(() => caches.match(e.request, { ignoreSearch: true })));
});
