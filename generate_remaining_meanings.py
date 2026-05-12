"""
補齊剩餘牌義的改良版腳本
- 使用 gemini-2.0-flash (Free Tier 1500 RPD / 15 RPM) 替代 2.5-flash (20 RPD)
- 加入重試機制 (最多 3 次)
- 更安全的速率控制
"""

import os
import sys
import json
import asyncio
import time
from dotenv import load_dotenv
from google import genai

# 強制 Windows console 輸出 UTF-8
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# 載入環境變數
load_dotenv()

# 初始化 Gemini API (新版 SDK)
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ 錯誤：找不到 GEMINI_API_KEY。")
    exit(1)

client = genai.Client(api_key=api_key)

MODEL_NAME = "gemini-2.0-flash"

SYSTEM_INSTRUCTION = (
    "你是「水木沐沐星空極光塔羅」的專屬塔羅解讀師，名字叫「星語」。\n"
    "請用溫柔正向、充滿愛與希望的語氣撰寫塔羅牌義。\n"
    "你需要針對每一張牌，撰寫約 200~300 字的繁體中文解讀。\n"
    "正位：著重於正向能量、發展機會與溫暖鼓勵。\n"
    "逆位：著重於向內看、自我療癒、釋放壓力與溫柔提醒，不使用恐嚇或過度負面的詞彙。"
)

MAX_RETRIES = 3
BASE_DELAY = 5  # 付費版配額充裕，5 秒即可


async def generate_meaning_for_card(card: dict, attempt: int = 1):
    """呼叫 Gemini API 產生特定牌面的詳細正逆位牌義，含重試機制"""
    prompt = f"""
{SYSTEM_INSTRUCTION}

請為以下塔羅牌生成「詳細的牌義解讀」（請以第一人稱「星語」的角度，或是充滿溫暖的第三人稱視角撰寫）。
請回傳嚴格的 JSON 格式，包含兩個欄位：
1. "upright_meaning"：這張牌的正位詳細解讀（約 200~250 字）。
2. "reversed_meaning"：這張牌的逆位詳細解讀（約 200~250 字）。

牌面資訊：
- 牌名：{card['name_zh']} ({card['name_en']})
- 原本簡短正位牌義參考：{card.get('upright_meaning', '')}
- 原本簡短逆位牌義參考：{card.get('reversed_meaning', '')}

請務必確保回傳的是合法的 JSON 格式。
"""
    try:
        # 速率控制
        wait_time = BASE_DELAY * attempt
        await asyncio.sleep(wait_time)
        
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "temperature": 0.7,
            }
        )
        text = response.text.strip()
        
        # 清理可能存在的 Markdown 標記
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
            text = text.rsplit("```", 1)[0]
            
        result = json.loads(text)
        return {
            "upright": result.get("upright_meaning", card.get('upright_meaning')),
            "reversed": result.get("reversed_meaning", card.get('reversed_meaning')),
            "success": True
        }
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg and attempt < MAX_RETRIES:
            retry_wait = BASE_DELAY * (attempt + 1) * 2
            print(f"\n   ⚠️ 速率限制，等待 {retry_wait} 秒後重試 (第 {attempt}/{MAX_RETRIES} 次)...", end="", flush=True)
            await asyncio.sleep(retry_wait)
            return await generate_meaning_for_card(card, attempt + 1)
        
        print(f"\n   ❌ 生成失敗 (嘗試 {attempt} 次): {error_msg[:100]}")
        return {
            "upright": card.get('upright_meaning', ''),
            "reversed": card.get('reversed_meaning', ''),
            "success": False
        }


async def main():
    data_path = os.path.join("data", "tarot_cards.json")
    
    # 讀取現有資料
    with open(data_path, "r", encoding="utf-8") as f:
        cards = json.load(f)
    
    # 找出需要補齊的牌
    cards_to_update = []
    for i, card in enumerate(cards):
        current_upright = card.get('upright_meaning', '')
        if len(current_upright) < 100:
            cards_to_update.append((i, card))
    
    if not cards_to_update:
        print("🎉 所有 78 張牌都已有詳細牌義，無需更新！")
        return
    
    print(f"🌟 使用 {MODEL_NAME} 補齊剩餘 {len(cards_to_update)} 張牌的詳細牌義")
    print(f"⏳ 每張牌間隔 {BASE_DELAY} 秒，預計需要 {len(cards_to_update) * BASE_DELAY // 60} 分鐘...")
    print()
    
    success_count = 0
    fail_count = 0
    failed_cards = []
    
    for idx, (card_index, card) in enumerate(cards_to_update):
        print(f"[{idx+1}/{len(cards_to_update)}] 正在生成：{card['name_zh']} ({card['name_en']}) ...", end="", flush=True)
        
        new_meanings = await generate_meaning_for_card(card)
        
        if new_meanings["success"]:
            cards[card_index]["upright_meaning"] = new_meanings["upright"]
            cards[card_index]["reversed_meaning"] = new_meanings["reversed"]
            success_count += 1
            print(" 完成！✨")
        else:
            fail_count += 1
            failed_cards.append(card['name_zh'])
            print(f" 失敗 ❌ (保留簡短牌義)")
        
        # 每 10 張暫存一次
        if (idx + 1) % 10 == 0:
            with open(data_path, "w", encoding="utf-8") as f:
                json.dump(cards, f, ensure_ascii=False, indent=2)
            print(f"   💾 已暫存進度 ({success_count} 成功 / {fail_count} 失敗)")
    
    # 最終存檔
    with open(data_path, "w", encoding="utf-8") as f:
        json.dump(cards, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*50}")
    print(f"✅ 成功生成: {success_count} 張")
    print(f"❌ 生成失敗: {fail_count} 張")
    if failed_cards:
        print(f"   失敗清單: {', '.join(failed_cards)}")
    print(f"\n💾 資料已儲存至 {data_path}")
    
    # 驗證
    with open(data_path, "r", encoding="utf-8") as f:
        final_cards = json.load(f)
    short = [c for c in final_cards if len(c.get('upright_meaning', '')) < 100]
    print(f"\n📊 最終統計: {len(final_cards)} 張牌中還有 {len(short)} 張需要補齊")
    if len(short) == 0:
        print("🎉 完美！78 張塔羅牌的牌義資料庫已全部完成！")


if __name__ == "__main__":
    asyncio.run(main())
