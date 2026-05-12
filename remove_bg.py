from rembg import remove
from PIL import Image

def process_image(input_path, output_path):
    print(f"Processing {input_path}...")
    try:
        input_image = Image.open(input_path)
        output_image = remove(input_image)
        output_image.save(output_path, "PNG")
        print(f"Saved to {output_path}")
    except Exception as e:
        print(f"Failed to process {input_path}: {e}")

base_dir = "C:/Users/jiayinglin/Desktop/SHUIMUMUU-Tarot-Backend/static/images"
healing = f"{base_dir}/healing_cute_child.png"
punching = f"{base_dir}/punching_villain_doll.png"

process_image(healing, healing)
process_image(punching, punching)
