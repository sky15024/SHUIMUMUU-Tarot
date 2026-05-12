import os

css_path = 'c:/Users/AKA淡水水母王/Desktop/SHUIMUMUU-Tarot-Backend/static/css/style.css'
with open(css_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

responsive_idx = -1
ads_idx = -1

for i, line in enumerate(lines):
    if '/* --- Responsive --- */' in line:
        responsive_idx = i
    if '/* ========== 廣告側邊欄 ==========' in line:
        ads_idx = i

if responsive_idx != -1 and ads_idx != -1 and ads_idx > responsive_idx:
    base_css = lines[:responsive_idx]
    responsive_css = lines[responsive_idx:ads_idx]
    late_base_css = lines[ads_idx:]
    
    new_lines = base_css + late_base_css + ['\n\n'] + responsive_css
    
    with open(css_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print("Fixed CSS cascade order.")
else:
    print(f"Could not find indices: responsive_idx={responsive_idx}, ads_idx={ads_idx}")
