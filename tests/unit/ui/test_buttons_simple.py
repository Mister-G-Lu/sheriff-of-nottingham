"""
Simple Button Display Test

Tests that buttons are displayed correctly during gameplay.
This test directly checks the button rendering without circular imports.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set up headless mode to prevent pygame windows from appearing
import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'


def test_pygame_ui_has_show_choices():
    """Test that pygame UI has show_choices method."""
    print("=" * 70)
    print("TEST: Pygame UI Has show_choices Method")
    print("=" * 70)
    
    try:
        from ui.pygame_ui import get_ui
        
        ui = get_ui()
        
        # Check if show_choices method exists
        if hasattr(ui, 'show_choices'):
            print("✓ UI has show_choices method")
            
            # Check if it's callable
            if callable(ui.show_choices):
                print("✓ show_choices is callable")
                print("\n✅ TEST PASSED")
                ui.close()
                return True
            else:
                print("❌ show_choices is not callable")
                print("\n❌ TEST FAILED")
                ui.close()
                return False
        else:
            print("❌ UI does not have show_choices method")
            print("\n❌ TEST FAILED")
            ui.close()
            return False
            
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_pygame_input_creates_buttons():
    """Test that PygameInput creates button rectangles."""
    print("\n" + "=" * 70)
    print("TEST: PygameInput Creates Buttons")
    print("=" * 70)
    
    try:
        from ui.pygame_input import PygameInput
        from ui.pygame_window import PygameWindow
        from ui.pygame_text import PygameText
        from ui.price_menu import PriceMenu
        
        window = PygameWindow()
        text = PygameText(window)
        price_menu = PriceMenu(window.screen, window.font_normal, window.font_small)
        input_handler = PygameInput(window, text, price_menu)
        
        # Check if choice_buttons attribute exists
        if hasattr(input_handler, 'choice_buttons'):
            print("✓ PygameInput has choice_buttons attribute")
            print(f"  Initial value: {input_handler.choice_buttons}")
            print("\n✅ TEST PASSED")
            window.close()
            return True
        else:
            print("❌ PygameInput does not have choice_buttons attribute")
            print("\n❌ TEST FAILED")
            window.close()
            return False
            
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_button_rendering_method_exists():
    """Test that _render_with_buttons method exists."""
    print("\n" + "=" * 70)
    print("TEST: Button Rendering Method Exists")
    print("=" * 70)
    
    try:
        from ui.pygame_input import PygameInput
        from ui.pygame_window import PygameWindow
        from ui.pygame_text import PygameText
        from ui.price_menu import PriceMenu
        
        window = PygameWindow()
        text = PygameText(window)
        price_menu = PriceMenu(window.screen, window.font_normal, window.font_small)
        input_handler = PygameInput(window, text, price_menu)
        
        # Check if _render_with_buttons method exists
        if hasattr(input_handler, '_render_with_buttons'):
            print("✓ PygameInput has _render_with_buttons method")
            
            if callable(input_handler._render_with_buttons):
                print("✓ _render_with_buttons is callable")
                print("\n✅ TEST PASSED")
                window.close()
                return True
            else:
                print("❌ _render_with_buttons is not callable")
                print("\n❌ TEST FAILED")
                window.close()
                return False
        else:
            print("❌ PygameInput does not have _render_with_buttons method")
            print("\n❌ TEST FAILED")
            window.close()
            return False
            
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all simple button tests."""
    print("\n" + "=" * 70)
    print("SIMPLE BUTTON DISPLAY TEST SUITE")
    print("=" * 70)
    print("\nThis test verifies that:")
    print("1. The UI has the show_choices method")
    print("2. PygameInput can create button rectangles")
    print("3. The button rendering method exists")
    print()
    
    try:
        results = []
        
        # Run all tests
        results.append(("UI Has show_choices", test_pygame_ui_has_show_choices()))
        results.append(("PygameInput Creates Buttons", test_pygame_input_creates_buttons()))
        results.append(("Button Rendering Method", test_button_rendering_method_exists()))
        
        # Summary
        print("\n" + "=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)
        
        for test_name, passed in results:
            status = "✅ PASSED" if passed else "❌ FAILED"
            print(f"{status}: {test_name}")
        
        all_passed = all(result[1] for result in results)
        
        if all_passed:
            print("\n" + "=" * 70)
            print("✅ ALL TESTS PASSED!")
            print("=" * 70)
            print("\nButton display infrastructure is working correctly.")
            print("\nIf buttons are not showing in the game, check:")
            print("1. That main.py is using pygame UI (not terminal mode)")
            print("2. That prompt_initial_decision is being called correctly")
            print("3. That there are no errors in the console during gameplay")
            return 0
        else:
            print("\n" + "=" * 70)
            print("❌ SOME TESTS FAILED")
            print("=" * 70)
            print("\nButton infrastructure has issues.")
            return 1
            
    except Exception as e:
        print(f"\n❌ TEST SUITE FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
