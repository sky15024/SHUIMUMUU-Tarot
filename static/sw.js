/* ============================================
   SHUIMUMUU 星空極光塔羅 — Service Worker
   策略：
   - 靜態資源 / HTML → Stale-While-Revalidate（快取優先，背景更新）
     → PWA 冷啟動時秒開，不會白屏
   - API 請求 → Network First（需要即時資料）
   ============================================ */

const CACHE_NAME = 'shuimumuu-tarot-v4';
const STATIC_ASSETS = [
  '/',
  '/static/css/style.css',
  '/static/js/app.js',
  '/static/images/pwa-icon-512.png'
];

// 安裝：預快取核心靜態資源
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(STATIC_ASSETS);
    }).catch(err => console.warn('快取安裝失敗:', err))
  );
  self.skipWaiting();
});

// 啟動：清除舊版快取
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))
      );
    })
  );
  self.clients.claim();
});

// 攔截請求
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);

  // ── API 請求 → 網路優先 (Network First) ──
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(
      fetch(event.request).catch(() => {
        return new Response(JSON.stringify({ success: false, error: '後端未開啟，請先雙擊 start.bat 啟動伺服器！' }), {
          headers: { 'Content-Type': 'application/json' }
        });
      })
    );
    return;
  }

  // ── 靜態資源與頁面 → Stale-While-Revalidate ──
  // 立即從快取回應（秒開），同時背景抓最新版本更新快取
  event.respondWith(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.match(event.request).then((cachedResponse) => {
        // 不論快取是否命中，都去網路抓最新的（背景更新）
        const fetchPromise = fetch(event.request).then((networkResponse) => {
          // 只快取同源的成功回應
          if (networkResponse.ok && url.origin === self.location.origin) {
            cache.put(event.request, networkResponse.clone());
          }
          return networkResponse;
        }).catch(() => {
          // 網路失敗時，回傳快取（如果有的話）
          return cachedResponse;
        });

        // 快取命中 → 立即回傳快取版本；快取未命中 → 等網路回應
        return cachedResponse || fetchPromise;
      });
    })
  );
});
