# Sheriff of Nottingham - Game Mechanics

## Overview

This document describes the complete Sheriff of Nottingham board game rules as implemented in the code, including core mechanics, bluff system, and inspection logic.

## Core Rules

### Starting Resources
- **Gold**: Each merchant starts with **50 gold**
- **Bag Size**: Maximum **6 items** per bag

### Game Flow

#### 1. Merchant Turn
1. Draw cards from market until you have 6 cards total
2. Load 1-6 items into your bag (cannot exceed 6 items)
3. Declare what's in your bag:
   - Must declare ONE type of LEGAL good (apples, cheese, bread, chickens)
   - Must declare the count
   - Can lie about contents

#### 2. Sheriff Decision
The sheriff can:
- **Pass**: Let merchant through without inspection
- **Inspect**: Open the bag and check contents
- **Threaten**: Attempt to negotiate a bribe

## Bluff System

### How It Works
When a merchant lies and gets inspected, a bluff check determines if the lie is caught:

1. **Sheriff rolls**: 1d10 + Perception
2. **Merchant rolls**: 1d10 + Bluff Skill
3. **Comparison**: If Sheriff's roll ≥ Merchant's roll, lie is caught

### Bluff Skill Values
- **Low (1-3)**: Easy to catch, poor liars
- **Medium (4-6)**: Average bluffing ability
- **High (7-9)**: Skilled liars, hard to catch
- **Expert (10+)**: Master bluffs, very difficult to detect

### Example Rolls
```
Scenario 1: Low Bluff Skill
Sheriff: 1d10(7) + 5 perception = 12
Merchant: 1d10(4) + 3 bluff = 7
Result: CAUGHT (12 ≥ 7)

Scenario 2: High Bluff Skill
Sheriff: 1d10(5) + 5 perception = 10
Merchant: 1d10(8) + 8 bluff = 16
Result: BLUFF SUCCEEDS (10 < 16)
```

### Catch Rate Probabilities

| Sheriff Perception | Merchant Bluff | Approximate Catch Rate |
|-------------------|----------------|------------------------|
| 5                 | 3              | ~70%                   |
| 5                 | 5              | ~50%                   |
| 5                 | 8              | ~30%                   |
| 8                 | 3              | ~90%                   |
| 8                 | 8              | ~50%                   |
| 3                 | 8              | ~20%                   |

*Note: Actual rates vary due to dice rolls (1-10)*

## Inspection Outcomes

### Partial Honesty Rule
Merchants can be partially honest. If they declare "3 apples" but have "2 apples + 1 silk", the 2 apples are considered truthfully declared and will pass through if caught.

### A. Fully Honest (Exact Match)
**Condition**: Bag exactly matches declaration

- **All goods pass through** (even though inspected)
- Merchant keeps everything and sells it
- Sheriff **loses reputation** for wrongly inspecting honest merchant
- No penalties

**Example:**
```
Declared: 4x apples
Actually had: 4x apples
Result: ✅ HONEST - All 4 apples pass through, merchant sells them
```

### B. Bluff Succeeds (Lie Not Caught)
**Condition**: Merchant lied but bluff roll beats sheriff's roll

- All goods pass through undetected
- Merchant profits from the lie
- Sheriff loses reputation for missing contraband

**Example:**
```
Benedict (Bluff: 9)
Declared: 3x apples
Has: 2x apples, 1x silk (6g contraband)

Sheriff roll: 1d10(4) + 5 = 9
Merchant roll: 1d10(7) + 9 = 16

Result: 🎭 BLUFF SUCCEEDS
- All goods pass through undetected
- Benedict sells: 2 apples + 1 silk = 10g profit
```

### C. Caught Lying
**Condition**: Merchant lied and sheriff's roll beats bluff

- **Separate declared goods from undeclared goods**
- **ALL undeclared goods are CONFISCATED** (legal AND contraband)
- Merchant must **pay Sheriff HALF the value** of confiscated goods
- Only truthfully declared goods pass through
- Sheriff gains reputation

