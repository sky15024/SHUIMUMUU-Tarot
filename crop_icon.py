"""裁切 PWA icon：移除外層圓角邊框，只保留內部 app icon 圖案"""
from PIL import Image
import sys

# 讀取原始圖片
src = r"C:\Users\AKA淡水水母王\.gemini\antigravity\brain\6d8ca2dd-cb4d-4f3a-956e-75928f163015\media__1778340688837.jpg"
img = Image.open(src)
w, h = img.size
print(f"原始尺寸: {w}x{h}")

# 圖片有灰色圓角邊框，需要裁切掉
# 從圖片分析，邊框大約佔整張圖的 3~4% 每邊
# 裁切掉外圍的灰色邊框
margin_ratio = 0.04  # 4% 邊距
margin_x = int(w * margin_ratio)
margin_y = int(h * margin_ratio)

# 裁切
cropped = img.crop((margin_x, margin_y, w - margin_x, h - margin_y))
print(f"裁切後尺寸: {cropped.size[0]}x{cropped.size[1]}")

# 輸出 512x512 PNG
icon_512 = cropped.resize((512, 512), Image.LANCZOS)
icon_512.save(r"c:\Users\AKA淡水水母王\Desktop\SHUIMUMUU-Tarot-Backend\static\images\pwa-icon-512.png", "PNG")
print("已儲存 pwa-icon-512.png (512x512)")

# 輸出 192x192 PNG
icon_192 = cropped.resize((192, 192), Image.LANCZOS)
icon_192.save(r"c:\Users\AKA淡水水母王\Desktop\SHUIMUMUU-Tarot-Backend\static\images\pwa-icon-192.png", "PNG")
print("已儲存 pwa-icon-192.png (192x192)")

print("完成！")
