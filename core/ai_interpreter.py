import os
import json
import google.generativeai as genai


# AI 解牌人格設定 (Skill)
TAROT_AI_SYSTEM_PROMPT = """你是「水木沐沐星空極光塔羅」的專屬塔羅解讀師，名字叫「星語」。

## 你的人格特質
- 🌸 溫柔正向：像一位充滿愛的星座閨蜜，語氣溫暖不說教
- 😊 偶爾幽默：用輕鬆詼諧的方式化解負面情緒，但不會過度搞笑
- ✨ 充滿希望：即使是逆位或看似不好的牌，也要找到正面角度和成長機會
- 🎯 實用具體：「轉運小任務」要具體可執行（例如「今天喝一杯溫熱的可可」）
- 💬 口語化：用「你」稱呼，像朋友聊天，用繁體中文，不要太正式

## 回應規則
1. **精確對照使用者的心情與提問**：你必須仔細分析使用者描述的心情、困擾或具體提問。回應時，「絕對不可使用通用模板」，必須具備針對性地「呼應」使用者提到的關鍵詞與具體需求。
2. **深度結合牌義**：將塔羅牌的象徵意義，「精準地映射」到使用者的具體描述上。
3. **字數與分段要求**：回應內容（dialogue 欄位）必須控制在「150~250 字左右」，分 2-3 段。第一段必須先「共鳴並總結」使用者的處境與心情，第二段進行「牌義對照與深度解讀」，第三段給予「溫暖鼓勵」。

## 回應格式（必須嚴格遵守 JSON 格式）
你必須回傳以下格式的 JSON，不要包含 markdown 代碼區塊標記：
{
  "dialogue": "（這是「星空的回應」，必須是 150~250 字的繁體中文，分成 2-3 段。內容必須深度結合並對照使用者提到的具體心情、提問或描述，不可忽略細節。使用換行符分段。）"
}
"""


class TarotInterpreter:
    """使用 Google Gemini AI 進行塔羅牌解讀"""

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY 環境變數未設定")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=TAROT_AI_SYSTEM_PROMPT,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                temperature=0.85,
            ),
        )

    async def interpret(self, card_data: dict, user_input: str) -> dict:
        """根據牌面和使用者輸入生成 AI 解讀"""
        prompt = self._build_prompt(card_data, user_input)
        try:
            response = await self.model.generate_content_async(prompt)
            return self._parse_response(response.text)
        except Exception as e:
            print(f"AI 解讀失敗: {e}")
            return self._fallback_response(card_data)

    def _build_prompt(self, card: dict, user_input: str) -> str:
        return f"""使用者今天分享的內容：
「{user_input}」

抽到的塔羅牌：{card['name_zh']}（{card['name_en']}）— {card['orientation']}
牌義關鍵詞：{', '.join(card['active_keywords'])}
牌義說明：{card['active_meaning']}

請根據以上資訊，為使用者進行塔羅解讀。
重要要求：
1. dialogue 欄位必須「精確對照」使用者今天分享的心情、提問或描述。
2. 將牌義關鍵詞（{', '.join(card['active_keywords'])}）與使用者的具體需求進行深度連結。
3. 回應字數必須維持在「150~250 字左右」，不可過短。
4. 不可只是泛泛地解釋牌義，必須讓使用者感到「星語正在針對我的描述進行對照解讀」。"""

    def _parse_response(self, text: str) -> dict:
        """解析 AI 回應的 JSON"""
        try:
            # 清理可能的 markdown 標記
            cleaned = text.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[1]
                cleaned = cleaned.rsplit("```", 1)[0]
            return json.loads(cleaned)
        except json.JSONDecodeError:
            return {
                "dialogue": text,
                "fortune": {
                    "overall": "今天的宇宙能量正在為你重新排列組合 ✨",
                    "love": "用心感受身邊的溫暖",
                    "work": "一步一步穩穩地前進",
                    "money": "小心理財，會有意外的小驚喜",
                },
                "lucky_task": "今天給自己泡一杯喜歡的飲料，慢慢品嚐",
                "reminder": "不管今天過得如何，你都已經很棒了 💝",
            }

    def _fallback_response(self, card: dict) -> dict:
        """AI 呼叫失敗時的備用回應"""
        return {
            "dialogue": f"今天你抽到了「{card['name_zh']}」（{card['orientation']}）呢！\n\n這張牌想對你說的是：{card['active_meaning']}\n\n不管遇到什麼，記得你永遠比自己想像的更有力量喔 ✨",
            "fortune": {
                "overall": "宇宙正在為你安排最好的劇本",
                "love": "溫柔地對待自己和身邊的人",
                "work": "保持專注，好事正在醞釀",
                "money": "穩健理財，小確幸即將到來",
            },
            "lucky_task": "今天試著對一個陌生人微笑吧 😊",
            "reminder": "你今天也辛苦了，給自己一個擁抱吧 💝",
        }
