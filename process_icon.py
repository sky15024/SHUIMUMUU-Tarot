import sys
from PIL import Image

def analyze_and_crop(image_path):
    img = Image.open(image_path)
    print(f"Original size: {img.size}, mode: {img.mode}")
    
    # If image has alpha channel, try to get bounding box
    if 'A' in img.mode:
        bbox = img.getbbox()
        if bbox:
            print(f"Bounding box (non-transparent): {bbox}")
            img = img.crop(bbox)
            print(f"Size after crop to bbox: {img.size}")
    else:
        # Try to find bounding box by converting to grayscale and finding non-background
        bg = Image.new(img.mode, img.size, img.getpixel((0,0)))
        diff = Image.composite(img, bg, img.convert('L').point(lambda x: 255 if x else 0, mode='1'))
        bbox = diff.getbbox()
        if bbox:
            print(f"Bounding box (difference from top-left pixel): {bbox}")
            # If the bounding box is too close to the edge, it might not be a solid background.
            # We won't crop blindly here, just print it.
    
    # Make it square by adding padding or cropping
    w, h = img.size
    size = max(w, h)
    
    # Actually, if the user wants "APP ICON大小", maybe it's just a square in the center?
    # Let's crop the center square.
    if w != h:
        min_dim = min(w, h)
        left = (w - min_dim) / 2
        top = (h - min_dim) / 2
        right = (w + min_dim) / 2
        bottom = (h + min_dim) / 2
        img = img.crop((left, top, right, bottom))
        print(f"Cropped to center square: {img.size}")
    
    # Resize to 512x512
    icon_512 = img.resize((512, 512), Image.Resampling.LANCZOS)
    icon_512.save("static/images/pwa-icon-512.png", "PNG")
    print("Saved pwa-icon-512.png")

if __name__ == "__main__":
    analyze_and_crop("static/images/PWA-ICON.png")
