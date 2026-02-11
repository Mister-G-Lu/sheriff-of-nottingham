# AI Strategy System - Developer Guide

## Overview

This directory contains the AI decision-making system for merchant NPCs in Sheriff of Nottingham. The system uses a tiered approach with intelligent bribe calculation and personality-driven behavior.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  Merchant.choose_declaration()               │
│                  (core/players/merchants.py)                 │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│              tiered_strategy.py (Main Controller)            │
│  • Queries GameMasterState for tier-appropriate history     │
│  • Analyzes sheriff behavior patterns                        │
│  • Selects strategy based on personality + tier + history    │
│  • Coordinates declaration building and bribe calculation    │
└──────────────┬──────────────────────────┬───────────────────┘
               │                          │
               ▼                          ▼
┌──────────────────────────┐  ┌──────────────────────────────┐
│  declaration_builder.py  │  │     bribe_strategy.py        │
│  • Builds 5 declaration  │  │  • Calculates scaled bribes  │
│    types (honest, legal  │  │  • 70-110% of declared value │
│    lie, mixed, low/high  │  │  • Personality modifiers     │
│    contraband)           │  │  • Advanced bluff logic      │
│  • Single source of      │  │  • Tier-based behavior       │
│    truth for bag         │  │                              │
│    building              │  │                              │
└──────────────────────────┘  └──────────────────────────────┘
```

## Core Modules

### 1. `tiered_strategy.py` - Main Strategy Controller

**Purpose**: Orchestrates merchant decision-making with tier-based sophistication

**Key Components**:
- `TieredMerchantStrategy` - Main strategy class
- `get_tiered_declaration()` - Public interface

**Difficulty Tiers**:

#### Easy Tier
- **History Access**: Last 1-2 events only
- **Strategy**: Mostly safe (60% honest, 35% legal lie, 5% mixed)
- **Bribe Frequency**: Rarely (30% even with contraband)
- **Behavior**: Nervous, predictable, honest-leaning
- **Example**: Alice (honesty=8, risk=2)

#### Medium Tier
- **History Access**: Last 3-4 events
- **Strategy**: Adapts to sheriff (balanced risk/reward)
- **Bribe Frequency**: Moderate (60% with contraband)
- **Behavior**: Observant, adaptive, profit-seeking
- **Example**: Cedric (honesty=5, risk=6)

#### Hard Tier
- **History Access**: Full game history
- **Strategy**: Advanced pattern recognition and exploitation
- **Bribe Frequency**: Sophisticated (70-95% context-dependent)
- **Behavior**: Intelligent, unpredictable, strategic
- **Special**: Can use advanced bluff (bribe on honest bag)
- **Example**: Silas Voss (Information Broker), Garrett

**Decision Flow**:
```python
1. Query GameMasterState for tier-appropriate history
2. Analyze sheriff patterns (inspection rate, catch rate)
3. Calculate risk score (personality + sheriff behavior)
4. Select strategy type (honest/legal_lie/mixed/contraband_low/contraband_high)
5. Build declaration using declaration_builder
6. Calculate bribe using bribe_strategy
7. Return complete decision
```

### 2. `declaration_builder.py` - Declaration Construction

**Purpose**: Single source of truth for building merchant declarations

**Functions**:
- `build_honest_declaration()` - Declare and carry same legal goods
- `build_legal_lie_declaration()` - Declare one legal, carry different legal
- `build_mixed_declaration()` - Declare legal, carry mostly legal + 1 contraband
- `build_contraband_low_declaration()` - Declare legal, carry 1-2 contraband
- `build_contraband_high_declaration()` - Declare legal, carry 3-5 high-value contraband
- `build_declaration(strategy_type)` - Unified interface

**Strategy Types**:

| Strategy | Risk | Reward | Description |
|----------|------|--------|-------------|
| `honest` | 0/10 | 0g | Truthful declaration |
| `legal_lie` | 3/10 | 5-14g | Mixed legal goods |
| `mixed` | 6/10 | 15-30g | Mostly legal + 1 contraband |
| `contraband_low` | 8/10 | 40-80g | 1-2 contraband items |
| `contraband_high` | 10/10 | 100-250g | 3-5 high-value contraband |

**Returns**:
```python
{
    'declared_id': str,      # Good ID to declare
    'count': int,            # How many to declare
    'actual_ids': list[str], # What's actually in bag
    'lie': bool,             # Is declaration false?
    'lie_type': str,         # 'none', 'legal', 'mixed', 'contraband'
    'strategy': str          # Strategy name
}
```

### 3. `bribe_strategy.py` - Intelligent Bribe Calculation

**Purpose**: Calculate bribes that scale with declared value to avoid suspicion

**Core Insight**:
```
❌ WRONG: Declare "1x Apple" (2g) + offer 9g bribe = SUSPICIOUS (450% of declared)
✅ RIGHT: Declare "4x Apple" (8g) + offer 9g bribe = REASONABLE (112% of declared)
```

**Key Functions**:
- `calculate_scaled_bribe()` - Main bribe calculation
- `calculate_contraband_bribe()` - For contraband smuggling
- `calculate_legal_lie_bribe()` - For legal goods lies
- `calculate_advanced_bluff_bribe()` - For advanced bluff (Hard AI only)
- `should_offer_bribe()` - Decides whether to bribe at all
- `should_accept_counter_offer()` - Negotiation logic

**Bribe Calculation Logic**:

#### Contraband Bribe
```python
# Base: 70-110% of declared value (makes sheriff think twice)
base = declared_value * random.uniform(0.7, 1.1)

