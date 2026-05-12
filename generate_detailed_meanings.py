import os
import sys
import json
import asyncio
from dotenv import load_dotenv
import google.generativeai as genai

# 強制 Windows console 輸出 UTF-8
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# 載入環境變數
load_dotenv()

# 初始化 Gemini API
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ 錯誤：找不到 GEMINI_API_KEY。請確認您已經在專案目錄下建立了 .env 檔案並設定好金鑰。")
    exit(1)

genai.configure(api_key=api_key)

# 這裡選擇使用 gemini-1.5-flash，因為它速度快、成本低，且在 Google AI Studio 中享有 15 RPM 的免費額度，非常適合大量生成。
# 就算使用付費版本，成本也非常低微。
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction=(
        "你是「水木沐沐星空極光塔羅」的專屬塔羅解讀師，名字叫「星語」。\n"
        "請用溫柔正向、充滿愛與希望的語氣撰寫塔羅牌義。\n"
        "你需要針對每一張牌，撰寫約 200~300 字的繁體中文解讀。\n"
        "正位：著重於正向能量、發展機會與溫暖鼓勵。\n"
        "逆位：著重於向內看、自我療癒、釋放壓力與溫柔提醒，不使用恐嚇或過度負面的詞彙。"
    ),
    generation_config=genai.GenerationConfig(
        response_mime_type="application/json",
        temperature=0.7,
    ),
)

async def generate_meaning_for_card(card: dict):
    """呼叫 Gemini API 產生特定牌面的詳細正逆位牌義"""
    prompt = f"""
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
        # 在發送請求前稍微等待，避免達到 API 速率限制 (gemini-2.5-flash Free Tier 限制為 5 RPM)
        # 每張牌之間間隔約 13 秒
        await asyncio.sleep(13)
        
        response = await model.generate_content_async(prompt)
        text = response.text.strip()
        
        # 清理可能存在的 Markdown 標記
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
            text = text.rsplit("```", 1)[0]
            
        result = json.loads(text)
        return {
            "upright": result.get("upright_meaning", card.get('upright_meaning')),
            "reversed": result.get("reversed_meaning", card.get('reversed_meaning'))
        }
    except Exception as e:
        print(f"❌ 牌面 {card['name_zh']} 生成失敗: {str(e)}")
        # 失敗時回傳原始的簡短牌義以作為備案
        return {
            "upright": card.get('upright_meaning', ''),
            "reversed": card.get('reversed_meaning', '')
        }

async def main():
    data_path = os.path.join("data", "tarot_cards.json")
    
    # 讀取現有資料
    with open(data_path, "r", encoding="utf-8") as f:
        cards = json.load(f)
        
    print(f"🌟 開始為 {len(cards)} 張塔羅牌生成詳細牌義...")
    print("⏳ 偵測到您使用的是 API Free Tier (限制 5次/分鐘)，這個過程預計會花費 15~20 分鐘，請耐心等候...")
    
    updated_cards = []
    
    # 為了絕對確保不超過 Free Tier 5 RPM 的限制，我們採用循序 (sequential) 執行
    # 這樣每 13 秒處理一張，一分鐘約處理 4-5 張，非常安全
    for i, card in enumerate(cards):
        # 檢查是否已經有詳細牌義 (假設字數大於 100 字就視為已生成過)
        current_upright = card.get('upright_meaning', '')
        if len(current_upright) > 100:
            print(f"[{i+1}/{len(cards)}] ⏭️ 已跳過：{card['name_zh']} (已有詳細牌義)")
            updated_cards.append(card)
            continue
            
        print(f"[{i+1}/{len(cards)}] 正在生成：{card['name_zh']} ...", end="", flush=True)
        
        new_meanings = await generate_meaning_for_card(card)
        
        # 更新卡片資料
        card["upright_meaning"] = new_meanings["upright"]
        card["reversed_meaning"] = new_meanings["reversed"]
        updated_cards.append(card)
        
        print(" 完成！✨")
        
        # 每處理 10 張牌，先存檔一次以防中斷
        if (i + 1) % 10 == 0:
            with open(data_path, "w", encoding="utf-8") as f:
                json.dump(updated_cards + cards[i+1:], f, ensure_ascii=False, indent=2)
            print("   💾 已暫存進度...")

    # 最終存檔
    with open(data_path, "w", encoding="utf-8") as f:
        json.dump(updated_cards, f, ensure_ascii=False, indent=2)
        
    print("\n🎉 恭喜！所有 78 張塔羅牌的詳細牌義已成功生成並更新至 data/tarot_cards.json！")

if __name__ == "__main__":
    asyncio.run(main())
