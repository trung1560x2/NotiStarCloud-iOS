/**
 * NotiStar Cloud (OneUI 7 iOS Edition) - Network-First OTA Service Worker
 * Luôn ưu tiên lấy bản cập nhật mới nhất qua mạng (OTA), chỉ dùng Cache khi mất mạng (Offline).
 * Tự động làm mới (auto-navigate) cửa sổ iPhone ngay khi nâng cấp từ bản cũ lên bản OTA mới.
 */

const CACHE_NAME = "notistar-ios-ota-v9";
const APP_SHELL_ASSETS = [
  "./",
  "./index.html",
  "./manifest.json",
  "./icon.png",
  "./version.json"
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
      let deletedOldCache = false;
      for (const key of keys) {
        if (key !== CACHE_NAME) {
          await caches.delete(key);
          deletedOldCache = true;
        }
      }
      await self.clients.claim();
      if (deletedOldCache) {
        const winClients = await self.clients.matchAll({ type: "window", includeUncontrolled: true });
        for (const client of winClients) {
          if (client.url && "navigate" in client) {
            try {
              await client.navigate(client.url);
            } catch (e) {}
          }
        }
      }
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

  // Network-First strategy for instant OTA updates!
  event.respondWith(
    fetch(req, { cache: "no-store" })
      .then((networkRes) => {
        if (networkRes && networkRes.status === 200 && url.origin === self.location.origin) {
          const clone = networkRes.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(req, clone)).catch(() => {});
        }
        return networkRes;
      })
      .catch(() => {
        return caches.match(req).then((cached) => {
          if (cached) return cached;
          if (req.mode === "navigate") {
            return caches.match("./index.html");
          }
          return new Response("Offline", { status: 503 });
        });
      })
  );
});

self.addEventListener("message", (event) => {
  if (event.data && event.data.type === "SKIP_WAITING") {
    self.skipWaiting();
  }
});
