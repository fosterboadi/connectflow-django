"""
Generate PWA icons for ConnectFlow Pro
Run this script to create placeholder icons
"""
from PIL import Image, ImageDraw, ImageFont
import os

# Icon sizes needed for PWA
SIZES = [72, 96, 128, 144, 152, 192, 384, 512]

# Colors
BG_COLOR = (79, 70, 229)  # Indigo-600
TEXT_COLOR = (255, 255, 255)  # White

def create_icon(size):
    """Create a simple icon with CF text"""
    img = Image.new('RGB', (size, size), color=BG_COLOR)
    draw = ImageDraw.Draw(img)
    
    # Try to use a font, fallback to default
    try:
        font_size = int(size * 0.4)
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    # Draw "CF" text (ConnectFlow)
    text = "CF"
    
    # Get text bounding box
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Center the text
    x = (size - text_width) / 2
    y = (size - text_height) / 2
    
    draw.text((x, y), text, fill=TEXT_COLOR, font=font)
    
    return img

def main():
    """Generate all icon sizes"""
    # Get the icons directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    icons_dir = os.path.join(script_dir, 'static', 'icons')
    
    # Create directory if it doesn't exist
    os.makedirs(icons_dir, exist_ok=True)
    
    print("🎨 Generating PWA icons...")
    
    for size in SIZES:
        icon = create_icon(size)
        filename = f'icon-{size}x{size}.png'
        filepath = os.path.join(icons_dir, filename)
        icon.save(filepath)
        print(f"✅ Created {filename}")
    
    print(f"\n🎉 All icons generated in: {icons_dir}")
    print("\n📝 Note: These are placeholder icons.")
    print("   Replace them with your custom logo for production!")

if __name__ == '__main__':
    main()
