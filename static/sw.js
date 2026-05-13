/* ============================================
   SHUIMUMUU 星空極光塔羅 — Service Worker
   策略：全部改為 Network First (網路優先)，確保隨時抓取最新版面
   ============================================ */

const CACHE_NAME = 'shuimumuu-tarot-v3';
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

// 攔截請求：網路優先 (Network First)
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);

  // API 請求 → 網路優先，失敗則回傳提示
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

  // 靜態資源與頁面 → 網路優先，失敗才讀取快取
  event.respondWith(
    fetch(event.request).then((response) => {
      // 判斷是否為 Render 喚醒畫面 (通常是 503 Service Unavailable)
      if (!response.ok && response.status === 503) {
        return caches.match(event.request).then(cached => cached || response);
      }

      // 成功取得最新資源，動態更新快取
      if (response.ok && url.origin === self.location.origin) {
        const clone = response.clone();
        caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
      }
      return response;
    }).catch(() => {
      // 網路失敗（伺服器沒開）時，從快取尋找
      return caches.match(event.request);
    })
  );
});
