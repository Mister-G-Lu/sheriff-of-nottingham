"""
Test script to display merchant PNG images in the terminal.

This script tests displaying the trader.png image for Benedict the Trader.
It tries multiple methods to display images in the terminal.

Run from project root:
    python test_image_display.py
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from core.players.merchants import load_merchants


def display_image_with_pil(image_path: Path, max_width: int = 100, max_height: int = 100):
    """Display image using PIL/Pillow with terminal-compatible methods."""
    try:
        from PIL import Image
        import io
        
        print(f"\n{'='*70}")
        print(f"METHOD 1: PIL/Pillow Image Display")
        print(f"{'='*70}")
        
        # Load and resize image
        with Image.open(image_path) as img:
            print(f"Original size: {img.size[0]}x{img.size[1]} pixels")
            
            # Create thumbnail (maintains aspect ratio)
            img.thumbnail((max_width, max_height))
            print(f"Thumbnail size: {img.size[0]}x{img.size[1]} pixels")
            
            # Try to display using different methods
            
            # Method 1a: ASCII art representation
            print("\n--- ASCII Representation ---")
            ascii_art = image_to_ascii(img, width=60)
            print(ascii_art)
            
            # Method 1b: Show image info
            print(f"\n--- Image Info ---")
            print(f"Format: {img.format}")
            print(f"Mode: {img.mode}")
            print(f"Size: {img.size}")
            
            return True
            
    except ImportError:
        print("❌ PIL/Pillow not installed. Install with: pip install Pillow")
        return False
    except Exception as e:
        print(f"❌ Error displaying image: {e}")
        return False


def image_to_ascii(image, width=60):
    """Convert PIL Image to ASCII art."""
    # ASCII characters from darkest to lightest
    ascii_chars = ['@', '#', 'S', '%', '?', '*', '+', ';', ':', ',', '.', ' ']
    
    # Resize image to fit width while maintaining aspect ratio
    aspect_ratio = image.height / image.width
    height = int(width * aspect_ratio * 0.55)  # 0.55 to account for character height
    image = image.resize((width, height))
    
    # Convert to grayscale
    image = image.convert('L')
    
    # Convert pixels to ASCII
    pixels = image.getdata()
    ascii_str = ''
    for i, pixel in enumerate(pixels):
        # Map pixel value (0-255) to ASCII character
        ascii_str += ascii_chars[pixel // 25]
        if (i + 1) % width == 0:
            ascii_str += '\n'
    
    return ascii_str


def display_image_with_iterm2(image_path: Path):
    """Display image using iTerm2 inline image protocol (Mac only)."""
    try:
        import base64
        from PIL import Image
        import io
        
        print(f"\n{'='*70}")
        print(f"METHOD 2: iTerm2 Inline Image Protocol")
        print(f"{'='*70}")
        
        # Check if running in iTerm2
        term_program = os.environ.get('TERM_PROGRAM', '')
        if term_program != 'iTerm.app':
            print(f"⚠️  Not running in iTerm2 (detected: {term_program or 'unknown terminal'})")
            print("This method only works in iTerm2 on macOS")
            return False
        
        # Load and resize image
        with Image.open(image_path) as img:
            img.thumbnail((100, 100))
            
            # Convert to PNG bytes
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            img_bytes = buffer.getvalue()
            
            # Encode to base64
            img_base64 = base64.b64encode(img_bytes).decode('utf-8')
            
            # iTerm2 inline image escape sequence
            print(f"\033]1337;File=inline=1;width=100px;height=100px:{img_base64}\a")
            print("\n✅ Image displayed above (if in iTerm2)")
            
            return True
            
    except ImportError:
        print("❌ PIL/Pillow not installed")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def display_image_with_sixel(image_path: Path):
    """Display image using Sixel graphics protocol."""
    try:
        print(f"\n{'='*70}")
        print(f"METHOD 3: Sixel Graphics Protocol")
        print(f"{'='*70}")
        
        # Check if terminal supports sixel
        import subprocess
        result = subprocess.run(['tput', 'colors'], capture_output=True, text=True)
        
        print("⚠️  Sixel support requires a compatible terminal (xterm, mlterm, etc.)")
        print("Most modern terminals don't support Sixel by default")
        
        # Try using img2sixel if available
        try:
            result = subprocess.run(
                ['img2sixel', '-w', '100', '-h', '100', str(image_path)],
                capture_output=True,
                timeout=5
            )
            if result.returncode == 0:
                print(result.stdout.decode())
                print("\n✅ Image displayed using Sixel")
                return True
            else:
                print("❌ img2sixel failed or not installed")
                return False
        except FileNotFoundError:
            print("❌ img2sixel not found. Install with: brew install libsixel")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def display_image_kitty(image_path: Path):
    """Display image using Kitty terminal graphics protocol."""
    try:
        import base64
        import os
        
        print(f"\n{'='*70}")
        print(f"METHOD 4: Kitty Terminal Graphics Protocol")
        print(f"{'='*70}")
        
        # Check if running in Kitty
        term = os.environ.get('TERM', '')
        if 'kitty' not in term.lower():
            print(f"⚠️  Not running in Kitty terminal (detected: {term})")
            print("This method only works in Kitty terminal")
            return False
        
        # Read image file
        with open(image_path, 'rb') as f:
            img_data = f.read()
        
        # Encode to base64
        img_base64 = base64.b64encode(img_data).decode('utf-8')
        
        # Kitty graphics protocol
        print(f"\033_Gf=100,a=T,t=f;{img_base64}\033\\")
        print("\n✅ Image displayed above (if in Kitty terminal)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_benedict_image():
    """Test displaying Benedict the Trader's image."""
    print("\n" + "="*70)
    print("BENEDICT THE TRADER - IMAGE DISPLAY TEST")
    print("="*70)
    
    # Find Benedict's merchant data
    merchants = load_merchants()
    benedict = next((m for m in merchants if m.id == "BenedictTrader"), None)
    
    if not benedict:
        print("❌ Benedict the Trader not found in merchants")
        return
    
    print(f"\n✅ Found merchant: {benedict.name}")
    print(f"Portrait file: {benedict.portrait_file}")
    
    # Locate the image file
    characters_dir = Path(__file__).parent / "characters"
    image_path = characters_dir / benedict.portrait_file
    
    if not image_path.exists():
        print(f"❌ Image file not found: {image_path}")
        return
    
    print(f"✅ Image file found: {image_path}")
    print(f"File size: {image_path.stat().st_size} bytes")
    
    # Try different display methods
    import os
    
    # Method 1: PIL with ASCII art (works everywhere)
    success1 = display_image_with_pil(image_path, max_width=100, max_height=100)
    
    # Method 2: iTerm2 (Mac only)
    if sys.platform == 'darwin':
        success2 = display_image_with_iterm2(image_path)
    
    # Method 3: Sixel (requires compatible terminal)
    # Commented out by default as it's rarely supported
    # success3 = display_image_with_sixel(image_path)
    
    # Method 4: Kitty terminal
    # success4 = display_image_kitty(image_path)
    
    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    print("""
✅ ASCII Art Method: Works in all terminals (shown above)
   - Converts image to text characters
   - Best compatibility
   - Lower quality but always works

⚠️  iTerm2 Method: Only works in iTerm2 on macOS
   - High quality image display
   - Requires iTerm2 terminal

⚠️  Sixel Method: Requires sixel-compatible terminal
   - Rarely supported in modern terminals
   - Needs img2sixel tool

⚠️  Kitty Method: Only works in Kitty terminal
   - High quality image display
   - Requires Kitty terminal

RECOMMENDATION:
For best compatibility, use ASCII art portraits (.txt files) instead of PNG.
The current system loads ASCII portraits from .txt files in characters/
    """)
    
    print("\n💡 To create ASCII art portrait for Benedict:")
    print("   1. Create characters/benedict-trader.txt")
    print("   2. Add ASCII art (can use online converters)")
    print("   3. Update JSON: \"portrait_file\": \"benedict-trader.txt\"")
    print()


if __name__ == "__main__":
    test_benedict_image()
