"""
Portrait Loading
Handles loading character portrait images
"""

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.players.merchants import Merchant


def characters_dir() -> Path:
    """Return the path to the characters directory."""
    return Path(__file__).parent.parent / "characters"


def load_portrait(merchant: 'Merchant') -> str:
    """
    Load a merchant's portrait file path.
    
    Args:
        merchant: Merchant object with portrait_file attribute
    
    Returns:
        str: Path to portrait file, or empty string if not found
    """
    if not merchant.portrait_file:
        return ""
    
    portrait_path = characters_dir() / "portraits" / merchant.portrait_file
    if portrait_path.exists():
        return str(portrait_path)
    return ""
