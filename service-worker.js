const CACHE = "little-moon-shell-v1";
const SHELL = ["./", "./manifest.webmanifest", "./app-icon-192.png", "./app-icon-512.png", "./assets/little_moon_icon.svg"];
self.addEventListener("install", event => event.waitUntil(caches.open(CACHE).then(cache => cache.addAll(SHELL))));
self.addEventListener("activate", event => event.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(key => key !== CACHE).map(key => caches.delete(key))))));
self.addEventListener("fetch", event => {
  const request = event.request;
  const url = new URL(request.url);
  if (url.origin !== self.location.origin || url.pathname.endsWith("/app-url.txt")) return;
  event.respondWith(caches.match(request).then(cached => cached || fetch(request)));
});

