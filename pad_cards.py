import os
import shutil
from PIL import Image, ImageFilter, ImageEnhance

cards_dir = r"C:\Users\jiayinglin\Desktop\SHUIMUMUU-Tarot-Backend\static\images\cards"
backup_dir = r"C:\Users\jiayinglin\Desktop\SHUIMUMUU-Tarot-Backend\static\images\cards_backup"

if not os.path.exists(backup_dir):
    os.makedirs(backup_dir)

images = [f for f in os.listdir(cards_dir) if f.startswith('major_') and f.endswith('.png')]

target_width = 1024
target_height = 1756 # approx 7:12 ratio

count = 0
for img_name in images:
    img_path = os.path.join(cards_dir, img_name)
    backup_path = os.path.join(backup_dir, img_name)
    
    # Backup first
    if not os.path.exists(backup_path):
        shutil.copy2(img_path, backup_path)
    
    with Image.open(backup_path) as img:
        # Some images might already be processed if this is re-run, so check size
        if img.size[1] == target_height:
            print(f"Skipping {img_name}, already processed.")
            continue
            
        img = img.convert('RGB')
        
        # 1. Create blurred background
        bg = img.copy()
        # Scale up to fill height, maybe stretch a little but blur will hide it
        bg = bg.resize((target_width, target_height), Image.Resampling.LANCZOS)
        
        # Darken the background slightly so the main card pops
        enhancer = ImageEnhance.Brightness(bg)
        bg = enhancer.enhance(0.4)  # Darken to 40%
        
        # Blur heavily
        bg = bg.filter(ImageFilter.GaussianBlur(radius=45))
        
        # 2. Paste the original in the center
        paste_y = (target_height - 1024) // 2
        bg.paste(img, (0, paste_y))
        
        # Save it
        bg.save(img_path, format="PNG")
        print(f"Processed {img_name}")
        count += 1

print(f"All done! Successfully converted {count} images.")
