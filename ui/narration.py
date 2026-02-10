"""ASCII and narration helpers: merchant arrival, declaration, bribe display."""

from core.merchants import Merchant, load_portrait
from core.rounds import Declaration

# Avatar box size when compressing large portraits
AVATAR_ROWS = 10
AVATAR_COLS = 10


def compress_portrait(art: str, max_rows: int = AVATAR_ROWS, max_cols: int = AVATAR_COLS) -> str:
    """Compress portrait art into a max_rows x max_cols box by sampling. Returns original if already small."""
    if not art or not art.strip():
        return art
    lines = [line.rstrip("\n") for line in art.splitlines()]
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    if not lines:
        return ""
    height, width = len(lines), max(len(line) for line in lines)
    if height <= max_rows and width <= max_cols:
        return art
    grid = [line.ljust(width) for line in lines]
    row_ix = (
        list(range(height))
        if height <= max_rows
        else [i * (height - 1) // (max_rows - 1) for i in range(max_rows)]
    )
    col_ix = (
        list(range(width))
        if width <= max_cols
        else [j * (width - 1) // (max_cols - 1) for j in range(max_cols)]
    )
    out = []
    for r in row_ix:
        row = grid[r]
        out.append("".join(row[c] if c < len(row) else " " for c in col_ix))
    return "\n".join(out)


def _safe_print_unicode(text: str) -> None:
    """Print text; if console can't encode Unicode (e.g. Windows cp1252), fall back to ASCII placeholder."""
    try:
        print(text)
    except UnicodeEncodeError:
        # Replace non-ASCII (e.g. block chars) with # for terminals that don't support UTF-8
        print("".join(c if ord(c) < 128 else "#" for c in text))


def show_portrait(merchant: Merchant) -> None:
    """Print merchant's ASCII portrait from their .txt file, compressed to avatar box (e.g. 10x10)."""
    art = load_portrait(merchant)
    if art:
        _safe_print_unicode(compress_portrait(art))


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