# Cap by contraband value (merchant must profit)
max_rational = contraband_value * 0.8

# Apply personality modifiers
final = min(base, max_rational) * greed_factor * risk_factor
```

**Sheriff's Calculation**:
- "If honest, I pay `declared_value` penalty"
- "If I accept `bribe_amount`, I profit"
- "If bribe ≈ declared_value, worth accepting"

#### Advanced Bluff (Hard AI Only)
- **Frequency**: 15% chance
- **Setup**: Carry PERFECT legal bag
- **Bribe**: Small "goodwill" gesture (2-5g)
- **Psychology**: Creates uncertainty, makes sheriff question instincts
- **Payoff**: If sheriff demands more, merchant REFUSES (calls bluff)

**Personality Modifiers**:
- **Greed** (0-10): Higher = lower bribe offers
- **Risk Tolerance** (0-10): Higher = lower bribes (willing to gamble)
- **Honesty Bias** (0-10): Affects whether to bribe at all

### 4. `silas_strategy.py` - Information Broker (Special Case)

**Purpose**: Sophisticated strategy for Silas Voss, the Information Broker

**Characteristics**:
- Always HARD tier
- Analyzes full game history
- Uses `analyze_sheriff_detailed()` for pattern recognition
- Adapts strategy based on sheriff's catch rate
- Exploits predictable behavior

**Decision Logic**:
```python
if catch_rate > 0.6:
    # Sheriff is dangerous - play safe or use advanced bluff
    return honest or legal_lie
elif catch_rate < 0.3:
    # Sheriff is lenient - go aggressive
    return contraband (3-4 items)
else:
    # Moderate risk - calculated smuggling
    return contraband (2-3 items)
```

## Game Master State Integration

All merchants query the centralized `GameMasterState` for history:

```python
from core.systems.game_master_state import get_game_master_state, MerchantTier

game_state = get_game_master_state()
history = game_state.get_history_for_tier(MerchantTier.MEDIUM)
sheriff_stats = game_state.get_sheriff_stats()
```

**History Slicing**:
- Easy: Last 1-2 events
- Medium: Last 3-4 events
- Hard: Full history

**Sheriff Stats**:
- `inspection_rate`: How often sheriff inspects (0.0-1.0)
- `catch_rate`: How often inspections catch lies (0.0-1.0)
- `bribe_acceptance_rate`: How often sheriff accepts bribes (0.0-1.0)

## Usage Examples

### Basic Usage (Merchant Class)

```python
from ai_strategy.tiered_strategy import get_tiered_declaration
from core.systems.game_master_state import MerchantTier

# Merchant personality
personality = {
    'risk_tolerance': 6,
    'greed': 7,
    'honesty_bias': 4
}

# Get complete decision
decision = get_tiered_declaration(personality, MerchantTier.MEDIUM)

# decision contains:
# - declared_id, count, actual_ids (what to declare/carry)
# - lie, lie_type, strategy (metadata)
# - bribe_amount (calculated bribe, 0 if none)
```

### Building Declarations Directly

```python
from ai_strategy.declaration_builder import build_declaration

# Build specific strategy
declaration = build_declaration('contraband_low')

# Returns declaration dict (without bribe calculation)
```

### Calculating Bribes Directly

```python
from ai_strategy.bribe_strategy import calculate_scaled_bribe
from core.systems.game_master_state import MerchantTier

