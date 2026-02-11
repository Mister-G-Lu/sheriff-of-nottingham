"""
Game menu and intro screen with ASCII art and image display.

DEVELOPER NOTE:
===============
DO NOT add large blocks of hardcoded text to this file!
All menu content (instructions, credits, ASCII art, etc.) should be stored in:
    data/menu_content.json

This keeps the code clean and makes content easy to edit without touching Python code.
To add or modify menu content:
1. Edit data/menu_content.json
2. Use load_menu_content() to load the content
3. Display it using the appropriate function

Keep this file focused on menu logic and display functions, not content storage.
"""

import sys
import json
from pathlib import Path

# Check if we're using Pygame UI
try:
    from ui.pygame_ui import get_ui
    USING_PYGAME = True
except ImportError:
    USING_PYGAME = False


def load_menu_content():
    """Load all menu content from JSON file."""
    menu_file = Path(__file__).parent.parent / "data" / "menu_content.json"
    try:
        with open(menu_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # Fallback if file not found
        return {
            'title_pygame': 'SHERIFF OF NOTTINGHAM',
            'how_to_play': {'header': 'HOW TO PLAY', 'sections': [], 'footer': ''},
            'credits': {'header': 'CREDITS', 'sections': [], 'footer': ''},
            'exit_message': 'Thanks for playing!'
        }


def display_sheriff_image():
    """Display the sheriff.png image as ASCII art."""
    try:
        from PIL import Image
        
        # Load sheriff image
        sheriff_path = Path(__file__).parent.parent / "characters" / "sheriff.png"
        
        if not sheriff_path.exists():
            return  # Skip if image not found
        
        with Image.open(sheriff_path) as img:
            # Resize for terminal display
            img.thumbnail((80, 40))
            
            # Convert to ASCII
            ascii_art = image_to_ascii(img, width=80)
            print(ascii_art)
            
    except ImportError:
        # PIL not available, skip image
        pass
    except Exception:
        # Any other error, skip image
        pass


def image_to_ascii(image, width=80):
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


def show_title_card():
    """Display the game title card with ASCII art."""
    content = load_menu_content()
    
    if USING_PYGAME:
        # In Pygame mode, show split screen: title on left, sheriff portrait on right
        ui = get_ui()
        ui.show_title_screen(content['title_pygame'])
    else:
        # Terminal mode - show full ASCII art
        print(content['title_ascii_art'], end='')
        
        # Display sheriff image with minimal spacing
        print()  # Single newline
        display_sheriff_image()
        print()  # Single newline after image


def show_main_menu():
    """Display the main menu and get player choice."""
    if USING_PYGAME:
        # Use Pygame choice buttons (title screen already displayed)
        ui = get_ui()
        choices = [
            ('start', 'Start Game'),
            ('help', 'How to Play'),
            ('credits', 'Credits'),
            ('exit', 'Exit')
        ]
        return ui.show_choices("", choices)
    else:
        # Terminal mode - use text input
        print("    [1] Start Game")
        print("    [2] How to Play")
        print("    [3] Credits")
        print("    [4] Exit")
        print()
        
        while True:
            choice = input("Enter your choice [1-4]: ").strip()
            
            if choice == '1':
                return 'start'
            elif choice == '2':
                return 'help'
            elif choice == '3':
                return 'credits'
            elif choice == '4':
                return 'exit'
            else:
                print("Invalid choice. Please enter 1, 2, 3, or 4.")


def show_how_to_play():
    """Display how to play instructions."""
    content = load_menu_content()
    how_to_play = content['how_to_play']
    
    # Build the instructions text from JSON data
    instructions = f"\n{how_to_play['header']}\n\n"
    
    for section in how_to_play['sections']:
        instructions += f"{section['title']}\n"
        instructions += f"   {section['content']}\n\n"
    
    instructions += f"{how_to_play['footer']}\n"
    
    print(instructions)
    input()


def show_credits():
    """Display game credits."""
    content = load_menu_content()
    credits_data = content['credits']
    
    # Build the credits text from JSON data
    credits = f"\n{credits_data['header']}\n\n"
    credits += f"    {credits_data['title']}\n\n"
    
    for section in credits_data['sections']:
        credits += f"    {section['title']}\n"
        credits += f"       {section['content']}\n\n"
    
    credits += f"    {credits_data['version']}\n    \n"
    credits += f"{credits_data['footer']}\n"
    
    print(credits)
    input()


def run_menu():
    """Run the main menu loop."""
    import os
    
    while True:
        # Clear screen
        if USING_PYGAME:
            ui = get_ui()
            ui.clear_text()
        else:
            os.system('clear' if os.name != 'nt' else 'cls')
        
        # Show title card
        show_title_card()
        
        # Show menu and get choice
        choice = show_main_menu()
        
        if choice == 'start':
            return True  # Start the game
        elif choice == 'help':
            show_how_to_play()
        elif choice == 'credits':
            show_credits()
        elif choice == 'exit':
            content = load_menu_content()
            print(content['exit_message'])
            return False  # Exit the game
