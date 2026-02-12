"""
End Game States - Victory and Defeat Conditions

This module centralizes all game ending logic, making it easy to find and modify
victory/defeat conditions and their associated narrative text.

Lore text is stored in data/end_game_lore.json for easy editing.
"""

import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class EndGameState(Enum):
    """Possible end game states."""

    LEGENDARY_SHERIFF = "legendary"  # Perfect run: high reputation + wealth
    HONORABLE_SHERIFF = "honorable"  # High reputation, no bribes
    CORRUPT_BARON = "corrupt"  # Low reputation, high bribes
    EXCELLENT = "excellent"  # Good performance
    GOOD = "good"  # Decent performance
    MEDIOCRE = "mediocre"  # Barely passing
    POOR = "poor"  # Bad performance
    FIRED = "fired"  # Game over - reputation 0


@dataclass
class EndGameResult:
    """Container for end game results."""

    state: EndGameState
    title: str
    rating: str
    flavor_text: list[str]  # List of paragraphs


def _load_lore() -> dict:
    """Load end game lore from JSON file."""
    lore_path = Path(__file__).parent.parent / "data" / "end_game_lore.json"
    try:
        with open(lore_path, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Warning: Could not load end game lore: {e}")
        return {}


def _create_result(
    lore: dict,
    lore_key: str,
    state: EndGameState,
    default_title: str,
    default_rating: str,
    default_text: list[str],
) -> EndGameResult:
    """
    Helper to create EndGameResult from lore data.

    Reduces repetitive lore.get() calls throughout the code.
    """
    lore_data = lore.get(lore_key, {})
    return EndGameResult(
        state=state,
        title=lore_data.get("title", default_title),
        rating=lore_data.get("rating", default_rating),
        flavor_text=lore_data.get("paragraphs", default_text),
    )


def determine_end_game_state(sheriff, stats) -> EndGameResult:
    """
    Determine the end game state based on sheriff performance.

    Victory Paths:
    1. LEGENDARY_SHERIFF: High rep (≥7) + High gold (≥50) + Good catches
    2. HONORABLE_SHERIFF: High rep (≥7) + No bribes
    3. CORRUPT_BARON: Low rep (≤3) + High bribes (≥5) + High gold (≥50)

    Standard Ratings:
    4. EXCELLENT: Rep ≥7
    5. GOOD: Rep 4-6
    6. MEDIOCRE: Rep 2-3
    7. POOR: Rep 1
    8. FIRED: Rep 0

    Args:
        sheriff: Sheriff object with reputation
        stats: GameStats object

    Returns:
        EndGameResult with state, title, rating, and flavor text
    """
    rep = sheriff.reputation
    gold = stats.gold_earned
    bribes = stats.bribes_accepted
    caught = stats.smugglers_caught

    # Load lore from JSON
    lore = _load_lore()

    # Check for special victory paths first
    if rep >= 7 and gold >= 50 and caught >= 3:
        return _create_result(
            lore,
            "legendary_sheriff",
            EndGameState.LEGENDARY_SHERIFF,
            "🏆 THE LEGENDARY SHERIFF",
            "★★★★★ LEGENDARY",
            ["Victory!"],
        )

    elif rep >= 7 and bribes == 0:
        return _create_result(
            lore,
            "honorable_sheriff",
            EndGameState.HONORABLE_SHERIFF,
            "⚔️ THE HONORABLE SHERIFF",
            "★★★★☆ HONORABLE",
            ["Victory!"],
        )

    elif rep <= 3 and bribes >= 5 and gold >= 50:
        return _create_result(
            lore,
            "corrupt_baron",
            EndGameState.CORRUPT_BARON,
            "💰 THE CORRUPT BARON",
            "★★★☆☆ CORRUPT",
            ["Victory!"],
        )

    # Standard ratings based on reputation
    elif rep >= 7:
        return _create_result(
            lore,
            "excellent",
            EndGameState.EXCELLENT,
            "Excellent Performance",
            "★★★★☆ EXCELLENT",
            ["Good job!"],
        )

    elif rep >= 4:
        return _create_result(
            lore,
            "good",
            EndGameState.GOOD,
            "Good Performance",
            "★★★☆☆ GOOD",
            ["Decent work."],
        )

    elif rep >= 2:
        return _create_result(
            lore,
            "mediocre",
            EndGameState.MEDIOCRE,
            "Mediocre Performance",
            "★★☆☆☆ MEDIOCRE",
            ["Could be better."],
        )

    elif rep > 0:
        return _create_result(
            lore,
            "poor",
            EndGameState.POOR,
            "Poor Performance",
            "★☆☆☆☆ POOR",
            ["Not good."],
        )

    else:  # rep == 0
        return _create_result(
            lore,
            "fired",
            EndGameState.FIRED,
            "💀 GAME OVER - FIRED",
            "☆☆☆☆☆ FIRED",
            ["Game Over."],
        )


def show_end_game_summary(sheriff, stats):
    """
    Display comprehensive end-game statistics and determine victory/defeat.

    Args:
        sheriff: Sheriff object
        stats: GameStats object
    """
    print("\n" + "=" * 70)
    print("SHIFT SUMMARY".center(70))
    print("=" * 70)
    print()

    # Performance Statistics
    print("📊 Performance:")
    print(f"   Merchants Processed: {stats.merchants_processed}")
    print(f"   Smugglers Caught: {stats.smugglers_caught} ⚔️")
    print(f"   Honest Merchants Inspected: {stats.honest_inspected}")
    print()

    # Inspections
    if stats.total_inspections > 0:
        print("🔍 Inspections:")
        print(f"   Total Inspections: {stats.total_inspections}")
        print(f"   Correct Decisions: {stats.correct_inspections}")
        print(f"   Accuracy: {stats.accuracy_percentage():.1f}%")
        if stats.missed_smugglers > 0:
            print(f"   Missed Smugglers: {stats.missed_smugglers} ⚠️")
        print()

    # Finances
    if stats.bribes_accepted > 0:
        print("💰 Finances:")
        print(f"   Bribes Accepted: {stats.bribes_accepted}")
        print(f"   Gold Earned: {stats.gold_earned} gold")
        print()

    # Reputation
    print("⚖️  Reputation:")
    print(f"   Final Reputation: {sheriff.reputation}/10")
    if sheriff.reputation >= 7:
        status = "Excellent Standing ✓"
    elif sheriff.reputation >= 4:
        status = "Good Standing ✓"
    elif sheriff.reputation >= 2:
        status = "Poor Standing ⚠️"
    elif sheriff.reputation > 0:
        status = "On Thin Ice ⚠️"
    else:
        status = "FIRED 💀"
    print(f"   Status: {status}")
    print()

    # Determine end game state
    result = determine_end_game_state(sheriff, stats)

    # Show victory/defeat state
    print("=" * 70)
    print(result.title.center(70))
    print("=" * 70)
    print()

    # Show flavor text
    for line in result.flavor_text:
        if line:
            print(line)
        else:
            print()
    print()

    # Show rating
    print("=" * 70)
    print(f"Rating: {result.rating}".center(70))
    print("=" * 70)
    print()