bribe = calculate_scaled_bribe(
    declared_good_id='cheese',
    declared_count=4,
    actual_good_ids=['silk', 'silk'],
    is_lying=True,
    personality={'risk_tolerance': 5, 'greed': 5, 'honesty_bias': 5},
    sheriff_stats={'inspection_rate': 0.5, 'catch_rate': 0.5},
    tier=MerchantTier.MEDIUM
)
```

## Personality Trait Effects

### Honesty Bias (0-10)
- **0-3**: Very dishonest, prefers contraband
- **4-6**: Balanced, adapts to situation
- **7-10**: Very honest, rarely lies

**Effect on Strategy**:
```python
risk_score -= (honesty / 2)  # Reduces risk-taking
```

### Risk Tolerance (0-10)
- **0-3**: Very cautious, prefers safe strategies
- **4-6**: Moderate, balanced risk/reward
- **7-10**: Bold, takes high risks

**Effect on Strategy**:
```python
risk_score += risk_tolerance  # Increases risk-taking
risk_factor = 1.0 - (risk / 40)  # Affects bribe (0.75-1.0)
```

### Greed (0-10)
- **0-3**: Not greedy, offers higher bribes
- **4-6**: Moderate, balanced
- **7-10**: Very greedy, offers lower bribes

**Effect on Strategy**:
```python
if greed > 7: risk_score += 2  # More willing to smuggle
greed_factor = 1.0 - (greed / 30)  # Affects bribe (0.67-1.0)
```

## Tier Assignment

Merchants are automatically assigned tiers based on personality:

```python
sophistication = risk_tolerance + greed - honesty_bias

if sophistication <= 5:
    tier = EASY
elif sophistication <= 10:
    tier = MEDIUM
else:
    tier = HARD
```

**Special Cases**:
- Information Brokers: Always HARD
- Can be overridden in character JSON

## Testing

### Unit Tests
```bash
python tests/test_bribe_improvements.py
python tests/test_bribe_scaling_detailed.py
```

### Test Coverage
- ✅ Game Master State recording/retrieval
- ✅ Bribe scaling with declared value
- ✅ Tiered merchant behavior
- ✅ Personality modifiers
- ✅ Advanced bluff strategy

## Best Practices

### Adding New Strategies

1. **Add declaration builder** in `declaration_builder.py`:
```python
def build_new_strategy() -> dict:
    # Build declaration
    return {
        'declared_id': ...,
        'count': ...,
        'actual_ids': ...,
        'lie': ...,
        'lie_type': ...,
        'strategy': 'new_strategy'
    }
```

2. **Update strategy mapping**:
```python
STRATEGY_BUILDERS = {
    ...
    'new_strategy': build_new_strategy,
}
```

3. **Add to tier selection logic** in `tiered_strategy.py`

### Modifying Bribe Logic

All bribe calculations should go through `bribe_strategy.py`:
- Maintain 70-110% of declared value principle
- Ensure merchant profits (bribe < contraband_value)
- Apply personality modifiers consistently

### Adding New Tiers

To add a new difficulty tier:
1. Add to `MerchantTier` enum in `game_master_state.py`
2. Update `get_history_for_tier()` with history slice size
3. Add tier selection logic in `tiered_strategy.py`
4. Update tier assignment in `merchants.py`

## Performance Considerations

- History slicing keeps memory usage reasonable
- All calculations are O(1) or O(n) where n is small
- Game Master State stores full history (consider pruning for 20+ merchants)

## Debugging

### Enable Verbose Logging

Add to merchant decision code:
```python
print(f"[DEBUG] {merchant.name} (tier: {tier.value})")
print(f"  Strategy: {decision['strategy']}")
print(f"  Declared: {decision['declared_id']} x{decision['count']}")
print(f"  Actual: {decision['actual_ids']}")
print(f"  Bribe: {decision.get('bribe_amount', 0)}g")
```

### Common Issues

**Bribes too high/low**:
- Check personality modifiers (greed, risk)
- Verify declared value calculation
- Check sheriff stats (inspection_rate affects bribe)

**Merchants too predictable**:
- Increase randomness in strategy selection
- Verify tier assignment (Easy merchants should be predictable)
- Check if Game Master State is updating

**Tier not working**:
- Verify `difficulty_tier` field in Merchant class
- Check tier assignment in `load_merchants()`
- Ensure `get_history_for_tier()` returns correct slice

## Future Enhancements

- **Dynamic Tier Adjustment**: Merchants "learn" and upgrade tiers
- **Reputation System**: Merchants remember sheriff across games
- **Sheriff AI**: Implement AI sheriff that learns patterns
- **Character-Specific Strategies**: Unique tactics per merchant
- **Bribe Negotiation AI**: More sophisticated counter-offers

## Summary

The AI strategy system provides:
- ✅ Tiered difficulty (Easy/Medium/Hard)
- ✅ Intelligent bribe scaling (prevents obvious tells)
- ✅ Personality-driven behavior
- ✅ Pattern recognition and adaptation
- ✅ Advanced bluff tactics (Hard AI)
- ✅ Centralized game state
- ✅ Clean, maintainable architecture

All merchants use the same core systems but behave differently based on their tier and personality, creating varied and interesting gameplay.
