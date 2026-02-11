"""
Test Portrait Loading System

Ensures that merchant portraits are loaded correctly from their JSON configuration
and that the UI properly displays PNG images instead of file paths.
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

from core.players.merchants import load_merchants
from ui.pygame_window import PygameWindow


def test_merchant_portrait_files():
    """Test that all merchants have valid portrait_file attributes."""
    print("=" * 70)
    print("TEST 1: Merchant Portrait File Attributes")
    print("=" * 70)
    
    merchants = load_merchants()
    
    if not merchants:
        print("❌ FAILED: No merchants loaded")
        return False
    
    print(f"\nLoaded {len(merchants)} merchants")
    
    all_valid = True
    for merchant in merchants:
        portrait_file = merchant.portrait_file
        
        if portrait_file:
            # Check that it's a string (not a path object or other type)
            if not isinstance(portrait_file, str):
                print(f"❌ {merchant.name}: portrait_file is not a string (type: {type(portrait_file)})")
                all_valid = False
                continue
            
            # Check that it ends with .png
            if not portrait_file.endswith('.png'):
                print(f"⚠️  {merchant.name}: portrait_file '{portrait_file}' doesn't end with .png")
            
            # Check that the file exists
            portrait_path = project_root / 'characters' / 'portraits' / portrait_file
            if portrait_path.exists():
                print(f"✓ {merchant.name}: portrait_file='{portrait_file}' (exists)")
            else:
                print(f"⚠️  {merchant.name}: portrait_file='{portrait_file}' (file not found)")
        else:
            print(f"⚠️  {merchant.name}: No portrait_file specified")
    
    if all_valid:
        print("\n✅ All merchant portrait_file attributes are valid")
    else:
        print("\n❌ Some merchant portrait_file attributes are invalid")
    
    return all_valid


def test_portrait_loading_method():
    """Test that load_portrait_file method works correctly."""
    print("\n" + "=" * 70)
    print("TEST 2: Portrait Loading Method")
    print("=" * 70)
    
    try:
        # Create a pygame window (this will initialize pygame)
        window = PygameWindow()
        
        # Test loading a portrait file directly
        print("\nTesting load_portrait_file() method...")
        
        # Test with a known portrait file
        test_files = ['baker.png', 'trader.png', 'broker.png']
        
        all_passed = True
        for filename in test_files:
            portrait_path = project_root / 'characters' / 'portraits' / filename
            
            if portrait_path.exists():
                result = window.load_portrait_file(filename)
                if result:
                    print(f"✓ Successfully loaded '{filename}'")
                    
                    # Verify that current_portrait is set
                    if window.current_portrait is None:
                        print(f"  ❌ ERROR: current_portrait is None after loading")
                        all_passed = False
                    else:
                        print(f"  ✓ current_portrait is set (type: {type(window.current_portrait).__name__})")
                else:
                    print(f"❌ Failed to load '{filename}'")
                    all_passed = False
            else:
                print(f"⚠️  Skipping '{filename}' (file not found)")
        
        # Test with invalid file
        print("\nTesting with invalid filename...")
        result = window.load_portrait_file('nonexistent.png')
        if not result:
            print("✓ Correctly returned False for nonexistent file")
            if window.current_portrait is None:
                print("  ✓ current_portrait is None (as expected)")
            else:
                print("  ⚠️  current_portrait is still set (should be None)")
        else:
            print("❌ Incorrectly returned True for nonexistent file")
            all_passed = False
        
        # Clean up
        window.close()
        
        if all_passed:
            print("\n✅ Portrait loading method tests passed")
        else:
            print("\n❌ Some portrait loading method tests failed")
        
        return all_passed
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_portrait_file_not_path_object():
    """Test that portrait_file is a string, not a Path object."""
    print("\n" + "=" * 70)
    print("TEST 3: Portrait File Type Check")
    print("=" * 70)
    
    merchants = load_merchants()
    
    all_strings = True
    for merchant in merchants:
        if merchant.portrait_file:
            if isinstance(merchant.portrait_file, Path):
                print(f"❌ {merchant.name}: portrait_file is a Path object (should be string)")
                all_strings = False
            elif not isinstance(merchant.portrait_file, str):
                print(f"❌ {merchant.name}: portrait_file is {type(merchant.portrait_file)} (should be string)")
                all_strings = False
    
    if all_strings:
        print("✅ All portrait_file attributes are strings (not Path objects)")
    else:
        print("❌ Some portrait_file attributes are not strings")
    
    return all_strings


def test_load_portrait_file_integration():
    """Test that load_portrait_file integrates correctly with merchant data."""
    print("\n" + "=" * 70)
    print("TEST 4: Integration Test")
    print("=" * 70)
    
    merchants = load_merchants()
    
    try:
        window = PygameWindow()
        
        print(f"\nTesting portrait loading for {len(merchants)} merchants...")
        
        loaded_count = 0
        failed_count = 0
        skipped_count = 0
        
        for merchant in merchants:
            if merchant.portrait_file:
                result = window.load_portrait_file(merchant.portrait_file)
                if result:
                    print(f"✓ {merchant.name}: Loaded '{merchant.portrait_file}'")
                    loaded_count += 1
                else:
                    print(f"❌ {merchant.name}: Failed to load '{merchant.portrait_file}'")
                    failed_count += 1
            else:
                print(f"⚠️  {merchant.name}: No portrait_file (skipped)")
                skipped_count += 1
        
        window.close()
        
        print(f"\nResults:")
        print(f"  Loaded: {loaded_count}")
        print(f"  Failed: {failed_count}")
        print(f"  Skipped: {skipped_count}")
        
        if failed_count == 0:
            print("\n✅ Integration test passed")
            return True
        else:
            print(f"\n❌ Integration test failed ({failed_count} portraits failed to load)")
            return False
            
    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all portrait loading tests."""
    print("\n" + "=" * 70)
    print("PORTRAIT LOADING TEST SUITE")
    print("=" * 70)
    print("\nThis test ensures that:")
    print("1. All merchants have valid portrait_file attributes")
    print("2. The load_portrait_file() method works correctly")
    print("3. Portrait files are strings, not Path objects")
    print("4. Integration with merchant data works properly")
    print()
    
    try:
        results = []
        
        # Run all tests
        results.append(("Merchant Portrait Files", test_merchant_portrait_files()))
        results.append(("Portrait Loading Method", test_portrait_loading_method()))
        results.append(("Portrait File Type Check", test_portrait_file_not_path_object()))
        results.append(("Integration Test", test_load_portrait_file_integration()))
        
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
            print("\nPortrait loading system is working correctly.")
            print("PNG images will display properly in the game UI.")
            return 0
        else:
            print("\n" + "=" * 70)
            print("❌ SOME TESTS FAILED")
            print("=" * 70)
            print("\nPlease fix the issues above.")
            return 1
            
    except Exception as e:
        print(f"\n❌ TEST SUITE FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
