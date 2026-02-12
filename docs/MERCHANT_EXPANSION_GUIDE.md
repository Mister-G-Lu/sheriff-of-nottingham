# Merchant Expansion Guide

## Overview
The Sheriff of Nottingham game now has a standardized merchant system with personality-driven AI decision-making and a dynamic negotiation system. This guide explains how to add new merchants and customize their behavior.

## What's New

### 1. **Personality Traits System**
Every merchant now has three core traits (0-10 scale):

- **`risk_tolerance`**: Willingness to smuggle and gamble on not bribing
  - `0-3`: Cautious (will almost always bribe when threatened)
  - `4-6`: Moderate (balanced approach)
  - `7-10`: Bold (often refuses to bribe, willing to risk inspection)

- **`greed`**: Desire for profit (affects bribe calculations)
  - `0-3`: Generous (offers higher bribes)
  - `4-6`: Moderate
  - `7-10`: Greedy (offers minimal bribes, gives up easily)

- **`honesty_bias`**: Tendency to be honest
  - `0-3`: Dishonest (frequently smuggles)
  - `4-6`: Opportunistic
  - `7-10`: Honest (rarely smuggles)

### 2. **Threat-Based Negotiation System**
Bribes are no longer offered upfront. Instead:

1. **Sheriff threatens to inspect** → Merchant evaluates situation
2. **Merchant decides**: Offer bribe OR refuse and allow inspection
3. **If bribe offered**: Sheriff can accept, reject, or counter-demand
4. **Multi-round negotiation**: Merchant can counter-offer or give up
5. **AI decision-making**: Merchant personality determines strategy

### 3. **AI Decision Methods**

Merchants now have intelligent decision-making:

- **`calculate_bribe_offer(goods_value, threat_level)`**: Calculates appropriate bribe amount
- **`should_negotiate(threat_level, goods_value, round_number)`**: Decides whether to offer bribe
- **`should_accept_counter(sheriff_demand, original_offer, goods_value)`**: Decides whether to accept counter-offer or give up

## Adding New Merchants

### Step 1: Create Character JSON

Create a new file in `characters/` directory (e.g., `characters/donna.json`):

```json
{
  "id": "donna",
  "name": "Donna the Daring",
  "personality": "Fearless smuggler who thrives on danger",
  "lore": "A former pirate who now runs goods through Nottingham's gates",
  "tells_honest": [
    "relaxed posture",
    "steady breathing",
    "casual smile"
  ],
  "tells_lying": [
    "hand on weapon",
    "too much eye contact",
    "whistles nervously"
  ],
  "bluff_skill": 8,
  "risk_tolerance": 9,
  "greed": 7,
  "honesty_bias": 2,
  "portrait_file": "donna.txt",
  "appearance": "Weathered woman with a scar across her cheek and a confident stance"
}
```

### Step 2: Create ASCII Portrait (Optional)

Create `characters/donna.txt` with ASCII art:

```
    ___
   /   \
  | O O |
   \\_-_/
    |||
```

### Step 3: Test Your Merchant

Run the game and observe how your merchant behaves based on their traits:

```bash
python main.py
```

## Merchant Personality Archetypes

### The Honest Trader (Alice)
```json
"risk_tolerance": 2,
"greed": 3,
"honesty_bias": 8
```
- Rarely smuggles contraband
- When caught, offers generous bribes quickly
- Accepts counter-demands easily

### The Bold Smuggler (Bob)
```json
"risk_tolerance": 7,
"greed": 6,
"honesty_bias": 3
```
- Frequently smuggles high-value contraband
- Often refuses to bribe, gambling on passing inspection
- Offers low bribes when threatened
- Gives up negotiation if demands are too high

### The Calculating Opportunist (Cedric)
```json
"risk_tolerance": 5,
"greed": 7,
"honesty_bias": 6
```
- Smuggles when opportunity is good
- Very greedy - offers minimal bribes
- Will negotiate but won't overpay

### The Information Broker (Silas)
```json
"risk_tolerance": 6,
"greed": 8,
"honesty_bias": 2
```
- Uses special logic (see `InformationBroker` class)
- Analyzes patterns in previous rounds
- Adapts strategy based on what worked before

## Advanced: Custom Merchant Classes

For merchants with unique behavior, create a subclass:

```python
class SpecialMerchant(Merchant):
    """A merchant with unique negotiation strategy."""
    
    def should_negotiate(self, threat_level: int, goods_value: int, round_number: int = 1) -> bool:
        # Custom logic here
        if goods_value > 20:
            return True  # Always negotiate for high-value goods
        return super().should_negotiate(threat_level, goods_value, round_number)
    
    def calculate_bribe_offer(self, goods_value: int, threat_level: int = 5) -> int:
        # Custom bribe calculation
        return goods_value // 2  # Offers exactly half the value
```

Then update `load_merchants()` in `core/merchants.py` to recognize your new role:

```python
role = data.get("role")
cls = Merchant
if role == "broker":
    cls = InformationBroker
elif role == "special":
    cls = SpecialMerchant
```

## Negotiation Flow Example

```
1. Sheriff: "That bag looks suspicious. I think I need to inspect it."
   
2. Merchant (evaluates):
   - Contraband value: 12 gold
   - Risk tolerance: 3 (cautious)
   - Greed: 4 (moderate)
   - Threat level: 7/10 (high)
   → Decision: Offer bribe

3. Merchant: "Perhaps... 5 gold would help you see everything is in order?"

4. Sheriff options:
   [a] Accept (take 5 gold, let pass)
   [r] Reject (inspect anyway)
   [c] Counter (demand more)

5. If counter (e.g., demand 8 gold):
   Merchant evaluates:
   - Original offer: 5 gold
   - Demand: 8 gold
   - Contraband value: 12 gold
   - Greed: 4 (moderate)
   → Decision: Accept or counter with 6-7 gold

6. Negotiation continues until:
   - Sheriff accepts
   - Sheriff rejects
   - Merchant gives up
   - Max rounds reached (3)
```

## Testing Your Merchants

Use the test script to verify behavior:

```bash
python tests/test_negotiation.py
```

Or create custom tests:

```python
from core.merchants import Merchant
from core.sheriff import Sheriff
from core.negotiation import initiate_threat, merchant_respond_to_threat

merchant = Merchant(
    id="test", name="Test", personality="", lore="",
    tells_honest=[], tells_lying=[],
    bluff_skill=5, risk_tolerance=7, greed=8, honesty_bias=3
)

sheriff = Sheriff(perception=5, authority=6, reputation=7)
negotiation = initiate_threat(sheriff, merchant, goods_value=15)
wants_to_negotiate, offer = merchant_respond_to_threat(negotiation)

print(f"Negotiates: {wants_to_negotiate}, Offers: {offer} gold")
```

## Tips for Balanced Merchants

1. **High risk + High greed = Unpredictable**: Sometimes refuses to bribe entirely
2. **Low risk + Low greed = Reliable briber**: Always offers generous bribes
3. **Moderate traits = Interesting negotiations**: Creates dynamic back-and-forth
4. **Bluff skill affects detection**: High bluff = harder for Sheriff to catch lies
5. **Balance the roster**: Mix cautious, moderate, and bold merchants for variety

## Future Expansion Ideas

- **Reputation tracking**: Merchants remember past interactions
- **Dynamic traits**: Traits change based on success/failure
- **Merchant relationships**: Some merchants work together
- **Special items**: Certain contraband triggers different behavior
- **Time pressure**: Limited time to negotiate adds urgency
- **Merchant moods**: Random daily mood affects willingness to negotiate
