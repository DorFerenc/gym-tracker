const CACHE = "gym-v4";
self.addEventListener("install", e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(["./", "./index.html", "./manifest.json"])));
  self.skipWaiting();
});
self.addEventListener("activate", e => {
  e.waitUntil(
    caches.keys()
      .then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});
self.addEventListener("fetch", e => {
  const url = new URL(e.request.url);
  // Same-origin GET only: the app never talks to other origins, so the SW won't either.
  if (e.request.method !== "GET" || url.origin !== location.origin) return;
  const cachePut = res => {
    const copy = res.clone();
    caches.open(CACHE).then(c => c.put(e.request, copy));
    return res;
  };
  // Network-first for the app shell so deployed updates reach installed clients.
  if (e.request.mode === "navigate" || url.pathname.endsWith("/index.html")) {
    e.respondWith(
      fetch(e.request).then(cachePut)
        .catch(() => caches.match(e.request).then(hit => hit || caches.match("./index.html")))
    );
    return;
  }
  e.respondWith(
    caches.match(e.request).then(hit => hit || fetch(e.request).then(cachePut))
  );
});
