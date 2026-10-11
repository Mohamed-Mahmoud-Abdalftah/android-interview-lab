// Network first keeps published content fresh; previously visited pages remain readable offline.
const CACHE = 'android-interview-lab-pages-v1';
const scopePath = new URL(self.registration.scope).pathname;

self.addEventListener('install', (event) => event.waitUntil(self.skipWaiting()));
self.addEventListener('activate', (event) => event.waitUntil((async () => {
  for (const key of await caches.keys()) if (key.startsWith('android-interview-lab-pages-') && key !== CACHE) await caches.delete(key);
  await self.clients.claim();
})()));
self.addEventListener('fetch', (event) => {
  const request = event.request;
  const url = new URL(request.url);
  if (request.method !== 'GET' || url.origin !== self.location.origin || !url.pathname.startsWith(scopePath)) return;
  event.respondWith((async () => {
    const cache = await caches.open(CACHE);
    try {
      const response = await fetch(request);
      if (response.ok && response.type === 'basic') cache.put(request, response.clone()).catch(() => {});
      return response;
    } catch {
      const cached = await cache.match(request);
      if (cached) return cached;
      if (request.mode === 'navigate') return new Response('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Offline</title><main><h1>Page unavailable offline</h1><p>Open this page online once to keep a cached copy for later.</p></main></html>', { status: 503, headers: { 'Content-Type': 'text/html; charset=utf-8' } });
      throw new Error('Resource unavailable offline');
    }
  })());
});
