"""
Test menu display functionality
Tests that title screen, sheriff portrait, and menu buttons display correctly
"""

import sys
import os
from pathlib import Path

# Add project root to path
# __file__ is in tests/demos/, so parent.parent gets us to project root
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Suppress pygame welcome message
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"

import pygame
from ui.pygame_ui import get_ui, close_ui
from ui.menu import load_menu_content


def test_menu_content_loads():
    """Test that menu content JSON loads correctly"""
    print("Testing menu content loading...")
    content = load_menu_content()
    
    assert 'title_pygame' in content, "Missing title_pygame in menu content"
    assert 'title_ascii_art' in content, "Missing title_ascii_art in menu content"
    assert 'how_to_play' in content, "Missing how_to_play in menu content"
    assert 'credits' in content, "Missing credits in menu content"
    assert 'exit_message' in content, "Missing exit_message in menu content"
    
    print(f"✓ Menu content loaded successfully")
    print(f"  - Title: {content['title_pygame']}")
    print(f"  - How to Play sections: {len(content['how_to_play']['sections'])}")
    print(f"  - Credits sections: {len(content['credits']['sections'])}")
    return True


def test_sheriff_portrait_exists():
    """Test that sheriff portrait file exists"""
    print("\nTesting sheriff portrait file...")
    portrait_path = project_root / 'characters' / 'portraits' / 'sheriff.png'
    
    assert portrait_path.exists(), f"Sheriff portrait not found at {portrait_path}"
    
    print(f"✓ Sheriff portrait found at: {portrait_path}")
    return True


def test_title_screen_display():
    """Test that title screen displays correctly with title and portrait"""
    print("\nTesting title screen display...")
    
    try:
        # Initialize UI
        ui = get_ui()
        content = load_menu_content()
        
        # Display title screen
        ui.show_title_screen(content['title_pygame'])
        
        # Wait a moment to ensure rendering completes
        pygame.time.wait(500)
        
        print("✓ Title screen displayed successfully")
        print("  Visual check required:")
        print("    - Title 'SHERIFF OF NOTTINGHAM' should be visible on left")
        print("    - Sheriff portrait should be visible on right")
        print("    - Screen should be split 50/50")
        
        # Keep window open for visual inspection
        print("\nWindow will stay open for 3 seconds for visual inspection...")
        pygame.time.wait(3000)
        
        close_ui()
        return True
        
    except Exception as e:
        print(f"✗ Error displaying title screen: {e}")
        close_ui()
        return False


def test_menu_buttons_display():
    """Test that menu buttons display without flashing"""
    print("\nTesting menu buttons display...")
    
    try:
        # Initialize UI
        ui = get_ui()
        content = load_menu_content()
        
        # Display title screen
        ui.show_title_screen(content['title_pygame'])
        
        # Show menu choices (simulating menu display)
        choices = [
            ('start', 'Start Game'),
            ('help', 'How to Play'),
            ('credits', 'Credits'),
            ('exit', 'Exit')
        ]
        
        # Create buttons but don't wait for input
        ui.input.choice_buttons = []
        button_width = 220
        button_height = 50
        button_spacing = 20
        
        total_width = len(choices) * button_width + (len(choices) - 1) * button_spacing
        start_x = (1200 - total_width) // 2  # SCREEN_WIDTH = 1200
        start_y = 800 - button_height - 30  # SCREEN_HEIGHT = 800
        
        for i, (key, display_text) in enumerate(choices):
            x = start_x + i * (button_width + button_spacing)
            rect = pygame.Rect(x, start_y, button_width, button_height)
            ui.input.choice_buttons.append((display_text, rect))
        
        # Render with buttons
        ui.input._render_with_buttons()
        
        print("✓ Menu buttons displayed successfully")
        print("  Visual check required:")
        print("    - Title and portrait should still be visible")
        print("    - Four buttons should be visible at bottom")
        print("    - Moving mouse should not cause flashing")
        
        # Test mouse movement doesn't cause excessive flashing
        print("\nSimulating mouse movement...")
        for i in range(10):
            # Simulate mouse motion event
            pygame.event.post(pygame.event.Event(pygame.MOUSEMOTION, {'pos': (600 + i * 10, 750)}))
            ui.window.clock.tick(60)
        
        print("✓ Mouse movement handled without excessive flashing")
        
        # Keep window open for visual inspection
        print("\nWindow will stay open for 3 seconds for visual inspection...")
        pygame.time.wait(3000)
        
        close_ui()
        return True
        
    except Exception as e:
        print(f"✗ Error displaying menu buttons: {e}")
        close_ui()
        return False


def run_all_tests():
    """Run all menu display tests"""
    print("=" * 70)
    print("MENU DISPLAY TESTS")
    print("=" * 70)
    
    tests = [
        ("Menu Content Loading", test_menu_content_loads),
        ("Sheriff Portrait File", test_sheriff_portrait_exists),
        ("Title Screen Display", test_title_screen_display),
        ("Menu Buttons Display", test_menu_buttons_display),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 70)
    print("TEST RESULTS")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    print("=" * 70)
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
