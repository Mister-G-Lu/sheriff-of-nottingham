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
from ui.pygame_ui import get_ui


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


def show_title_card():
    """Display the game title card."""
    content = load_menu_content()
    ui = get_ui()
    # Show split screen: title on left, sheriff portrait on right
    ui.show_title_screen(content['title_pygame'])


def show_main_menu():
    """Display the main menu and get player choice."""
    ui = get_ui()
    choices = [
        ('start', 'Start Game'),
        ('help', 'How to Play'),
        ('credits', 'Credits'),
        ('exit', 'Exit')
    ]
    return ui.show_choices("", choices)


def show_how_to_play():
    """Display how to play instructions."""
    content = load_menu_content()
    how_to_play = content['how_to_play']
    ui = get_ui()
    
    # Clear screen and display header
    ui.clear_text()
    ui.display_text(how_to_play['header'], clear_previous=False)
    ui.display_text("", clear_previous=False)  # Empty line
    
    # Display each section
    for section in how_to_play['sections']:
        ui.display_text(section['title'], clear_previous=False)
        # Split multi-line content
        for line in section['content'].split('\n'):
            ui.display_text(f"   {line}", clear_previous=False)
        ui.display_text("", clear_previous=False)  # Empty line between sections
    
    # Display footer and wait for input
    ui.display_text(how_to_play['footer'], clear_previous=False)
    input()


def show_credits():
    """Display game credits."""
    content = load_menu_content()
    credits_data = content['credits']
    ui = get_ui()
    
    # Clear screen and display header
    ui.clear_text()
    ui.display_text(credits_data['header'], clear_previous=False)
    ui.display_text("", clear_previous=False)  # Empty line
    
    # Display title
    for line in credits_data['title'].split('\n'):
        ui.display_text(f"    {line}", clear_previous=False)
    ui.display_text("", clear_previous=False)  # Empty line
    
    # Display each section
    for section in credits_data['sections']:
        ui.display_text(f"    {section['title']}", clear_previous=False)
        # Split multi-line content
        for line in section['content'].split('\n'):
            ui.display_text(f"       {line}", clear_previous=False)
        ui.display_text("", clear_previous=False)  # Empty line between sections
    
    # Display version and footer
    ui.display_text(f"    {credits_data['version']}", clear_previous=False)
    ui.display_text("", clear_previous=False)
    ui.display_text(credits_data['footer'], clear_previous=False)
    input()


def run_menu():
    """Run the main menu loop."""
    ui = get_ui()
    
    while True:
        # Clear screen
        ui.clear_text()
        
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
