import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('data/tarot_cards.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)

short = [c for c in cards if len(c.get('upright_meaning', '')) < 100]
print(f"總牌數: {len(cards)}")
print(f"需要補齊詳細牌義的牌數: {len(short)}")
print("---")
for c in short:
    print(f"  [{c['id']}] {c['name_zh']} ({c['name_en']}) - 正位 {len(c.get('upright_meaning',''))} 字 / 逆位 {len(c.get('reversed_meaning',''))} 字")
