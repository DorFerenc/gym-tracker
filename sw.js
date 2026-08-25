const CACHE = "gym-v6";
const SHELL = ["./", "./index.html", "./manifest.json"];
self.addEventListener("install", e => {
  // cache:"reload" bypasses the HTTP cache so a new SW never precaches a stale shell
  e.waitUntil(caches.open(CACHE).then(c =>
    Promise.all(SHELL.map(u => c.add(new Request(u, { cache: "reload" }))))
  ));
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
  const put = res => {
    // never cache error pages or redirects — a poisoned shell would be served offline
    if (res && res.ok && res.type === "basic")
      e.waitUntil(caches.open(CACHE).then(c => c.put(e.request, res.clone())));
    return res;
  };
  if (e.request.mode === "navigate") {
    // Network-first so deployed updates reach installed clients, but capped at 3s:
    // on a slow link the cached shell renders immediately and the fetch finishes
    // in the background (waitUntil) to refresh the cache for the next open.
    e.respondWith((async () => {
      const net = fetch(e.request).then(put).catch(() => null);
      e.waitUntil(net); // keep the SW alive so a post-timeout fetch still lands in cache
      const res = await Promise.race([net, new Promise(r => setTimeout(() => r(null), 3000))]);
      if (res) return res;
      const hit = await caches.match(e.request) || await caches.match("./index.html");
      if (hit) return hit;
      return (await net) || Response.error(); // nothing cached: wait the network out
    })());
    return;
  }
  e.respondWith(
    caches.match(e.request).then(hit => hit || fetch(e.request).then(put).catch(() => Response.error()))
  );
});
