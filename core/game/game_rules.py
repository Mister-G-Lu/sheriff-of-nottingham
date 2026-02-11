"""
Game Rules and Constants
Defines the core Sheriff of Nottingham game rules
"""

# Starting resources
STARTING_GOLD = 50
BAG_SIZE_LIMIT = 6  # Maximum items a merchant can carry in their bag

# Penalty rules
CONFISCATION_PENALTY_RATE = 0.5  # Merchants pay 50% of confiscated goods' value

# Game flow
"""
Sheriff of Nottingham Rules:

1. MERCHANT TURN:
   - Draw cards from market until you have 6 cards total
   - Load 1-6 items into your bag
   - Declare what's in your bag (must declare ONE type of good and count)

2. DECLARATION RULES:
   - You can only declare LEGAL goods (apples, cheese, bread, chickens)
   - You must declare the count accurately if telling the truth
   - You can lie about what's in the bag

3. INSPECTION OUTCOMES:
   
   A. If you told the TRUTH:
      - All declared goods pass through (even if inspected)
      - You keep your goods and sell them
      - Sheriff loses reputation for wrongly inspecting honest merchant
   
   B. If you LIED and get CAUGHT:
      - ALL undeclared goods are confiscated (legal AND contraband)
      - You must pay the Sheriff HALF the value of confiscated goods
      - Sheriff gains reputation for catching a liar
      - Only truthfully declared goods pass through
   
   C. If you LIED and DON'T get caught:
      - All goods pass through
      - You profit from the lie
      - Sheriff loses reputation for missing contraband

4. GOLD SYSTEM:
   - Players start with 50 gold
   - Bribes cost gold
   - Penalties cost gold (half value of confiscated goods)
   - Selling goods earns gold
   - Running out of gold limits your options

5. BAG SIZE:
   - Maximum 6 items per bag
   - Merchants choose how many items to load (1-6)
   - More items = more profit but higher risk
"""


def calculate_confiscation_penalty(goods: list) -> int:
    """
    Calculate penalty for confiscated goods.
    
    Args:
        goods: List of Good objects that were confiscated
    
    Returns:
        int: Amount merchant must pay (50% of goods value)
    """
    total_value = sum(g.value for g in goods)
    return int(total_value * CONFISCATION_PENALTY_RATE)


def separate_declared_and_undeclared(actual_goods: list, declaration: dict) -> tuple[list, list]:
    """
    Separate goods into declared (truthful) and undeclared (lies/contraband).
    
    Args:
        actual_goods: List of Good objects in the bag
        declaration: Dict with 'good_id' and 'count'
    
    Returns:
        tuple: (declared_goods, undeclared_goods)
    """
    declared_id = declaration['good_id']
    declared_count = declaration['count']
    
    declared_goods = []
    undeclared_goods = []
    
    # Count how many of the declared good are actually in the bag
    declared_found = 0
    for good in actual_goods:
        if good.id == declared_id and declared_found < declared_count:
            declared_goods.append(good)
            declared_found += 1
        else:
            undeclared_goods.append(good)
    
    return declared_goods, undeclared_goods
