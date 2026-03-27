from PIL import Image
from rembg import remove
import io

def create_transparent_icon(input_path, output_path):
    # 1. Load image
    with open(input_path, "rb") as f:
        input_data = f.read()

    # 2. Remove background using rembg
    output_data = remove(input_data)
    img = Image.open(io.BytesIO(output_data)).convert("RGBA")

    # 3. Get bounding box of non-transparent pixels and crop
    # This automatically removes the padding making the icon larger in the frame
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)
        
    # 4. Save as multi-size ICO
    icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    img.save(output_path, format="ICO", sizes=icon_sizes)
    print(f"Successfully processed icon -> {output_path}")

input_img = r"C:\Users\user\.gemini\antigravity\brain\5586816f-1007-4f91-81ad-671ff1e2f20d\app_icon_base_1773796379836.png"
output_ico = r"C:\Users\user\Project\folder-organizer\app_icon.ico"

if __name__ == "__main__":
    create_transparent_icon(input_img, output_ico)
