"""
Core game logic package - reorganized into submodules:
- game: Game flow and management (game_manager, game_rules, rounds, end_game)
- players: Player-related logic (merchants, sheriff, merchant_loader, sheriff_analysis)
- mechanics: Game mechanics (goods, inspection, negotiation, black_market)
- systems: Supporting systems (logger, game_stats, reputation)

For backward compatibility, commonly used classes are re-exported below.
"""

# Re-export commonly used classes for backward compatibility
# Note: run_game is not imported here to avoid circular imports with ui.narration
# Import it directly from core.game.game_manager when needed
from core.constants import (
    HAND_SIZE_LIMIT, BAG_SIZE_LIMIT, STARTING_GOLD, STARTING_REPUTATION,
    STARTING_PERCEPTION, STARTING_AUTHORITY, STARTING_EXPERIENCE
)
from core.game.rounds import Declaration, resolve_inspection
from core.game.end_game import show_end_game_summary

from core.players.merchants import Merchant, InformationBroker
from core.players.merchant_loader import load_merchants
from core.players.sheriff import Sheriff
from core.players.sheriff_analysis import calculate_catch_rate, analyze_sheriff_detailed

from core.mechanics.goods import Good, GOOD_BY_ID, ALL_LEGAL, ALL_CONTRABAND
from core.mechanics.inspection import handle_inspection, handle_pass_without_inspection
from core.mechanics.negotiation import (
    initiate_threat, merchant_respond_to_threat, sheriff_respond_to_bribe,
    merchant_respond_to_counter, resolve_negotiation, NegotiationOutcome, NegotiationState
)
# black_market removed - feature not being implemented

from core.systems.logger import log_error, log_warning, log_info, log_debug
from core.systems.game_stats import GameStats
from core.systems.reputation import update_sheriff_reputation

__all__ = [
    # Game management
    'HAND_SIZE_LIMIT', 'BAG_SIZE_LIMIT', 'STARTING_GOLD', 'STARTING_REPUTATION',
    'STARTING_PERCEPTION', 'STARTING_AUTHORITY', 'STARTING_EXPERIENCE',
    'Declaration', 'resolve_inspection', 'show_end_game_summary',
    # Players
    'Merchant', 'InformationBroker', 'load_merchants', 'Sheriff',
    'calculate_catch_rate', 'analyze_sheriff_detailed',
    # Mechanics
    'Good', 'GOOD_BY_ID', 'ALL_LEGAL', 'ALL_CONTRABAND',
    'handle_inspection', 'handle_pass_without_inspection',
    'initiate_threat', 'merchant_respond_to_threat', 'sheriff_respond_to_bribe',
    'merchant_respond_to_counter', 'resolve_negotiation', 'NegotiationOutcome', 'NegotiationState',
    # Systems
    'log_error', 'log_warning', 'log_info', 'log_debug',
    'GameStats', 'update_sheriff_reputation',
]
