import json
import random
from pathlib import Path


class TarotEngine:
    """塔羅牌抽牌引擎 — 管理 78 張偉特塔羅牌的抽取邏輯"""

    def __init__(self):
        data_path = Path(__file__).parent.parent / "data" / "tarot_cards.json"
        with open(data_path, "r", encoding="utf-8") as f:
            self.cards = json.load(f)
        self._card_map = {card["id"]: card for card in self.cards}
        
        tasks_path = Path(__file__).parent.parent / "data" / "lucky_tasks.json"
        with open(tasks_path, "r", encoding="utf-8") as f:
            self.lucky_tasks = json.load(f)

        reminders_path = Path(__file__).parent.parent / "data" / "reminders.json"
        with open(reminders_path, "r", encoding="utf-8") as f:
            self.reminders = json.load(f)
            
        fortunes_path = Path(__file__).parent.parent / "data" / "tarot_fortunes.json"
        with open(fortunes_path, "r", encoding="utf-8") as f:
            self.fortunes = json.load(f)

    def draw_card(self):
        """隨機抽取一張牌，並決定正位/逆位"""
        card = random.choice(self.cards)
        is_reversed = random.choice([True, False])
        return self._build_result(card, is_reversed)

    def get_card(self, card_id: int):
        """根據 ID 取得特定牌面資料"""
        return self._card_map.get(card_id)

    def get_full_card(self, card_id: int, is_reversed: bool) -> dict:
        """根據 ID 取得完整的解讀結果（包含運勢、任務、提醒）"""
        card = self.get_card(card_id)
        if not card:
            return None
        return self._build_result(card, is_reversed)

    def _get_lucky_task(self, card: dict) -> str:
        """根據牌面屬性抽取對應的轉運小任務"""
        arcana = card.get("arcana")
        category_pool = ["healing"]  # default fallback
        
        if arcana == "minor":
            suit = card.get("suit")
            if suit == "cups":
                category_pool = ["connection", "healing"]
            elif suit == "wands":
                category_pool = ["action", "healing"]
            elif suit == "swords":
                category_pool = ["healing", "action"]
            elif suit == "pentacles":
                category_pool = ["action", "connection"]
        else:
            card_id = card.get("id")
            action_ids = [0, 1, 4, 7, 8, 10, 11, 15, 19, 20]
            healing_ids = [2, 9, 12, 13, 14, 16, 17, 18]
            connection_ids = [3, 5, 6, 21]
            
            if card_id in action_ids:
                category_pool = ["action"]
            elif card_id in healing_ids:
                category_pool = ["healing"]
            elif card_id in connection_ids:
                category_pool = ["connection"]

        chosen_category = random.choice(category_pool)
        return random.choice(self.lucky_tasks[chosen_category])

    def _get_reminder(self, card: dict) -> str:
        """根據牌面屬性抽取對應的溫馨小提醒"""
        arcana = card.get("arcana")
        primary_category = "universal"
        
        if arcana == "minor":
            suit = card.get("suit")
            if suit == "swords":
                primary_category = "healing"
            elif suit in ["wands", "pentacles"]:
                primary_category = "action"
            elif suit == "cups":
                primary_category = "connection"
        else:
            card_id = card.get("id")
            action_ids = [0, 1, 4, 7, 8, 10, 11, 15, 19, 20]
            healing_ids = [2, 9, 12, 13, 14, 16, 17, 18]
            connection_ids = [3, 5, 6, 21]
            
            if card_id in action_ids:
                primary_category = "action"
            elif card_id in healing_ids:
                primary_category = "healing"
            elif card_id in connection_ids:
                primary_category = "connection"
                
        # 從 Primary + Universal 中隨機抽取
        pool = self.reminders.get(primary_category, []) + self.reminders.get("universal", [])
        return random.choice(pool) if pool else "你今天也辛苦了，給自己一個擁抱吧 ❤️"

    def _build_result(self, card: dict, is_reversed: bool) -> dict:
        card_id_str = str(card["id"])
        state_key = "reversed" if is_reversed else "upright"
        fortune = self.fortunes.get(card_id_str, {}).get(state_key, {
            "overall": "宇宙正在為你安排最好的劇本",
            "love": "用心感受身邊的溫暖",
            "work": "保持專注，好事正在醞釀",
            "money": "穩健理財，小確幸即將到來",
        })

        return {
            "id": card["id"],
            "name_en": card["name_en"],
            "name_zh": card["name_zh"],
            "arcana": card["arcana"],
            "suit": card.get("suit"),
            "number": card["number"],
            "is_reversed": is_reversed,
            "orientation": "逆位" if is_reversed else "正位",
            "active_keywords": card["reversed_keywords"] if is_reversed else card["upright_keywords"],
            "active_meaning": card["reversed_meaning"] if is_reversed else card["upright_meaning"],
            "image": card.get("image"),
            "lucky_task": self._get_lucky_task(card),
            "reminder": self._get_reminder(card),
            "fortune": fortune
        }
