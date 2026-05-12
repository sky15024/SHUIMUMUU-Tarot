import json
import os

def get_keywords(card, is_reversed):
    """取得牌的關鍵字，如果不足 4 個則用備用詞語補齊"""
    key = 'reversed_keywords' if is_reversed else 'upright_keywords'
    keywords = card.get(key, [])
    
    # 溫暖正向的備用詞彙
    fallback_pos = ["希望", "愛", "平靜", "力量", "成長", "喜悅", "溫柔", "包容"]
    # 逆位時，轉換成溫暖視角的詞彙
    fallback_rev = ["自我照顧", "沉澱", "內在力量", "釋放", "理解", "耐心", "轉化", "療癒"]
    
    fallbacks = fallback_rev if is_reversed else fallback_pos
    
    # 確保至少有 4 個詞可以用
    result = list(keywords)
    for word in fallbacks:
        if len(result) >= 4:
            break
        if word not in result:
            result.append(word)
            
    return result[0], result[1], result[2], result[3]

def generate_warm_fortunes(card, is_reversed):
    """根據牌的特性生成溫暖療癒的運勢短評"""
    k1, k2, k3, k4 = get_keywords(card, is_reversed)
    name = card['name_zh']
    
    if not is_reversed:
        overall = f"宇宙今天為你注入了「{name}」的閃耀能量！這是一個充滿契機的日子，請放心展開你的{k2}之旅，宇宙會溫柔地支持著你。"
        love = f"在人際與感情中，展現你真實的特質，將為你帶來充滿{k3}與喜悅的溫暖交流。"
        work = f"工作與學習上，帶著{k4}的信心前進吧！你所散發的「{k1}」光芒會讓你事半功倍。"
        money = f"保持敞開與感恩的心，順著美好的流動，宇宙的豐盛會自然而然地來到你身邊。"
    else:
        # 逆位：更強調向內看、自我療癒與放慢腳步
        overall = f"今天或許會面臨一些關於「{k1}」的感受。請溫柔地擁抱這樣的情緒，這正是宇宙在提醒你停下腳步，找回內在的平靜與{k2}。"
        love = f"在感情互動中，如果感到有些迷惘，請先給自己一個深深的擁抱。用愛與理解取代批判，溫暖自然會回歸。"
        work = f"工作上若遇到卡關，這是在引導你釋放過度的壓力。允許自己慢慢來，你的價值並不會因此減少。"
        money = f"財務上適合回歸保守與穩定。把焦點放回照顧自己的身心，外在的豐盛會在你準備好時平靜地流向你。"

    return {
        "overall": overall,
        "love": love,
        "work": work,
        "money": money
    }

def main():
    # 確保讀取路徑正確
    input_path = os.path.join('data', 'tarot_cards.json')
    output_path = os.path.join('data', 'tarot_fortunes.json')
    
    with open(input_path, 'r', encoding='utf-8') as f:
        cards = json.load(f)

    fortunes_db = {}
    
    for card in cards:
        card_id = str(card['id'])
        fortunes_db[card_id] = {
            "upright": generate_warm_fortunes(card, False),
            "reversed": generate_warm_fortunes(card, True)
        }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(fortunes_db, f, ensure_ascii=False, indent=2)

    print(f"成功生成 624 則溫暖療癒的運勢短評！")
    print(f"檔案已儲存至：{output_path}")

if __name__ == "__main__":
    main()
