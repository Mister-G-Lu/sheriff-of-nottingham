# Merchant Characters

Character data for Sheriff of Nottingham merchants.

## 📁 Files
- **`data/*.json`** - Character data and stats
- **`portraits/*.png`** - Character portraits

## 🎮 Merchant Strategy Types

Merchants use four main strategies based on their personality:

### **1. Full Honest** (Safest, Low Reward)
- Declare exactly what they carry
- All legal goods, truthful count
- **Risk**: None | **Reward**: Low
- **Example**: Diana (Honesty: 9), Alice (Honesty: 8)

### **2. Legal Goods Lie** (Low Risk, Moderate Reward)
- Declare one legal good, carry mix of legal goods
- Example: Declare "3 apples", actually have "2 apples + 1 bread"
- **Risk**: Low (no contraband) | **Reward**: Moderate
- **Example**: Edmund (Honesty: 6), Cedric (Honesty: 6)

### **3. Some Contraband** (Moderate Risk, High Reward)
- Declare legal goods, sneak 1-2 contraband items
- Example: Declare "3 cheese", actually have "2 cheese + 1 silk"
- **Risk**: Moderate | **Reward**: High
- **Example**: Fiona (Honesty: 4), Bob (Honesty: 3)

### **4. Full Contraband** (Very Risky, Highest Reward)
- Declare legal goods, carry all contraband
- Example: Declare "3 apples", actually have "3 crossbows"
- **Risk**: Very High | **Reward**: Highest
- **Example**: Garrett (Honesty: 3), Silas (Honesty: 1)

## 🎭 Merchant Roster

### Easy ⭐⭐
- **Diana** (Bluff: 1) - Tutorial merchant, almost always honest, terrible liar
- **Alice** (Bluff: 3) - Nervous baker, rarely lies, obvious tells

### Medium ⭐⭐⭐
- **Edmund** (Bluff: 4) - Friendly fishmonger, occasional smuggler
- **Bob** (Bluff: 7) - Bold trader, frequent smuggler, gambler
- **Cedric** (Bluff: 5) - Greedy blacksmith, won't overpay bribes

### Hard ⭐⭐⭐⭐⭐
- **Fiona** (Bluff: 6) - Calculating seamstress, subtle tells
- **Garrett** (Bluff: 7) - Veteran with poker face, identical tells

### Expert ⭐⭐⭐⭐⭐⭐
- **Silas** (Bluff: 9) - Information broker, adaptive AI, learns your behavior

## 📊 Key Stats

**Bluff Skill** (1-10): Ability to deceive
- 1-3: Poor liar, obvious tells
- 4-6: Average deceiver
- 7-10: Expert liar, subtle/no tells

**Honesty Bias** (1-10): Tendency to be truthful
- 1-3: Frequent smuggler (contraband strategy)
- 4-6: Opportunistic (mixed strategy)
- 7-10: Mostly honest (honest/legal lie strategy)

**Risk Tolerance** (1-10): Willingness to gamble
- 1-3: Cautious, offers bribes easily
- 4-6: Balanced approach
- 7-10: Bold, may refuse bribes

**Greed** (1-10): Affects bribe amounts
- 1-3: Generous bribes
- 4-6: Moderate bribes
- 7-10: Minimal bribes, gives up easily

## 🔧 Adding Merchants

Create `data/merchant-name.json`:
```json
{
  "id": "unique-id",
  "name": "Display Name",
  "tells_honest": ["relaxed posture", "steady voice"],
  "tells_lying": ["fidgets", "avoids eye contact"],
  "bluff_skill": 5,
  "risk_tolerance": 5,
  "greed": 5,
  "honesty_bias": 5,
  "portrait_file": "portrait.png"
}
```

**Difficulty Guidelines:**
- Easy: Bluff + Risk < 8
- Medium: Bluff + Risk 8-14
- Hard: Bluff + Risk 15-18
- Expert: Bluff + Risk > 18

## 📚 See Also
- **MERCHANT_EXPANSION_GUIDE.md** - Detailed creation guide
- **../docs/GAME_MECHANICS.md** - Game rules and mechanics
