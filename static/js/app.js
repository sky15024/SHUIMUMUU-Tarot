/* ============================================
   SHUIMUMUU 星空極光塔羅 — 前端互動邏輯
   ============================================ */

document.addEventListener('DOMContentLoaded', () => {
    initStarfield();
    initInputHandlers();
    initLeftSidebar();
});

/* ---- 星空背景粒子 ---- */
function initStarfield() {
    const canvas = document.getElementById('starfield');
    const ctx = canvas.getContext('2d');
    let stars = [];
    const STAR_COUNT = 200;

    function resize() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }
    resize();
    window.addEventListener('resize', resize);

    for (let i = 0; i < STAR_COUNT; i++) {
        stars.push({
            x: Math.random() * canvas.width,
            y: Math.random() * canvas.height,
            r: Math.random() * 1.5 + 0.3,
            alpha: Math.random(),
            speed: Math.random() * 0.005 + 0.002,
            phase: Math.random() * Math.PI * 2,
        });
    }

    function drawStars() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Aurora gradient background
        const grd = ctx.createRadialGradient(
            canvas.width * 0.3, canvas.height * 0.3, 0,
            canvas.width * 0.3, canvas.height * 0.3, canvas.width * 0.6
        );
        grd.addColorStop(0, 'rgba(40, 20, 80, 0.15)');
        grd.addColorStop(1, 'transparent');
        ctx.fillStyle = grd;
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        const grd2 = ctx.createRadialGradient(
            canvas.width * 0.7, canvas.height * 0.7, 0,
            canvas.width * 0.7, canvas.height * 0.7, canvas.width * 0.5
        );
        grd2.addColorStop(0, 'rgba(0, 60, 120, 0.1)');
        grd2.addColorStop(1, 'transparent');
        ctx.fillStyle = grd2;
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        const time = Date.now() * 0.001;
        stars.forEach(star => {
            const flicker = Math.sin(time * star.speed * 200 + star.phase) * 0.4 + 0.6;
            ctx.beginPath();
            ctx.arc(star.x, star.y, star.r, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(200, 210, 255, ${star.alpha * flicker})`;
            ctx.fill();
        });

        requestAnimationFrame(drawStars);
    }
    drawStars();
}

/* ---- 輸入處理 ---- */
function initInputHandlers() {
    const textarea = document.getElementById('user-input');
    const charCount = document.getElementById('char-count');
    const drawBtn = document.getElementById('draw-btn');
    const retryBtn = document.getElementById('retry-btn');
    const modeBtns = document.querySelectorAll('.mode-btn');
    const manualContainer = document.getElementById('input-container-manual');
    const meditateContainer = document.getElementById('input-container-meditate');

    // 模式切換邏輯
    modeBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            modeBtns.forEach(b => b.classList.remove('active'));
            e.currentTarget.classList.add('active');
            currentMode = e.currentTarget.dataset.mode;

            if (currentMode === 'manual') {
                manualContainer.style.display = 'block';
                meditateContainer.style.display = 'none';
                drawBtn.disabled = textarea.value.length === 0;
            } else {
                manualContainer.style.display = 'none';
                meditateContainer.style.display = 'block';
                drawBtn.disabled = false; // 默念模式可直接點擊
            }
        });
    });

    textarea.addEventListener('input', () => {
        const len = textarea.value.length;
        charCount.textContent = len;
        if (currentMode === 'manual') {
            drawBtn.disabled = len === 0;
        }
    });

    drawBtn.addEventListener('click', handleDraw);
    retryBtn.addEventListener('click', handleRetry);
}

/* ---- 狀態管理 ---- */
let currentCard = null;
let isDrawing = false;
let currentMode = 'meditate';

/* ---- 抽牌流程 ---- */
async function handleDraw() {
    if (isDrawing) return;
    isDrawing = true;

    const userInput = document.getElementById('user-input').value.trim();
    if (currentMode === 'manual' && !userInput) return;

    const drawBtn = document.getElementById('draw-btn');
    drawBtn.disabled = true;
    drawBtn.querySelector('.btn-text').textContent = '🔮 占卜中...';

    try {
        // 1. 呼叫抽牌 API
        const drawRes = await fetch('/api/draw', { method: 'POST' });
        const drawData = await drawRes.json();

        if (!drawData.success) throw new Error('抽牌失敗');
        currentCard = drawData.card;

        // 2. 顯示翻牌動畫
        await showCardFlip(currentCard);

        // 3. 顯示結果區域 & 載入中
        showResultLoading();

        let interpData;

        // 4. 根據模式決定是否呼叫 AI 解讀 API
        if (currentMode === 'manual') {
            const interpRes = await fetch('/api/interpret', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_input: userInput,
                    card_id: currentCard.id,
                    is_reversed: currentCard.is_reversed,
                }),
            });
            interpData = await interpRes.json();
            if (!interpData.success) throw new Error('解讀失敗');
        } else {
            // 默念模式：直接使用牌義資料庫內容，模擬 AI 解讀的回傳格式
            await delay(1000); // 模擬稍微等待讓動畫順暢
            interpData = {
                success: true,
                interpretation: {
                    dialogue: currentCard.active_meaning,
                    fortune: currentCard.fortune,
                    lucky_task: currentCard.lucky_task,
                    reminder: currentCard.reminder
                }
            };
        }

        // 使用從資料庫隨機抽取的幸運任務，取代 AI 產生的
        if (currentCard.lucky_task) {
            interpData.interpretation.lucky_task = currentCard.lucky_task;
        }

        // 5. 顯示解讀結果（打字機效果）
        await showInterpretation(interpData.interpretation);

    } catch (err) {
        console.error('占卜流程錯誤:', err);
        showError('當前的時機似乎還在醞釀，請重新靜下心來，再次與牌面連結。');
    } finally {
        isDrawing = false;
    }
}

/* ---- 翻牌動畫 ---- */
async function showCardFlip(card) {
    const cardSection = document.getElementById('card-section');
    const tarotCard = document.getElementById('tarot-card');
    const cardBack = tarotCard.querySelector('.card-back');
    const keywordsDiv = document.getElementById('card-keywords');
    const flash = document.getElementById('card-flash');
    const infoDisplay = document.getElementById('card-info-display');

    // 確保獨立文字區塊在翻牌前隱藏
    if (infoDisplay) infoDisplay.style.display = 'none';

    // 如果卡片目前是翻開的狀態，先把它翻轉回背面並等待動畫完成（避免換圖時暴雷）
    if (tarotCard.classList.contains('flipped')) {
        tarotCard.classList.remove('flipped');
        if (infoDisplay) infoDisplay.style.display = 'none';
        await delay(1200);
    }

    // 重置狀態
    keywordsDiv.style.display = 'none';
    flash.classList.remove('active');
    if (infoDisplay) infoDisplay.style.display = 'none';

    // 確保牌背可見
    cardBack.style.display = 'block';

    // 先預載圖片，再設定正面
    await preloadCardImage(card);
    setupCardFront(card);

    // 顯示卡片區（此時看到的是牌背）
    cardSection.style.display = 'flex';
    cardSection.scrollIntoView({ behavior: 'smooth', block: 'center' });

    // 等一下，讓使用者看到牌背
    await delay(1200);

    // 觸發金光特效
    flash.classList.add('active');
    await delay(400);

    // 翻牌！
    tarotCard.classList.add('flipped');

    // 等待翻牌動畫完成
    await delay(1400);

    // 隱藏牌背（避免遮擋正面點擊）
    cardBack.style.display = 'none';

    // 顯示文字資訊
    if (infoDisplay) infoDisplay.style.display = 'block';

    // 顯示關鍵詞
    showKeywords(card.active_keywords);
}

/* ---- 預載圖片 ---- */
function preloadCardImage(card) {
    return new Promise((resolve) => {
        if (!card.image) {
            card._imageLoaded = false;
            resolve();
            return;
        }
        const img = new Image();
        img.onload = () => {
            card._imageLoaded = true;
            resolve();
        };
        img.onerror = () => {
            console.warn(`圖片載入失敗: ${card.image}`);
            card._imageLoaded = false;
            resolve();
        };
        img.src = `/static/${card.image}`;
    });
}

function setupCardFront(card) {
    const nameZh = document.getElementById('card-name-zh');
    const nameEn = document.getElementById('card-name-en');
    const orientation = document.getElementById('card-orientation');
    const cardImage = document.getElementById('card-image');
    const fallback = document.getElementById('card-image-fallback');
    const fallbackSymbol = document.getElementById('fallback-symbol');

    nameZh.textContent = card.name_zh;
    nameEn.textContent = card.name_en.toUpperCase();
    orientation.textContent = card.orientation;

    // 大阿爾克那符號對應
    const majorSymbols = {
        0: '🃏', 1: '🎩', 2: '🌙', 3: '👑', 4: '🏛️', 5: '⛪',
        6: '💕', 7: '🏇', 8: '🦁', 9: '🏮', 10: '☸️', 11: '⚖️',
        12: '🔄', 13: '💀', 14: '⏳', 15: '😈', 16: '🗼', 17: '⭐',
        18: '🌙', 19: '☀️', 20: '📯', 21: '🌍'
    };

    // 小阿爾克那符號對應（以花色區分）
    const minorSuitSymbols = {
        wands: '🔥',
        cups: '🏆',
        swords: '⚔️',
        pentacles: '💰'
    };

    // 取得 fallback 符號
    const getFallbackSymbol = () => {
        if (card.arcana === 'major') {
            return majorSymbols[card.number] || '✦';
        }
        return minorSuitSymbols[card.suit] || '✦';
    };

    // 使用預載結果決定顯示圖片或 fallback
    if (card._imageLoaded && card.image) {
        cardImage.src = `/static/${card.image}`;
        cardImage.alt = card.name_zh;
        cardImage.style.display = 'block';
        fallback.style.display = 'none';
    } else {
        cardImage.style.display = 'none';
        fallback.style.display = 'flex';
        fallbackSymbol.textContent = getFallbackSymbol();
    }

    // 逆位旋轉：僅旋轉圖片容器，維持文字正確方向
    const imageWrapper = document.querySelector('.card-image-wrapper');
    if (card.is_reversed) {
        imageWrapper.style.transform = 'rotate(180deg)';
    } else {
        imageWrapper.style.transform = 'none';
    }
}

function showKeywords(keywords) {
    const keywordsDiv = document.getElementById('card-keywords');
    keywordsDiv.innerHTML = keywords
        .map(kw => `<span class="keyword-tag">${kw}</span>`)
        .join('');
    keywordsDiv.style.display = 'flex';
}

/* ---- 結果區域 ---- */
function showResultLoading() {
    const resultSection = document.getElementById('result-section');
    const loadingIndicator = document.getElementById('loading-indicator');
    const interpretation = document.getElementById('interpretation');
    const retryBtn = document.getElementById('retry-btn');

    resultSection.style.display = 'flex';
    loadingIndicator.style.display = 'block';
    
    // 確保每次重新抽牌時，還原 loading-indicator 的內部 HTML，避免被先前的 showError 覆蓋
    loadingIndicator.innerHTML = `
        <div class="loading-orb"></div>
        <p class="loading-text">正在與宇宙頻率連結，請等待星辰回應...</p>
    `;
    
    interpretation.style.display = 'none';
    retryBtn.style.display = 'none';

    resultSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

async function showInterpretation(data) {
    const loadingIndicator = document.getElementById('loading-indicator');
    const interpretation = document.getElementById('interpretation');
    const retryBtn = document.getElementById('retry-btn');

    loadingIndicator.style.display = 'none';
    interpretation.style.display = 'block';

    // 填充內容（帶打字機效果）
    await typeText('dialogue-text', data.dialogue || '');

    // 運勢
    if (data.fortune) {
        setFortuneText('fortune-overall', data.fortune.overall);
        setFortuneText('fortune-love', data.fortune.love);
        setFortuneText('fortune-work', data.fortune.work);
        setFortuneText('fortune-money', data.fortune.money);
    }

    // 轉運小任務
    document.getElementById('lucky-task').textContent = data.lucky_task || '';

    // 溫馨小提醒
    document.getElementById('reminder-text').textContent = data.reminder || '';

    // 顯示再抽一次按鈕
    retryBtn.style.display = 'inline-block';

    // 顯示分享按鈕
    const shareButtons = document.getElementById('share-buttons');
    if (shareButtons) shareButtons.style.display = 'flex';

    // 第一次抽牌完成時，彈出廣告插頁
    showAdOnce();

    // 捲動到結果區域頂部，確保使用者能看到「星空的回應」
    resultSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function setFortuneText(elementId, text) {
    const el = document.getElementById(elementId);
    if (el) {
        el.querySelector('.fortune-value').textContent = text || '';
    }
}

/* ---- 打字機效果 ---- */
async function typeText(elementId, text) {
    const el = document.getElementById(elementId);
    el.textContent = '';
    const chars = text.split('');
    const chunkSize = 3; // 每次顯示 3 個字元加速

    for (let i = 0; i < chars.length; i += chunkSize) {
        el.textContent += chars.slice(i, i + chunkSize).join('');
        await delay(30);
    }
}

/* ---- 再抽一次 ---- */
function handleRetry() {
    const cardSection = document.getElementById('card-section');
    const resultSection = document.getElementById('result-section');
    const tarotCard = document.getElementById('tarot-card');
    const drawBtn = document.getElementById('draw-btn');
    const input = document.getElementById('user-input');
    const flash = document.getElementById('card-flash');
    const cardBack = tarotCard.querySelector('.card-back');

    // 清空輸入框與字數統計
    input.value = '';
    const charCount = document.getElementById('char-count');
    if (charCount) charCount.textContent = '0';

    // 隱藏結果
    cardSection.style.display = 'none';
    resultSection.style.display = 'none';
    tarotCard.classList.remove('flipped');

    // 隱藏分享按鈕
    const shareButtons = document.getElementById('share-buttons');
    if (shareButtons) shareButtons.style.display = 'none';

    // 恢復牌背和金光
    cardBack.style.display = 'block';
    flash.classList.remove('active');

    // 重新啟用按鈕
    if (currentMode === 'manual') {
        drawBtn.disabled = true; // 因為已經清空輸入框，所以手動模式下預設為禁用
    } else {
        drawBtn.disabled = false;
    }
    drawBtn.querySelector('.btn-text').textContent = '✨ 開始占卜 ✨';

    // 滾到頂部
    document.getElementById('input-section').scrollIntoView({ behavior: 'smooth' });

    currentCard = null;
}

/* ---- 錯誤處理 ---- */
function showError(message) {
    const loadingIndicator = document.getElementById('loading-indicator');
    if (loadingIndicator) {
        loadingIndicator.innerHTML = `
            <div style="color: var(--accent-pink); font-size: 2rem; margin-bottom: 16px;">✦</div>
            <p style="color: var(--text-accent);">${message}</p>
        `;
    }
    const drawBtn = document.getElementById('draw-btn');
    drawBtn.disabled = false;
    drawBtn.querySelector('.btn-text').textContent = '✨ 開始占卜 ✨';

    const retryBtn = document.getElementById('retry-btn');
    retryBtn.style.display = 'inline-block';
}

/* ---- 工具 ---- */
function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

/* ========== 左側互動側邊欄 ========== */
function initLeftSidebar() {
    const toggles = document.querySelectorAll('.left-toggle-btn');
    const tabs = document.querySelectorAll('.left-tab');

    // 切換面板
    toggles.forEach(toggle => {
        toggle.addEventListener('click', (e) => {
            e.stopPropagation();
            const parentTab = toggle.closest('.left-tab');
            const isActive = parentTab.classList.contains('open');
            
            // 關閉所有面板
            tabs.forEach(tab => {
                tab.classList.remove('open');
                tab.querySelector('.left-toggle-btn').classList.remove('active');
            });

            // 如果原本沒開，就打開這個
            if (!isActive) {
                parentTab.classList.add('open');
                toggle.classList.add('active');
            }
        });
    });

    // 點擊外部自動關閉
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.left-sidebar-container')) {
            tabs.forEach(tab => {
                tab.classList.remove('open');
                tab.querySelector('.left-toggle-btn').classList.remove('active');
            });
        }
    });

    initHealingInteraction();
    initPunishInteraction();
    initInstallGuide();
}

function initHealingInteraction() {
    const area = document.getElementById('area-healing');
    const scoreSpan = document.getElementById('score-healing');
    const particles = document.getElementById('healing-particles');
    const charImg = document.getElementById('char-healing');
    let score = 0;
    let lastMoveTime = 0;

    function handlePet(e) {
        const now = Date.now();
        if (now - lastMoveTime < 100) return; // 節流，避免產生太多愛心
        lastMoveTime = now;

        score += 1;
        scoreSpan.textContent = score;

        // 產生愛心特效
        createParticle(e, particles, ['💖', '✨', '💕', '⭐']);
    }

    if (area) {
        area.addEventListener('mousemove', (e) => {
            // 設定為滑鼠經過就觸發安撫
            handlePet(e);
        });
        area.addEventListener('touchmove', (e) => {
            if(e.cancelable) e.preventDefault();
            handlePet(e.touches[0]);
        }, {passive: false});

        // 支援手機觸控圖片切換
        area.addEventListener('touchstart', () => {
            if (charImg) charImg.src = '/static/images/角色A-被摸.png';
        }, {passive: true});
        area.addEventListener('touchend', () => {
            if (charImg) charImg.src = '/static/images/角色A-正常.png';
        });
        area.addEventListener('touchcancel', () => {
            if (charImg) charImg.src = '/static/images/角色A-正常.png';
        });
    }
}

function initPunishInteraction() {
    const area = document.getElementById('area-punish');
    const char = document.getElementById('char-punish');
    const scoreSpan = document.getElementById('score-punish');
    const particles = document.getElementById('punish-particles');
    const nameInput = document.getElementById('punish-target-name');
    const nameDisplay = document.getElementById('target-name-display');
    let score = 0;
    
    let state = 'normal'; // 'normal', 'hurt', 'angry', 'flattened'
    let angryTimeout = null;
    let hurtTimeout = null;
    // 隨機設定 8~15 次被揍扁
    let flattenTarget = Math.floor(Math.random() * 8) + 8; 

    // 同步顯示小人名字
    if (nameInput && nameDisplay) {
        nameInput.addEventListener('input', (e) => {
            nameDisplay.textContent = e.target.value;
        });
    }

    // 建立自訂鞭子鼠標
    const whipCursor = document.createElement('div');
    whipCursor.id = 'whip-cursor';
    whipCursor.innerHTML = `<svg viewBox="0 0 24 72" width="24" height="72" xmlns="http://www.w3.org/2000/svg">
        <!-- 鞭身（長條狀淺咖啡色） -->
        <line x1="6" y1="2" x2="6" y2="44" stroke="#D2B48C" stroke-width="3" stroke-linecap="round"/>
        <!-- 鞭尾（漸細） -->
        <line x1="6" y1="2" x2="5" y2="0" stroke="#C4A882" stroke-width="1.5" stroke-linecap="round"/>
        <!-- 握把（深咖啡色） -->
        <rect x="3" y="44" width="6" height="18" rx="3" fill="#8B4513"/>
        <line x1="3" y1="48" x2="9" y2="48" stroke="#A0522D" stroke-width="1"/>
        <line x1="3" y1="52" x2="9" y2="52" stroke="#A0522D" stroke-width="1"/>
        <line x1="3" y1="56" x2="9" y2="56" stroke="#A0522D" stroke-width="1"/>
    </svg>`;
    document.body.appendChild(whipCursor);

    if (area && char) {
        // 讓鞭子跟隨鼠標
        area.addEventListener('mousemove', (e) => {
            whipCursor.style.left = e.clientX + 'px';
            whipCursor.style.top = e.clientY + 'px';
        });
        area.addEventListener('mouseenter', () => whipCursor.style.display = 'block');
        area.addEventListener('mouseleave', () => whipCursor.style.display = 'none');
        const resetToNormal = () => {
            if (state === 'flattened') return;
            state = 'normal';
            char.className = 'interactive-char';
            char.src = '/static/images/punching_villain_doll.png?v=2';
        };

        // 支援點擊與觸控
        const handleHit = (e) => {
            if (e.cancelable) e.preventDefault();
            // 如果已經扁了就不反應
            if (state === 'flattened') return; 

            // 觸發鞭打動畫
            whipCursor.classList.remove('strike');
            void whipCursor.offsetWidth; // 強制重繪
            whipCursor.classList.add('strike');

            score += 1;
            scoreSpan.textContent = score;

            if (angryTimeout) clearTimeout(angryTimeout);
            if (hurtTimeout) clearTimeout(hurtTimeout);

            // 檢查是否達到揍扁次數
            if (score >= flattenTarget) {
                state = 'flattened';
                char.className = 'interactive-char char-flattened';
                char.src = '/static/images/角色B-被打扁.png';
                createParticle(e.type.includes('touch') ? e.touches[0] : e, particles, ['💀', '👻', '💨']);
                
                // 5秒後小人會憤怒復活
                setTimeout(() => {
                    score = 0; 
                    flattenTarget = Math.floor(Math.random() * 8) + 8;
                    state = 'angry';
                    char.className = 'interactive-char char-angry';
                    char.src = '/static/images/punching_villain_doll.png?v=2';
                    scoreSpan.textContent = score;
                }, 5000);
                return;
            }

            // 還沒扁，進入受痛狀態
            state = 'hurt';
            char.className = 'interactive-char'; // Reset first
            void char.offsetWidth; // Trigger reflow
            char.className = 'interactive-char char-hurt';

            // 產生打擊特效
            createParticle(e.type.includes('touch') ? e.touches[0] : e, particles, ['💢', '👊', '💥', '😵']);

            // 0.3 秒後不再痛
            hurtTimeout = setTimeout(() => {
                if (state !== 'flattened') {
                    resetToNormal();
                    // 如果停手 1.5 秒，小人就會變生氣
                    angryTimeout = setTimeout(() => {
                        state = 'angry';
                        char.className = 'interactive-char char-angry';
                        const rect = area.getBoundingClientRect();
                        createParticle({clientX: rect.left + rect.width/2, clientY: rect.top + 40}, particles, ['💢', '🔥', '🤬']);
                    }, 1500);
                }
            }, 300);
        };

        area.addEventListener('mousedown', handleHit);
        area.addEventListener('touchstart', handleHit, {passive: false});
    }
}

function createParticle(event, container, emojis) {
    if (!container) return;
    const rect = container.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;

    const el = document.createElement('div');
    el.className = 'particle';
    el.textContent = emojis[Math.floor(Math.random() * emojis.length)];
    
    // 稍微隨機偏移
    const offsetX = (Math.random() - 0.5) * 60;
    el.style.left = `${x + offsetX}px`;
    el.style.top = `${y}px`;
    
    container.appendChild(el);

    // 動畫結束後移除DOM，保持乾淨
    setTimeout(() => {
        el.remove();
    }, 1000);
}

/* ========== PWA 安裝引導 ========== */
let deferredInstallPrompt = null;

// 攔截 beforeinstallprompt（Chrome / Edge / Samsung Browser 等）
window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredInstallPrompt = e;
    // 如果安裝面板已初始化，顯示原生安裝按鈕
    const nativeDiv = document.getElementById('install-native');
    if (nativeDiv) nativeDiv.style.display = 'block';
    // 隱藏手動教學
    const manualDiv = document.getElementById('install-android-manual');
    if (manualDiv) manualDiv.style.display = 'none';
});

function initInstallGuide() {
    const installBtn = document.getElementById('install-pwa-btn');
    const isStandalone = window.matchMedia('(display-mode: standalone)').matches
        || window.navigator.standalone === true;

    // 如果已經以 PWA 模式執行
    if (isStandalone) {
        const doneDiv = document.getElementById('install-done');
        if (doneDiv) doneDiv.style.display = 'block';
        return;
    }

    // 偵測裝置類型
    const ua = navigator.userAgent || '';
    const isIOS = /iPad|iPhone|iPod/.test(ua) && !window.MSStream;
    const isAndroid = /Android/.test(ua);

    if (isIOS) {
        // iOS → 顯示 Safari 分享步驟
        const iosDiv = document.getElementById('install-ios');
        if (iosDiv) iosDiv.style.display = 'block';
    } else if (isAndroid) {
        // Android → 優先顯示原生安裝按鈕（如果已攔截到 prompt）
        if (deferredInstallPrompt) {
            const nativeDiv = document.getElementById('install-native');
            if (nativeDiv) nativeDiv.style.display = 'block';
        } else {
            // 沒有攔截到 prompt → 顯示手動教學
            const manualDiv = document.getElementById('install-android-manual');
            if (manualDiv) manualDiv.style.display = 'block';
        }
    } else {
        // 桌面版
        const desktopDiv = document.getElementById('install-desktop');
        if (desktopDiv) desktopDiv.style.display = 'block';

        // 桌面版一律顯示按鈕，若無法自動安裝則提示使用者手動操作
        const nativeDiv = document.getElementById('install-native');
        if (nativeDiv) nativeDiv.style.display = 'block';
    }

    // 一鍵安裝按鈕
    if (installBtn) {
        installBtn.addEventListener('click', async () => {
            if (!deferredInstallPrompt) {
                if (confirm("需要重新整理頁面才能再次啟動下載程序。\n是否立即重新整理？")) {
                    window.location.reload();
                }
                return;
            }
            deferredInstallPrompt.prompt();
            const result = await deferredInstallPrompt.userChoice;
            if (result.outcome === 'accepted') {
                // 安裝成功
                const nativeDiv = document.getElementById('install-native');
                if (nativeDiv) nativeDiv.style.display = 'none';
                const doneDiv = document.getElementById('install-done');
                if (doneDiv) doneDiv.style.display = 'block';
            } else {
                // 若使用者取消或安裝沒成功，變更按鈕文字提示
                const textSpan = installBtn.querySelector('span:last-child');
                if (textSpan) textSpan.textContent = "重新啟動下載";
            }
            deferredInstallPrompt = null;
        });
    }
}

/* ========== 社群分享功能 ========== */
// 偵測 LINE 內建瀏覽器
function isLineIAB() {
  return /Line/i.test(navigator.userAgent);
}

// 偵測手機裝置
function isMobile() {
  return /Android|iPhone|iPad|iPod/i.test(navigator.userAgent);
}

// 跨瀏覽器複製文字（含 LINE IAB fallback）
function copyTextFallback(str) {
  if (navigator.clipboard && navigator.clipboard.writeText) {
    return navigator.clipboard.writeText(str).catch(function() { return execCopyFallback(str); });
  }
  return execCopyFallback(str);
}
function execCopyFallback(str) {
  return new Promise(function(resolve) {
    var ta = document.createElement('textarea');
    ta.value = str;
    ta.style.cssText = 'position:fixed;left:-9999px;top:-9999px;opacity:0;';
    document.body.appendChild(ta);
    ta.focus(); ta.select();
    try { document.execCommand('copy'); } catch(e) {}
    document.body.removeChild(ta);
    resolve();
  });
}

// 跨瀏覽器開啟連結
function openUrl(url) {
  window.open(url, '_blank');
}

// 分享功能（不可加 async！popup blocker 會擋）
function shareTo(platform) {
  var url = window.location.href;
  var text = '✨ 我剛在星空極光塔羅抽了一張牌，來看看你的今日運勢吧！';
  var fullText = encodeURIComponent(text + ' ' + url);

  // 複製連結
  if (platform === 'copy') {
    copyTextFallback(text + '\n' + url).then(function() {
      showShareToast('✅ 已複製到剪貼簿！');
    });
    return;
  }

  // IG：複製文字 + 提示 → 開 IG app
  if (platform === 'ig') {
    copyTextFallback(text + ' ' + url).then(function() {
      showShareToast('📸 文字已複製！請到 IG 限動或貼文手動貼上');
      setTimeout(function() {
        if (isMobile()) { window.location.href = 'instagram://app'; }
        else { openUrl('https://www.instagram.com/'); }
      }, 600);
    });
    return;
  }

  // LINE / Threads / FB
  var shareUrl = '';
  switch (platform) {
    case 'line':
      if (isMobile()) {
        shareUrl = 'line://msg/text/' + encodeURIComponent(text + '\n' + url);
      } else if (isLineIAB()) {
        shareUrl = 'https://line.me/R/share?text=' + fullText;
      } else {
        shareUrl = 'https://social-plugins.line.me/lineit/share?url=' + encodeURIComponent(url) + '&text=' + encodeURIComponent(text);
      }
      break;
    case 'threads':
      shareUrl = 'https://www.threads.net/intent/post?text=' + fullText;
      break;
    case 'fb':
      if (isMobile()) {
        window.location.href = 'fb://share/?link=' + encodeURIComponent(url) + '&quote=' + encodeURIComponent(text);
        setTimeout(function() {
          window.open('https://www.facebook.com/sharer/sharer.php?u=' + encodeURIComponent(url) + '&quote=' + encodeURIComponent(text), '_blank');
        }, 1500);
        return;
      }
      shareUrl = 'https://www.facebook.com/sharer/sharer.php?u=' + encodeURIComponent(url) + '&quote=' + encodeURIComponent(text);
      break;
  }
  if (shareUrl) {
    if (platform === 'line' && isMobile()) {
      window.location.href = shareUrl;
    } else {
      openUrl(shareUrl);
    }
  }
}

// Toast 提示
function showShareToast(msg) {
  var toast = document.getElementById('share-toast');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'share-toast';
    toast.style.cssText = 'position:fixed;bottom:80px;left:50%;transform:translateX(-50%) translateY(20px);background:rgba(10,10,30,0.95);border:1px solid rgba(139,92,246,0.3);color:#e8e8ff;padding:14px 24px;border-radius:16px;font-size:14px;z-index:9999;opacity:0;transition:all 0.3s;backdrop-filter:blur(12px);text-align:center;max-width:320px;';
    document.body.appendChild(toast);
  }
  toast.textContent = msg;
  toast.style.opacity = '1';
  toast.style.transform = 'translateX(-50%) translateY(0)';
  setTimeout(function() {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(-50%) translateY(20px)';
  }, 4000);
}

/* ========== 廣告插頁彈窗 ========== */
var _adShown = false;

function showAdOnce() {
  if (_adShown) return;
  _adShown = true;
  var modal = document.getElementById('ad-modal');
  if (modal) {
    modal.classList.add('show');
  }
}

function closeAdModal() {
  var modal = document.getElementById('ad-modal');
  if (modal) {
    modal.classList.remove('show');
  }
}
