"""ASCII and narration helpers: merchant arrival, declaration, bribe display."""

from core.merchants import Merchant, load_portrait
from core.rounds import Declaration
from PIL import Image
import base64

def show_portrait(self):
        image_path = f"resources/{self.name.lower()}.png"
        try:
            with Image.open(image_path) as img:
                img.thumbnail((100, 100))
                img.save(image_path)
                img_bytes = img.tobytes()
                img_base64 = base64.b64encode(img_bytes).decode("utf-8")
                print(f'<img src="data:image/png;base64,{img_base64}" />')
        except FileNotFoundError:
            print("Portrait not found.")

def narrate_arrival(merchant: Merchant) -> None:
    """Narrate merchant arrival and show portrait."""
    print(f"\n--- {merchant.name} approaches the gate ---")
    print(f"  {merchant.personality}")
    if merchant.lore:
        print(f"  {merchant.lore}")
    show_portrait(merchant)
    print()


def show_declaration(merchant: Merchant, declaration: Declaration) -> None:
    """Display what the merchant declares."""
    print(f"{merchant.name} declares: {declaration.count} x {declaration.good_id}")
    print()


def show_bribe(merchant: Merchant, bribe: str) -> None:
    """Display bribe offer."""
    if bribe:
        print(f"{merchant.name} offers: {bribe}")
    else:
        print(f"{merchant.name} offers no bribe.")
    print()


def show_inspection_result(merchant: Merchant, sheriff_opens: bool, caught: bool) -> None:
    """Report whether the Sheriff opened the bag and caught a lie."""
    if sheriff_opens:
        if caught:
            print(f"The Sheriff inspects {merchant.name}'s bag and finds contraband!")
        else:
            print(f"The Sheriff inspects {merchant.name}'s bag and finds nothing amiss.")
    else:
        print(f"The Sheriff lets {merchant.name} pass without inspection.")
    print()