**Example 1: Partial Honesty**
```
Declared: 3x apples
Actually had: 2x apples, 1x silk (contraband)

Result:
- 2 apples pass through (truthfully declared)
- 1 silk confiscated
- Merchant pays Sheriff: silk_value * 0.5 = penalty
- Merchant sells the 2 apples that passed
```

**Example 2: Caught with Legal Goods**
```
Declared: 2x cheese
Actually had: 3x cheese, 1x bread

Result:
- 2 cheese pass through (truthfully declared)
- 1 cheese + 1 bread confiscated (undeclared, even though legal!)
- Merchant pays penalty for confiscated goods
- Merchant sells the 2 cheese that passed
```

**Example 3: Detailed Scenario**
```
Cedric (Bluff: 3)
Declared: 3x bread
Has: 1x bread, 2x pepper (contraband)

Sheriff roll: 1d10(8) + 5 = 13
Merchant roll: 1d10(2) + 3 = 5

Result: ❌ CAUGHT LYING
- 1 bread passes (truthfully declared)
- 2 pepper confiscated (10g value)
- Penalty: 5g (50% of 10g)
- Cedric sells: 1 bread = 4g
- Net result: -1g (lost 5g penalty, gained 4g)
```

## Gold System

### Earning Gold
- Selling goods that pass through inspection
- Receiving bribes (Sheriff)
- Receiving penalties from caught liars (Sheriff)

### Spending Gold
- Paying bribes to Sheriff
- Paying penalties when caught lying

### Running Out of Gold
- Merchants with low gold cannot afford large bribes
- Penalties are capped at merchant's available gold
- Gold becomes a strategic resource

## Strategic Implications

### For Merchants

**High Bluff Skill (8+)**:
- Can lie more safely
- Higher chance of getting contraband through
- Worth taking bigger risks

**Low Bluff Skill (1-3)**:
- Should be more honest
- Risky to smuggle contraband
- Better to use legal goods strategies

**Medium Bluff Skill (4-7)**:
- Balanced approach
- Occasional lies can work
- Need to read sheriff's behavior

**General Strategies**:
- **Honest strategy**: Safe, guaranteed profit, no penalties
- **Legal goods lying**: Moderate risk (e.g., declare 2 apples, carry 4)
- **Contraband smuggling**: High risk, high reward
- **Partial honesty**: Declare some truth to minimize losses if caught
- **Gold management**: Keep enough for bribes and penalties

### For Sheriff

**High Perception (8+)**:
- Better at catching lies
- More confident inspections
- Can catch even skilled bluffers

**Low Perception (1-3)**:
- Harder to catch lies
- Skilled merchants will fool you
- Need to be more selective

**General Strategies**:
- **Know the merchants**: Check their bluff skills
- **Upgrade perception**: Makes catching lies easier
- **Watch for patterns**: Skilled bluffers may get greedy
- **Inspect honest merchants**: Lose reputation
- **Catch liars**: Gain reputation + penalty payment
- **Accept bribes**: Gain gold, lose reputation
- **Miss contraband**: Lose reputation

## Implementation Details

### Bag Size Limit
```python
BAG_SIZE_LIMIT = 6  # Maximum items per bag
```

### Penalty Calculation
```python
penalty = sum(confiscated_goods_values) * 0.5
actual_penalty = min(penalty, merchant.gold)  # Can't pay more than you have
```

### Goods Separation
When caught lying, the game separates:
1. **Declared goods**: Match the declaration (pass through)
2. **Undeclared goods**: Everything else (confiscated)

### Inspection Flow
```python
1. Check if fully honest (exact match)
   → If yes: All goods pass

2. Separate declared vs undeclared goods

3. Roll bluff check:
   sheriff_roll = 1d10 + perception
   merchant_roll = 1d10 + bluff_skill

4. Compare rolls:
   if sheriff_roll >= merchant_roll:
       → Caught! Confiscate undeclared goods
   else:
       → Bluff succeeds! All goods pass
```

## Code Modules

- **`core/game/game_rules.py`**: Constants and rule calculations
- **`core/mechanics/inspection.py`**: Inspection logic with bluff checks
- **`core/players/merchants.py`**: Merchant class with `roll_bluff()` method
- **`core/game/game_manager.py`**: Main game loop and display logic
