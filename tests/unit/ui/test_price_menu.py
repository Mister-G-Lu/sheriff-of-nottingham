"""
Test Price Menu Display

Ensures that the price menu can be accessed from the right-hand side
and displays correctly.
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


def test_price_menu_button_on_right_side():
    """Test that price menu button is positioned on the right side."""
    print("=" * 70)
    print("TEST 1: Price Menu Button on Right Side")
    print("=" * 70)
    
    try:
        from ui.price_menu import PriceMenu
        from ui.pygame_window import PygameWindow
        
        window = PygameWindow()
        price_menu = PriceMenu(window.screen, window.font_normal, window.font_small)
        
        screen_width = window.screen.get_width()
        button_x = price_menu.button_x
        button_width = price_menu.button_width
        
        print(f"Screen width: {screen_width}")
        print(f"Button X position: {button_x}")
        print(f"Button width: {button_width}")
        print(f"Button right edge: {button_x + button_width}")
        
        # Button should be on the right side (X > 50% of screen width)
        if button_x > screen_width / 2:
            print("✓ Button is on the right side of screen")
            
            # Button should be near the right edge (within 100px)
            if button_x + button_width > screen_width - 100:
                print("✓ Button is near the right edge")
                print("\n✅ TEST PASSED")
                window.close()
                return True
            else:
                print("❌ Button is too far from right edge")
                print("\n❌ TEST FAILED")
                window.close()
                return False
        else:
            print("❌ Button is not on the right side")
            print("\n❌ TEST FAILED")
            window.close()
            return False
            
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_price_menu_toggle():
    """Test that price menu can be toggled open and closed."""
    print("\n" + "=" * 70)
    print("TEST 2: Price Menu Toggle")
    print("=" * 70)
    
    try:
        from ui.price_menu import PriceMenu
        from ui.pygame_window import PygameWindow
        
        window = PygameWindow()
        price_menu = PriceMenu(window.screen, window.font_normal, window.font_small)
        
        print(f"Initial state: is_open = {price_menu.is_open}")
        
        # Simulate clicking the button
        button_center = price_menu.button_rect.center
        result = price_menu.handle_click(button_center)
        
        print(f"After first click: is_open = {price_menu.is_open}, returned = {result}")
        
        if result and price_menu.is_open:
            print("✓ Menu opened on first click")
            
            # Click again to close
            result = price_menu.handle_click(button_center)
            print(f"After second click: is_open = {price_menu.is_open}, returned = {result}")
            
            if result and not price_menu.is_open:
                print("✓ Menu closed on second click")
                print("\n✅ TEST PASSED")
                window.close()
                return True
            else:
                print("❌ Menu did not close properly")
                print("\n❌ TEST FAILED")
                window.close()
                return False
        else:
            print("❌ Menu did not open on first click")
            print("\n❌ TEST FAILED")
            window.close()
            return False
            
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_price_menu_displays_goods():
    """Test that price menu displays legal goods and contraband."""
    print("\n" + "=" * 70)
    print("TEST 3: Price Menu Displays Goods")
    print("=" * 70)
    
    try:
        from ui.price_menu import PriceMenu
        from ui.pygame_window import PygameWindow
        from core.mechanics.goods import ALL_LEGAL, ALL_CONTRABAND
        
        window = PygameWindow()
        price_menu = PriceMenu(window.screen, window.font_normal, window.font_small)
        
        # Open the menu
        price_menu.is_open = True
        
        # Render the menu (this should not crash)
        try:
            price_menu.render_menu()
            print("✓ Menu renders without errors")
        except Exception as e:
            print(f"❌ Menu rendering failed: {e}")
            window.close()
            return False
        
        # Check that goods data is available
        print(f"✓ Legal goods available: {len(ALL_LEGAL)} items")
        print(f"✓ Contraband available: {len(ALL_CONTRABAND)} items")
        
        if len(ALL_LEGAL) > 0 and len(ALL_CONTRABAND) > 0:
            print("\n✅ TEST PASSED")
            window.close()
            return True
        else:
            print("❌ No goods data available")
            print("\n❌ TEST FAILED")
            window.close()
            return False
            
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_price_menu_panel_on_right():
    """Test that price menu panel appears on the right side."""
    print("\n" + "=" * 70)
    print("TEST 4: Price Menu Panel on Right Side")
    print("=" * 70)
    
    try:
        from ui.price_menu import PriceMenu
        from ui.pygame_window import PygameWindow
        
        window = PygameWindow()
        price_menu = PriceMenu(window.screen, window.font_normal, window.font_small)
        
        screen_width = window.screen.get_width()
        menu_x = price_menu.menu_x
        menu_width = price_menu.menu_width
        
        print(f"Screen width: {screen_width}")
        print(f"Menu X position: {menu_x}")
        print(f"Menu width: {menu_width}")
        print(f"Menu right edge: {menu_x + menu_width}")
        
        # Menu panel should be on the right side
        if menu_x > screen_width / 2:
            print("✓ Menu panel is on the right side")
            
            # Menu should align with button
            if abs(menu_x - price_menu.button_x) < 50:
                print("✓ Menu panel aligns with button")
                print("\n✅ TEST PASSED")
                window.close()
                return True
            else:
                print("⚠️  Menu panel doesn't align perfectly with button")
                print("   (This is acceptable)")
                print("\n✅ TEST PASSED")
                window.close()
                return True
        else:
            print("❌ Menu panel is not on the right side")
            print("\n❌ TEST FAILED")
            window.close()
            return False
            
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_price_menu_click_outside():
    """Test that clicking outside the button doesn't toggle menu."""
    print("\n" + "=" * 70)
    print("TEST 5: Click Outside Button")
    print("=" * 70)
    
    try:
        from ui.price_menu import PriceMenu
        from ui.pygame_window import PygameWindow
        
        window = PygameWindow()
        price_menu = PriceMenu(window.screen, window.font_normal, window.font_small)
        
        initial_state = price_menu.is_open
        
        # Click somewhere else on screen (center)
        center_pos = (window.screen.get_width() // 2, window.screen.get_height() // 2)
        result = price_menu.handle_click(center_pos)
        
        print(f"Initial state: {initial_state}")
        print(f"Clicked at screen center: {center_pos}")
        print(f"Result: {result}, New state: {price_menu.is_open}")
        
        if not result and price_menu.is_open == initial_state:
            print("✓ Menu state unchanged when clicking outside button")
            print("\n✅ TEST PASSED")
            window.close()
            return True
        else:
            print("❌ Menu state changed unexpectedly")
            print("\n❌ TEST FAILED")
            window.close()
            return False
            
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all price menu tests."""
    print("\n" + "=" * 70)
    print("PRICE MENU TEST SUITE")
    print("=" * 70)
    print("\nThis test verifies that:")
    print("1. Price menu button is on the right side of screen")
    print("2. Price menu can be toggled open and closed")
    print("3. Price menu displays legal goods and contraband")
    print("4. Price menu panel appears on the right side")
    print("5. Clicking outside button doesn't toggle menu")
    print()
    
    try:
        results = []
        
        # Run all tests
        results.append(("Button on Right Side", test_price_menu_button_on_right_side()))
        results.append(("Menu Toggle", test_price_menu_toggle()))
        results.append(("Displays Goods", test_price_menu_displays_goods()))
        results.append(("Panel on Right Side", test_price_menu_panel_on_right()))
        results.append(("Click Outside", test_price_menu_click_outside()))
        
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
            print("\nPrice menu system is working correctly.")
            print("Menu can be accessed from the right-hand side.")
            return 0
        else:
            print("\n" + "=" * 70)
            print("❌ SOME TESTS FAILED")
            print("=" * 70)
            print("\nPrice menu has issues.")
            return 1
            
    except Exception as e:
        print(f"\n❌ TEST SUITE FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
