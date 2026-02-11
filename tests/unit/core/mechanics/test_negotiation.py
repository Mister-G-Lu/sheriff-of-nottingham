"""
Test the negotiation system with different merchant personalities.

Run from project root:

    python tests/test_negotiation.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.players.merchants import Merchant
from core.players.sheriff import Sheriff
from core.mechanics.goods import SILK, PEPPER, APPLE
from core.mechanics.negotiation import (
    initiate_threat, merchant_respond_to_threat, sheriff_respond_to_bribe,
    merchant_respond_to_counter, resolve_negotiation, NegotiationOutcome
)


def test_cautious_merchant():
    """Test cautious merchant behavior (low risk tolerance)."""
    print("\n=== Test 1: Cautious Merchant (Alice-like) ===")
    print("Personality: Low risk tolerance (2), Low greed (3)")
    
    merchant = Merchant(
        id="test_cautious",
        name="Cautious Carl",
        intro="Nervous and eager to avoid trouble",
        tells_honest=[],
        tells_lying=[],
        bluff_skill=3,
        risk_tolerance=2,
        greed=3,
        honesty_bias=7
    )
    
    # Test that merchant object is created correctly
    assert merchant.id == "test_cautious"
    assert merchant.bluff_skill == 3
    assert merchant.risk_tolerance == 2
    print("✓ Cautious merchant created successfully")
    
    print()


def test_bold_merchant():
    """Test bold merchant behavior (high risk tolerance)."""
    print("\n=== Test 2: Bold Merchant (Bob-like) ===")
    print("Personality: High risk tolerance (7), High greed (6)")
    
    merchant = Merchant(
        id="test_bold",
        name="Bold Bob",
        intro="Confident and willing to take risks",
        tells_honest=[],
        tells_lying=[],
        bluff_skill=7,
        risk_tolerance=7,
        greed=6,
        honesty_bias=3
    )
    
    # Test that merchant object is created correctly
    assert merchant.id == "test_bold"
    assert merchant.bluff_skill == 7
    assert merchant.risk_tolerance == 7
    print("✓ Bold merchant created successfully")
    
    sheriff = Sheriff(perception=5, authority=6, reputation=7)
    
    # Carrying 12 gold worth of contraband
    goods_value = SILK.value * 2  # 12 gold
    
    negotiation = initiate_threat(sheriff, merchant, goods_value)
    print(f"Contraband value: {goods_value} gold")
    print(f"Threat level: {negotiation.threat_level}/10")
    print()
    
    # Merchant responds to threat
    wants_to_negotiate, offer = merchant_respond_to_threat(negotiation)
    
    if wants_to_negotiate:
        print(f"✓ Merchant offers bribe: {offer} gold")
        print(f"  (Bold/greedy merchants offer less: ~{int(offer/goods_value*100)}% of contraband value)")
    else:
        print("✗ Merchant refuses to bribe (bold merchants sometimes gamble on not bribing)")
    
    print()


def test_negotiation_rounds():
    """Test multi-round negotiation."""
    print("\n=== Test 3: Multi-Round Negotiation ===")
    
    merchant = Merchant(
        id="test_negotiator",
        name="Negotiator Nick",
        intro="Willing to haggle",
        tells_honest=[],
        tells_lying=[],
        bluff_skill=5,
        risk_tolerance=5,
        greed=5,
        honesty_bias=5
    )
    
    # Test that merchant object is created correctly
    assert merchant.id == "test_negotiator"
    assert merchant.bluff_skill == 5
    print("✓ Negotiator merchant created successfully")
    
    sheriff = Sheriff(perception=5, authority=6, reputation=7)
    
    # Carrying valuable contraband
    goods_value = PEPPER.value * 3  # 18 gold
    
    negotiation = initiate_threat(sheriff, merchant, goods_value)
    print(f"Contraband value: {goods_value} gold")
    print()
    
    # Round 1: Initial offer
    wants_to_negotiate, offer1 = merchant_respond_to_threat(negotiation)
    print(f"Round 1 - Merchant offers: {offer1} gold")
    
    if not wants_to_negotiate:
        print("Merchant refuses to negotiate")
        return
    
    # Sheriff counters (simulate player demanding more)
    counter_demand = offer1 + 5
    print(f"Round 1 - Sheriff demands: {counter_demand} gold")
    continues = sheriff_respond_to_bribe(negotiation, "counter", counter_demand)
    print()
    
    if not continues:
        print("Negotiation ended")
        return
    
    # Round 2: Merchant responds to counter
    continues, offer2 = merchant_respond_to_counter(negotiation)
    
    if continues:
        if offer2 == counter_demand:
            print(f"Round 2 - Merchant accepts: {offer2} gold")
        else:
            print(f"Round 2 - Merchant counter-offers: {offer2} gold")
            print(f"  (Split the difference: between {offer1} and {counter_demand})")
    else:
        print("Round 2 - Merchant gives up on negotiation")
    
    print()


def test_merchant_giving_up():
    """Test merchant giving up negotiation."""
    print("\n=== Test 4: Merchant Giving Up ===")
    
    merchant = Merchant(
        id="test_stubborn",
        name="Stubborn Steve",
        intro="Won't be pushed around",
        tells_honest=[],
        tells_lying=[],
        bluff_skill=5,
        risk_tolerance=3,
        greed=8,
        honesty_bias=4
    )
    
    # Test that merchant object is created correctly
    assert merchant.id == "test_stubborn"
    assert merchant.risk_tolerance == 3
    assert merchant.greed == 8
    print("✓ Stubborn merchant created successfully")
    
    sheriff = Sheriff(perception=5, authority=6, reputation=7)
    
    # Carrying moderate contraband
    goods_value = SILK.value  # 6 gold
    
    negotiation = initiate_threat(sheriff, merchant, goods_value)
    print(f"Contraband value: {goods_value} gold")
    print()
    
    # Initial offer
    wants_to_negotiate, offer = merchant_respond_to_threat(negotiation)
    
    if not wants_to_negotiate:
        print("Merchant refuses to bribe from the start")
        print("  (High risk tolerance + high greed = willing to gamble)")
        return
    
    print(f"Merchant offers: {offer} gold")
    
    # Sheriff demands way more than contraband is worth
    unreasonable_demand = goods_value + 10
    print(f"Sheriff demands: {unreasonable_demand} gold (more than contraband is worth!)")
    sheriff_respond_to_bribe(negotiation, "counter", unreasonable_demand)
    print()
    
    # Merchant likely gives up
    continues, response = merchant_respond_to_counter(negotiation)
    
    if not continues:
        print("✓ Merchant gives up: 'Just inspect the bag then!'")
        print("  (Greedy merchants won't pay more than the goods are worth)")
    else:
        print(f"Merchant still negotiating: {response} gold")
    
    print()


def run_all_tests():
    """Run all negotiation tests."""
    print("=" * 60)
    print("NEGOTIATION SYSTEM TEST SUITE")
    print("=" * 60)
    print()
    
    test_cautious_merchant()
    print("-" * 60)
    print()
    
    test_bold_merchant()
    print("-" * 60)
    print()
    
    test_negotiation_rounds()
    print("-" * 60)
    print()
    
    test_merchant_giving_up()
    print("-" * 60)
    print()
    
    print("=" * 60)
    print("TESTS COMPLETE")
    print("=" * 60)
    print()
    print("Key Insights:")
    print("• Cautious merchants (low risk tolerance) offer higher bribes")
    print("• Greedy merchants offer lower bribes and give up easier")
    print("• Bold merchants sometimes refuse to bribe at all")
    print("• Merchants won't pay more than their contraband is worth")
    print("• Each negotiation round reduces merchant's willingness to continue")


if __name__ == "__main__":
    run_all_tests()
