"""
整合塔羅小牌圖片到牌堆中
- 將「塔羅小牌OK版」中的 56 張小牌圖片複製並重新命名到 static/images/cards/
- 更新 tarot_cards.json 中所有小牌的 image 欄位
"""

import json
import shutil
import sys
from pathlib import Path

# 強制 UTF-8 輸出
sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = Path(__file__).parent
SOURCE_DIR = BASE_DIR / "static" / "images" / "塔羅小牌OK版"
TARGET_DIR = BASE_DIR / "static" / "images" / "cards"
JSON_PATH = BASE_DIR / "data" / "tarot_cards.json"

MINOR_CARD_MAP = {
    "權杖1_clean.png":    "minor_wands_01_ace.png",
    "權杖2_clean.png":    "minor_wands_02.png",
    "權杖3_clean.png":    "minor_wands_03.png",
    "權杖4_clean.png":    "minor_wands_04.png",
    "權杖5_clean.png":    "minor_wands_05.png",
    "權杖6_clean.png":    "minor_wands_06.png",
    "權杖7_clean.png":    "minor_wands_07.png",
    "權杖8_clean.png":    "minor_wands_08.png",
    "權杖9_clean.png":    "minor_wands_09.png",
    "權杖10_clean.png":   "minor_wands_10.png",
    "權杖侍者_clean.png": "minor_wands_11_page.png",
    "權杖騎士_clean.png": "minor_wands_12_knight.png",
    "權杖皇后_clean.png": "minor_wands_13_queen.png",
    "權杖國王_clean.png": "minor_wands_14_king.png",
    "聖杯1_clean.png":    "minor_cups_01_ace.png",
    "聖杯2_clean.png":    "minor_cups_02.png",
    "聖杯3_clean.png":    "minor_cups_03.png",
    "聖杯4_clean.png":    "minor_cups_04.png",
    "聖杯5_clean.png":    "minor_cups_05.png",
    "聖杯6_clean.png":    "minor_cups_06.png",
    "聖杯7_clean.png":    "minor_cups_07.png",
    "聖杯8_clean.png":    "minor_cups_08.png",
    "聖杯9_clean.png":    "minor_cups_09.png",
    "聖杯10_clean.png":   "minor_cups_10.png",
    "聖杯侍者_clean.png": "minor_cups_11_page.png",
    "聖杯騎士_clean.png": "minor_cups_12_knight.png",
    "聖杯皇后_clean.png": "minor_cups_13_queen.png",
    "聖杯國王_clean.png": "minor_cups_14_king.png",
    "寶劍1_clean.png":    "minor_swords_01_ace.png",
    "寶劍2_clean.png":    "minor_swords_02.png",
    "寶劍3_clean.png":    "minor_swords_03.png",
    "寶劍4_clean.png":    "minor_swords_04.png",
    "寶劍5_clean.png":    "minor_swords_05.png",
    "寶劍6_clean.png":    "minor_swords_06.png",
    "寶劍7_clean.png":    "minor_swords_07.png",
    "寶劍8_clean.png":    "minor_swords_08.png",
    "寶劍9_clean.png":    "minor_swords_09.png",
    "寶劍10_clean.png":   "minor_swords_10.png",
    "寶劍侍者_clean.png": "minor_swords_11_page.png",
    "寶劍騎士_clean.png": "minor_swords_12_knight.png",
    "寶劍皇后_clean.png": "minor_swords_13_queen.png",
    "寶劍國王_clean.png": "minor_swords_14_king.png",
    "金幣1_clean.png":    "minor_pentacles_01_ace.png",
    "金幣2_clean.png":    "minor_pentacles_02.png",
    "金幣3_clean.png":    "minor_pentacles_03.png",
    "金幣4_clean.png":    "minor_pentacles_04.png",
    "金幣5_clean.png":    "minor_pentacles_05.png",
    "金幣6_clean.png":    "minor_pentacles_06.png",
    "金幣7_clean.png":    "minor_pentacles_07.png",
    "金幣8_clean.png":    "minor_pentacles_08.png",
    "金幣9_clean.png":    "minor_pentacles_09.png",
    "金幣10_clean.png":   "minor_pentacles_10.png",
    "金幣侍者_clean.png": "minor_pentacles_11_page.png",
    "金幣騎士_clean.png": "minor_pentacles_12_knight.png",
    "金幣皇后_clean.png": "minor_pentacles_13_queen.png",
    "金幣國王_clean.png": "minor_pentacles_14_king.png",
}

