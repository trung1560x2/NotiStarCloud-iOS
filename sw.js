/**
 * NotiStar Cloud (OneUI 7 iOS Edition) - Instant-Boot Stale-While-Revalidate + Live OTA Service Worker
 * - Phục vụ giao diện App Shell (index.html, icon, manifest) TỨC THÌ trong <5ms từ bộ nhớ đệm (0ms lag khi bật app).
 * - Đồng thời tự động tải ngầm bản mới nhất từ mạng để cập nhật Cache & kiểm tra version.json trực tiếp.
 */

const CACHE_NAME = "notistar-ios-ota-v10";
const APP_SHELL_ASSETS = [
  "./",
  "./index.html",
  "./manifest.json",
  "./icon.png"
];

self.addEventListener("install", (event) => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(APP_SHELL_ASSETS).catch(() => {});
    })
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    (async () => {
      const keys = await caches.keys();
      for (const key of keys) {
        if (key !== CACHE_NAME) {
          await caches.delete(key);
        }
      }
      await self.clients.claim();
    })()
  );
});

self.addEventListener("fetch", (event) => {
  const req = event.request;
  if (req.method !== "GET") return;

  const url = new URL(req.url);

  // Bypass Google Apps Script / Google Drive API calls (always live network)
  if (
    url.hostname.includes("script.google.com") ||
    url.hostname.includes("googleusercontent.com") ||
    url.hostname.includes("googleapis.com")
  ) {
    return;
  }

  // Luôn lấy trực tiếp từ mạng cho version.json hoặc các yêu cầu có ?_t= (kiểm tra OTA)
  if (url.pathname.endsWith("version.json") || url.search.includes("_t=")) {
    event.respondWith(
      fetch(req, { cache: "no-store" }).catch(() => caches.match(req))
    );
    return;
  }

  // Stale-While-Revalidate cho App Shell: Mở app tức thì (<5ms) từ Cache, đồng thời cập nhật ngầm từ mạng!
  event.respondWith(
    caches.open(CACHE_NAME).then(async (cache) => {
      const cachedRes = await cache.match(req);
      const networkPromise = fetch(req)
        .then((networkRes) => {
          if (networkRes && networkRes.status === 200 && url.origin === self.location.origin) {
            cache.put(req, networkRes.clone()).catch(() => {});
          }
          return networkRes;
        })
        .catch(() => null);

      if (cachedRes) {
        return cachedRes;
      }
      const netRes = await networkPromise;
      if (netRes) return netRes;
      if (req.mode === "navigate") {
        const fallback = await cache.match("./index.html");
        if (fallback) return fallback;
      }
      return new Response("Offline", { status: 503 });
    })
  );
});

self.addEventListener("message", (event) => {
  if (event.data && event.data.type === "SKIP_WAITING") {
    self.skipWaiting();
  }
});
