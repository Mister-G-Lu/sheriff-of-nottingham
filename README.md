# Sheriff of Nottingham - Interactive Inspector Game

A Pygame-based inspector game where you play as the Sheriff of Nottingham, deciding which merchants to inspect while navigating bribes, negotiations, and strategic AI opponents.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the game
python main.py

# Build executable (macOS)
./build.sh
```

## 📁 Project Structure

```
sheriff-of-nottingham/
├── main.py                 # Entry point - minimal, just UI setup
├── core/                   # Game logic (DO NOT add UI code here)
│   ├── game_manager.py     # Main game loop
│   ├── merchants.py        # Merchant class & loading
│   ├── goods.py            # Legal goods & contraband definitions
│   ├── negotiation.py      # Bribery negotiation system
│   ├── sheriff.py          # Sheriff state (reputation, authority)
│   ├── black_market.py     # Black market encounter system
│   ├── game_stats.py       # Statistics tracking
│   └── strategy/           # Merchant strategy modules
│       └── legal_goods_strategy.py  # Legal goods lying strategy
├── ai_strategy/            # Advanced AI strategies
│   └── silas_strategy.py   # Silas Voss (Information Broker) AI
├── ui/                     # All UI code (Pygame)
│   ├── pygame_ui.py        # Core UI components
│   ├── menu.py             # Main menu
│   └── narration.py        # Text display & prompts
├── characters/             # Merchant data
│   ├── data/*.json         # Merchant definitions
│   └── portraits/*.txt     # ASCII art portraits
└── tests/                  # Test suite
```

## 🎮 Core Game Systems

### 1. Game Loop (`core/game_manager.py`)
- **Main function**: `run_game()`
- Iterates through merchants, handles decisions, tracks history
- Each merchant uses their own strategy via `merchant.choose_declaration(history)`

### 2. Merchant Strategy System
Merchants make strategic decisions about what to carry and declare:

**Base Merchant** (`core/merchants.py`):
- `choose_declaration(history)` - Returns declaration dict
- Default: Simple random honest/dishonest behavior

**Information Broker** (`core/merchants.py` + `ai_strategy/silas_strategy.py`):
- Analyzes sheriff behavior patterns (inspection rate, catch rate)
- Adapts strategy: tells truth when dangerous, smuggles when safe
- Scales contraband count (1-2 items) based on risk
- Selects contraband value based on safety assessment

**Legal Goods Lying** (`core/strategy/legal_goods_strategy.py`):
- Declares homogeneous bag (e.g., "3x Cheese")
- Actually carries mixed bag (e.g., "2x Cheese + 1x Chicken")
- Lower risk than contraband, moderate profit

### 3. Goods System (`core/goods.py`)
```python
# Legal goods (can be declared)
APPLE, CHEESE, BREAD, CHICKEN

# Contraband (cannot be declared)
SILK, PEPPER, MEAD, CROSSBOW

# Each has: id, name, kind, value
```

### 4. Negotiation System (`core/negotiation.py`)
- Multi-round bribery negotiations
- Merchants calculate bribes based on contraband value
- Sheriff can accept, reject, or counter-offer
- Merchants may give up if demands too high

## 🔧 Development Guide

### Adding New Merchants

Create `characters/data/yourmerchant.json`:
```json
{
  "id": "yourmerchant",
  "name": "Your Merchant Name",
  "personality": "Brief personality description",
  "lore": "Background story",
  "tells_honest": ["calm demeanor", "steady voice"],
  "tells_lying": ["fidgets", "avoids eye contact"],
  "bluff_skill": 5,
  "portrait_file": "yourmerchant.txt",
  "appearance": "Visual description for portraits"
}
```

**Special Merchant Types:**
- Set `"role": "broker"` to create an Information Broker (uses `ai_strategy/silas_strategy.py`)
- Override `choose_declaration()` method for custom strategies

### Adding New Strategies

1. Create strategy module in `core/strategy/` or `ai_strategy/`
2. Implement decision logic that returns:
   ```python
   {
       "declared_id": str,      # What good to declare
       "count": int,            # How many items
       "actual_ids": list[str], # What's actually in bag
       "lie": bool              # Is this a lie?
   }
   ```
3. Use `history` parameter to analyze sheriff behavior patterns

### Key Design Principles

1. **Separation of Concerns**: 
   - `main.py` = minimal entry point
   - `core/` = pure game logic (no UI)
   - `ui/` = all Pygame/display code

2. **Strategy Pattern**: 
   - Merchants use `choose_declaration(history)` for decisions
   - History allows adaptive AI (learning from past encounters)

3. **History Tracking**:
   - Each encounter records: declaration, actual goods, opened, caught_lie
   - Strategic merchants (like Silas) analyze this to adapt

### Testing

```bash
# Run negotiation tests
python tests/test_negotiation.py

# Test specific merchant strategies
python -c "from core.merchants import load_merchants; print(load_merchants())"
```

## 📚 Key Files for Development

| File | Purpose |
|------|---------|
| `core/game_manager.py` | Main game loop - start here to understand flow |
| `core/merchants.py` | Merchant class, loading, strategy interface |
| `ai_strategy/silas_strategy.py` | Example of sophisticated adaptive AI |
| `core/strategy/legal_goods_strategy.py` | Example of risk-based strategy |
| `core/negotiation.py` | Bribery negotiation state machine |
| `ui/narration.py` | All text display and user prompts |

## 🎯 How the Game Works

1. **Game Loop** (`run_game()` in `game_manager.py`):
   - Load 8 merchants randomly
   - For each merchant:
     - Call `build_bag_and_declaration(merchant, history)`
     - Show declaration and tells
     - Player decides: accept bribe, pass, inspect, or threaten
     - Record outcome in history
   - Show end game summary

2. **Merchant Decision Flow**:
   ```
   merchant.choose_declaration(history)
   ↓
   [Base Merchant: random honest/lie]
   [Information Broker: analyze patterns → strategic decision]
   ↓
   Returns: {declared_id, count, actual_ids, lie}
   ```

3. **History-Based Learning**:
   - Silas analyzes: inspection_rate, catch_rate
   - Adjusts: truth/lie decision, contraband count, contraband value
   - Result: Adaptive difficulty that responds to player behavior

# Rejected ideas

Dynamic market price - might be too complex
Multiplayer - servers are hard to manage

## 🔮 Future Development Ideas

- Save/load game state - encryption how? Secret obtained from file metadata?
- Merchant/Sheriff reputation across sessions

---

**For detailed merchant expansion guide, see:** `docs/MERCHANT_EXPANSION_GUIDE.md`