NAME_EN_TO_FILENAME = {
    "Ace of Wands":    "minor_wands_01_ace.png",
    "Two of Wands":    "minor_wands_02.png",
    "Three of Wands":  "minor_wands_03.png",
    "Four of Wands":   "minor_wands_04.png",
    "Five of Wands":   "minor_wands_05.png",
    "Six of Wands":    "minor_wands_06.png",
    "Seven of Wands":  "minor_wands_07.png",
    "Eight of Wands":  "minor_wands_08.png",
    "Nine of Wands":   "minor_wands_09.png",
    "Ten of Wands":    "minor_wands_10.png",
    "Page of Wands":   "minor_wands_11_page.png",
    "Knight of Wands": "minor_wands_12_knight.png",
    "Queen of Wands":  "minor_wands_13_queen.png",
    "King of Wands":   "minor_wands_14_king.png",
    "Ace of Cups":     "minor_cups_01_ace.png",
    "Two of Cups":     "minor_cups_02.png",
    "Three of Cups":   "minor_cups_03.png",
    "Four of Cups":    "minor_cups_04.png",
    "Five of Cups":    "minor_cups_05.png",
    "Six of Cups":     "minor_cups_06.png",
    "Seven of Cups":   "minor_cups_07.png",
    "Eight of Cups":   "minor_cups_08.png",
    "Nine of Cups":    "minor_cups_09.png",
    "Ten of Cups":     "minor_cups_10.png",
    "Page of Cups":    "minor_cups_11_page.png",
    "Knight of Cups":  "minor_cups_12_knight.png",
    "Queen of Cups":   "minor_cups_13_queen.png",
    "King of Cups":    "minor_cups_14_king.png",
    "Ace of Swords":     "minor_swords_01_ace.png",
    "Two of Swords":     "minor_swords_02.png",
    "Three of Swords":   "minor_swords_03.png",
    "Four of Swords":    "minor_swords_04.png",
    "Five of Swords":    "minor_swords_05.png",
    "Six of Swords":     "minor_swords_06.png",
    "Seven of Swords":   "minor_swords_07.png",
    "Eight of Swords":   "minor_swords_08.png",
    "Nine of Swords":    "minor_swords_09.png",
    "Ten of Swords":     "minor_swords_10.png",
    "Page of Swords":    "minor_swords_11_page.png",
    "Knight of Swords":  "minor_swords_12_knight.png",
    "Queen of Swords":   "minor_swords_13_queen.png",
    "King of Swords":    "minor_swords_14_king.png",
    "Ace of Pentacles":     "minor_pentacles_01_ace.png",
    "Two of Pentacles":     "minor_pentacles_02.png",
    "Three of Pentacles":   "minor_pentacles_03.png",
    "Four of Pentacles":    "minor_pentacles_04.png",
    "Five of Pentacles":    "minor_pentacles_05.png",
    "Six of Pentacles":     "minor_pentacles_06.png",
    "Seven of Pentacles":   "minor_pentacles_07.png",
    "Eight of Pentacles":   "minor_pentacles_08.png",
    "Nine of Pentacles":    "minor_pentacles_09.png",
    "Ten of Pentacles":     "minor_pentacles_10.png",
    "Page of Pentacles":    "minor_pentacles_11_page.png",
    "Knight of Pentacles":  "minor_pentacles_12_knight.png",
    "Queen of Pentacles":   "minor_pentacles_13_queen.png",
    "King of Pentacles":    "minor_pentacles_14_king.png",
}


def main():
    print("=" * 50)
    print("Step 1: 複製小牌圖片到 cards 目錄")
    print("=" * 50)

    copied = 0
    missing = []
    for zh_name, en_name in MINOR_CARD_MAP.items():
        src = SOURCE_DIR / zh_name
        dst = TARGET_DIR / en_name
        if not src.exists():
            missing.append(zh_name)
            print(f"  [MISS] 找不到: {zh_name}")
            continue
        shutil.copy2(src, dst)
        copied += 1
        print(f"  [OK] {zh_name} -> {en_name}")

    print(f"\n複製完成: {copied}/56")
    if missing:
        print(f"  缺少 {len(missing)} 張: {missing}")

    print("\n" + "=" * 50)
    print("Step 2: 更新 tarot_cards.json")
    print("=" * 50)

    with open(JSON_PATH, "r", encoding="utf-8") as f:
        cards = json.load(f)

    updated = 0
    for card in cards:
        if card["arcana"] == "minor" and card["image"] is None:
            filename = NAME_EN_TO_FILENAME.get(card["name_en"])
            if filename:
                card["image"] = f"images/cards/{filename}"
                updated += 1
                print(f"  [OK] {card['name_zh']} -> {card['image']}")
            else:
                print(f"  [MISS] 找不到對照: {card['name_en']}")

    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(cards, f, ensure_ascii=False, indent=2)

    print(f"\n更新完成: {updated}/56")

    print("\n" + "=" * 50)
    print("Step 3: 最終驗證")
    print("=" * 50)

    total = len(cards)
    major = [c for c in cards if c["arcana"] == "major"]
    minor = [c for c in cards if c["arcana"] == "minor"]
    has_image = [c for c in cards if c.get("image")]
    no_image = [c for c in cards if not c.get("image")]

    print(f"  總牌數: {total}")
    print(f"  大阿爾克那: {len(major)}")
    print(f"  小阿爾克那: {len(minor)}")
    print(f"  有圖片: {len(has_image)}")
    print(f"  無圖片: {len(no_image)}")

    card_files = list(TARGET_DIR.glob("*.png"))
    print(f"  cards 目錄圖片數: {len(card_files)}")
    print(f"    大牌 (major_*): {len([f for f in card_files if f.name.startswith('major_')])}")
    print(f"    小牌 (minor_*): {len([f for f in card_files if f.name.startswith('minor_')])}")

    if total == 78 and len(has_image) == 78:
        print("\n>>> 完美! 78 張塔羅牌全部整合完成!")
    else:
        print(f"\n>>> 還有 {len(no_image)} 張牌缺少圖片")


if __name__ == "__main__":
    main()
