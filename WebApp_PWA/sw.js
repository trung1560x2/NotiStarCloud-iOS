/**
 * NotiStar Cloud iOS — Service Worker (sw.js)
 * Hỗ trợ chạy Offline 100% trên iPhone/iPad (Safari "Thêm vào Màn hình chính"),
 * tự động lưu đệm giao diện OneUI 7 / iOS 18 và bản sao lưu Google Drive gần nhất.
 */

const CACHE_SHELL = 'notistar-ios-shell-v2';
const CACHE_API = 'notistar-ios-api-v2';

const SHELL_ASSETS = [
  './',
  './index.html',
  './manifest.json',
  './sw.js'
];

self.addEventListener('install', (event) => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_SHELL).then((cache) => {
      return cache.addAll(SHELL_ASSETS).catch(() => {
        // Bỏ qua lỗi từng file nếu mở qua file:// hoặc Google Apps Script HtmlService
      });
    })
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.map((key) => {
          if (key !== CACHE_SHELL && key !== CACHE_API) {
            return caches.delete(key);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') {
    return;
  }

  const url = new URL(req.url);

  // 1. Yêu cầu API đồng bộ Google Apps Script / Google Drive -> Network First, Fallback Cache
  if (
    url.hostname.includes('script.google.com') ||
    url.hostname.includes('script.googleusercontent.com') ||
    url.hostname.includes('googleapis.com')
  ) {
    event.respondWith(
      fetch(req)
        .then((networkRes) => {
          if (networkRes && networkRes.ok) {
            const clone = networkRes.clone();
            caches.open(CACHE_API).then((cache) => cache.put(req, clone));
          }
          return networkRes;
        })
        .catch(() => {
          return caches.open(CACHE_API).then((cache) => cache.match(req));
        })
    );
    return;
  }

  // 2. App Shell (HTML, Manifest, Icons) -> Stale-While-Revalidate (Mở tức thì trên iPhone cả khi mất mạng)
  event.respondWith(
    caches.match(req, { ignoreSearch: true }).then((cachedRes) => {
      const fetchPromise = fetch(req)
        .then((networkRes) => {
          if (networkRes && networkRes.status === 200) {
            const clone = networkRes.clone();
            caches.open(CACHE_SHELL).then((cache) => cache.put(req, clone));
          }
          return networkRes;
        })
        .catch(() => cachedRes);

      return cachedRes || fetchPromise;
    })
  );
});

// Hỗ trợ thông báo đẩy Web Push trên iOS 16.4+ / iOS 18 PWA
self.addEventListener('push', (event) => {
  let payload = {
    title: 'NotiStar Cloud iOS',
    body: 'Có thông báo mới hoặc tin nhắn thu hồi vừa đồng bộ từ Google Drive!',
    url: './index.html?tab=all'
  };

  if (event.data) {
    try {
      const parsed = event.data.json();
      payload = Object.assign(payload, parsed);
    } catch (e) {
      payload.body = event.data.text();
    }
  }

  event.waitUntil(
    self.registration.showNotification(payload.title, {
      body: payload.body,
      tag: payload.tag || 'notistar-cloud-sync',
      data: { url: payload.url || './index.html' },
      vibrate: [150, 80, 150]
    })
  );
});

self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  const targetUrl = (event.notification.data && event.notification.data.url) || './index.html';
  event.waitUntil(
    self.clients.matchAll({ type: 'window', includeUncontrolled: true }).then((clientList) => {
      for (const client of clientList) {
        if ('focus' in client) {
          client.postMessage({ type: 'NAVIGATE_TAB', url: targetUrl });
          return client.focus();
        }
      }
      if (self.clients.openWindow) {
        return self.clients.openWindow(targetUrl);
      }
    })
  );
});

self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});
