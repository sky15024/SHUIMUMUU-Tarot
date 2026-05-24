/* ============================================
   SHUIMUMUU 星空極光塔羅 — Service Worker v5
   策略：
   - 導航請求（首頁）→ Cache First + 背景更新（防止 Render 冷啟動卡住）
   - 靜態資源 → Stale-While-Revalidate（快取優先，背景更新）
   - API 請求 → Network Only（離線回傳提示）
   ============================================ */

const CACHE_NAME = 'shuimumuu-tarot-v5';
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

  // ── API 請求 → Network Only（離線時回傳友善提示）──
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(
      fetch(event.request).catch(() => {
        return new Response(JSON.stringify({ success: false, error: '目前離線中，請確認網路連線後再試' }), {
          headers: { 'Content-Type': 'application/json' }
        });
      })
    );
    return;
  }

  // ── 導航請求（PWA 開啟 / 使用者輸入網址）→ Cache First + 背景更新 ──
  // 這是解決 Render 冷啟動的關鍵：先回傳快取的 HTML，再背景更新
  if (event.request.mode === 'navigate') {
    event.respondWith(
      caches.match('/').then((cached) => {
        // 不管有沒有快取，都嘗試在背景更新
        const fetchPromise = fetch(event.request).then((response) => {
          if (response.ok) {
            const clone = response.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put('/', clone));
          }
          return response;
        }).catch(() => null);

        // 有快取就直接回傳（不等 Render 喚醒）
        if (cached) {
          return cached;
        }

        // 沒有快取（極端情況：首次開啟且離線）→ 等待 network
        return fetchPromise.then((response) => {
          if (response) return response;
          // 連 network 都失敗，回傳基本離線頁面
          return new Response(
            '<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>星空極光塔羅</title><style>body{background:#06061a;color:#e8e8ff;font-family:sans-serif;display:flex;align-items:center;justify-content:center;min-height:100vh;text-align:center;}h1{font-size:1.5rem;margin-bottom:16px;}p{color:#a0a0d0;}</style></head><body><div><h1>✦ 星空極光塔羅 ✦</h1><p>目前無法連線，請稍後再試</p><button onclick="location.reload()" style="margin-top:20px;padding:12px 24px;background:linear-gradient(135deg,#667eea,#764ba2);color:white;border:none;border-radius:25px;cursor:pointer;font-size:1rem;">重新連線</button></div></body></html>',
            { headers: { 'Content-Type': 'text/html; charset=utf-8' } }
          );
        });
      })
    );
    return;
  }

  // ── 靜態資源 → Stale-While-Revalidate ──
  // 立即從快取回應（秒開），同時背景抓最新版本更新快取
  event.respondWith(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.match(event.request).then((cachedResponse) => {
        const fetchPromise = fetch(event.request).then((networkResponse) => {
          if (networkResponse.ok && url.origin === self.location.origin) {
            cache.put(event.request, networkResponse.clone());
          }
          return networkResponse;
        }).catch(() => cachedResponse);

        return cachedResponse || fetchPromise;
      });
    })
  );
});
