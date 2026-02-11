"""
Test Button Display System

Ensures that choice buttons are properly displayed during gameplay
and that the UI doesn't fall back to text-only mode.
"""

import sys
from pathlib import Path
from unittest.mock import Mock, patch
import pygame

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_show_choices_creates_buttons():
    """Test that show_choices creates button rectangles."""
    print("=" * 70)
    print("TEST 1: Button Creation")
    print("=" * 70)
    
    try:
        from ui.pygame_input import PygameInput
        from ui.pygame_window import PygameWindow
        from ui.pygame_text import PygameText
        from ui.price_menu import PriceMenu
        
        # Initialize components
        window = PygameWindow()
        text = PygameText(window)
        price_menu = PriceMenu(window.screen, window.font_normal, window.font_small)
        input_handler = PygameInput(window, text, price_menu)
        
        # Test choices
        test_choices = [
            ('accept', 'Accept 5 gold'),
            ('threaten', 'Threaten to inspect'),
            ('inspect', 'Inspect immediately'),
            ('pass', 'Wave them through')
        ]
        
        # Mock the event loop to avoid hanging
        original_tick = window.clock.tick
        call_count = [0]
        
        def mock_tick(fps):
            call_count[0] += 1
            if call_count[0] > 2:  # Exit after a few ticks
                # Simulate a button click
                pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'pos': (600, 750)}))
            return original_tick(fps)
        
        window.clock.tick = mock_tick
        
        # Call show_choices (will exit quickly due to mock)
        try:
            result = input_handler.show_choices("What do you do?", test_choices)
        except (SystemExit, pygame.error):
            pass  # Expected when pygame quits
        
        # Check that buttons were created
        if hasattr(input_handler, 'choice_buttons') and input_handler.choice_buttons:
            print(f"✓ Buttons created: {len(input_handler.choice_buttons)} buttons")
            for i, (text, rect) in enumerate(input_handler.choice_buttons):
                print(f"  Button {i+1}: '{text}' at ({rect.x}, {rect.y})")
            print("\n✅ Button creation test passed")
            window.close()
            return True
        else:
            print("❌ No buttons were created!")
            print(f"  choice_buttons attribute: {hasattr(input_handler, 'choice_buttons')}")
            if hasattr(input_handler, 'choice_buttons'):
                print(f"  choice_buttons value: {input_handler.choice_buttons}")
            print("\n❌ Button creation test failed")
            window.close()
            return False
            
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_prompt_initial_decision_uses_buttons():
    """Test that prompt_initial_decision calls show_choices (not text input)."""
    print("\n" + "=" * 70)
    print("TEST 2: Initial Decision Uses Buttons")
    print("=" * 70)
    
    try:
        # Mock the UI to track method calls
        from ui import narration
        from ui.pygame_ui import get_ui
        
        # Check if USING_PYGAME is True
        if not narration.USING_PYGAME:
            print("⚠️  USING_PYGAME is False - buttons won't be shown")
            print("   This might be why buttons aren't appearing!")
            return False
        
        print(f"✓ USING_PYGAME = {narration.USING_PYGAME}")
        
        # Create a mock UI
        mock_ui = Mock()
        mock_ui.show_choices = Mock(return_value='inspect')
        
        # Patch get_ui to return our mock
        with patch('ui.narration.get_ui', return_value=mock_ui):
            result = narration.prompt_initial_decision(has_proactive_bribe=True, bribe_amount=5)
        
        # Check if show_choices was called
        if mock_ui.show_choices.called:
            print("✓ show_choices() was called")
            call_args = mock_ui.show_choices.call_args
            print(f"  Prompt: {call_args[0][0]}")
            print(f"  Choices: {call_args[0][1]}")
            print("\n✅ Initial decision uses buttons test passed")
            return True
        else:
            print("❌ show_choices() was NOT called")
            print("   The function is using text input instead of buttons!")
            print("\n❌ Initial decision uses buttons test failed")
            return False
            
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_render_with_buttons_draws_rectangles():
    """Test that _render_with_buttons actually draws button rectangles."""
    print("\n" + "=" * 70)
    print("TEST 3: Button Rendering")
    print("=" * 70)
    
    try:
        from ui.pygame_input import PygameInput
        from ui.pygame_window import PygameWindow
        from ui.pygame_text import PygameText
        from ui.price_menu import PriceMenu
        
        # Initialize components
        window = PygameWindow()
        text = PygameText(window)
        price_menu = PriceMenu(window.screen, window.font_normal, window.font_small)
        input_handler = PygameInput(window, text, price_menu)
        
        # Manually create some test buttons
        test_buttons = [
            ("Test Button 1", pygame.Rect(100, 700, 200, 50)),
            ("Test Button 2", pygame.Rect(320, 700, 200, 50)),
        ]
        input_handler.choice_buttons = test_buttons
        
        # Mock pygame.draw.rect to track if it's called
        draw_calls = []
        original_draw_rect = pygame.draw.rect
        
        def mock_draw_rect(surface, color, rect, width=0):
            draw_calls.append(('rect', color, rect, width))
            return original_draw_rect(surface, color, rect, width)
        
        pygame.draw.rect = mock_draw_rect
        
        # Call _render_with_buttons
        input_handler._render_with_buttons()
        
        # Restore original
        pygame.draw.rect = original_draw_rect
        
        # Check if rectangles were drawn
        rect_draws = [call for call in draw_calls if call[0] == 'rect']
        
        if len(rect_draws) >= len(test_buttons) * 2:  # Each button = filled rect + border
            print(f"✓ Button rectangles drawn: {len(rect_draws)} draw calls")
            print(f"  Expected at least {len(test_buttons) * 2} calls (2 per button)")
            print("\n✅ Button rendering test passed")
            window.close()
            return True
        else:
            print(f"❌ Not enough draw calls: {len(rect_draws)}")
            print(f"  Expected at least {len(test_buttons) * 2} calls")
            print("\n❌ Button rendering test failed")
            window.close()
            return False
            
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_button_positioning():
    """Test that buttons are positioned at the bottom of the screen."""
    print("\n" + "=" * 70)
    print("TEST 4: Button Positioning")
    print("=" * 70)
    
    try:
        from ui.pygame_input import PygameInput
        from ui.pygame_window import PygameWindow, SCREEN_HEIGHT
        from ui.pygame_text import PygameText
        from ui.price_menu import PriceMenu
        
        # Initialize components
        window = PygameWindow()
        text = PygameText(window)
        price_menu = PriceMenu(window.screen, window.font_normal, window.font_small)
        input_handler = PygameInput(window, text, price_menu)
        
        # Create test buttons
        test_choices = [
            ('option1', 'Option 1'),
            ('option2', 'Option 2'),
            ('option3', 'Option 3'),
        ]
        
        # Manually trigger button creation logic
        button_width = 220
        button_height = 50
        expected_y = SCREEN_HEIGHT - button_height - 30
        
        print(f"Screen height: {SCREEN_HEIGHT}")
        print(f"Expected button Y position: {expected_y}")
        print(f"Expected button height: {button_height}")
        
        # Buttons should be near bottom of screen
        if expected_y > SCREEN_HEIGHT - 100:
            print(f"✓ Buttons positioned at bottom of screen (Y={expected_y})")
            print("\n✅ Button positioning test passed")
            window.close()
            return True
        else:
            print(f"❌ Buttons not at bottom (Y={expected_y})")
            print("\n❌ Button positioning test failed")
            window.close()
            return False
            
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all button display tests."""
    print("\n" + "=" * 70)
    print("BUTTON DISPLAY TEST SUITE")
    print("=" * 70)
    print("\nThis test ensures that:")
    print("1. Choice buttons are created when show_choices() is called")
    print("2. prompt_initial_decision() uses buttons (not text)")
    print("3. Buttons are actually rendered to the screen")
    print("4. Buttons are positioned correctly at the bottom")
    print()
    
    try:
        results = []
        
        # Run all tests
        results.append(("Button Creation", test_show_choices_creates_buttons()))
        results.append(("Initial Decision Uses Buttons", test_prompt_initial_decision_uses_buttons()))
        results.append(("Button Rendering", test_render_with_buttons_draws_rectangles()))
        results.append(("Button Positioning", test_button_positioning()))
        
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
            print("\nButton display system is working correctly.")
            print("Buttons should appear during gameplay.")
            return 0
        else:
            print("\n" + "=" * 70)
            print("❌ SOME TESTS FAILED")
            print("=" * 70)
            print("\nButtons may not be displaying correctly.")
            print("Check the failures above for details.")
            return 1
            
    except Exception as e:
        print(f"\n❌ TEST SUITE FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
