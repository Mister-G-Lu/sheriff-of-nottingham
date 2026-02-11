"""
Interactive demo showing the new negotiation system.

This script demonstrates how merchants with different personalities
respond to threats and negotiate bribes.

Run from project root:
    python demo_negotiation.py
"""

from core.players.merchants import load_merchants
from core.players.sheriff import Sheriff
from core.mechanics.goods import SILK, PEPPER, CROSSBOW, APPLE
from core.mechanics.negotiation import (
    initiate_threat, merchant_respond_to_threat, sheriff_respond_to_bribe,
    merchant_respond_to_counter, resolve_negotiation, NegotiationOutcome
)


def demo_scenario(merchant, sheriff, contraband_items, scenario_name):
    """Run a negotiation scenario and show the results."""
    print(f"\n{'='*70}")
    print(f"SCENARIO: {scenario_name}")
    print(f"{'='*70}")
    print(f"\nMerchant: {merchant.name}")
    print(f"Personality: {merchant.personality}")
    print(f"Traits: Risk={merchant.risk_tolerance}, Greed={merchant.greed}, Honesty={merchant.honesty_bias}")
    print(f"\nContraband in bag: {', '.join(g.name for g in contraband_items)}")
    
    goods_value = sum(g.value for g in contraband_items)
    print(f"Total value: {goods_value} gold")
    print()
    
    # Sheriff threatens
    print("🔍 Sheriff: 'That bag looks suspicious. I think I need to inspect it.'")
    print()
    
    # Start negotiation
    negotiation = initiate_threat(sheriff, merchant, goods_value)
    print(f"[Threat Level: {negotiation.threat_level}/10]")
    print()
    
    # Merchant responds
    wants_to_negotiate, initial_offer = merchant_respond_to_threat(negotiation)
    
    if not wants_to_negotiate:
        print(f"💪 {merchant.name}: 'I have nothing to hide. Inspect if you must.'")
        print(f"\n❌ Result: Merchant refuses to bribe (bold/honest personality)")
        return
    
    print(f"💰 {merchant.name}: 'Perhaps... {initial_offer} gold would help you see everything is in order?'")
    print(f"   [Offering {int(initial_offer/goods_value*100)}% of contraband value]")
    print()
    
    # Simulate sheriff counter-offer
    if initial_offer < goods_value * 0.3:
        # Low offer, demand more
        counter_demand = initial_offer + (goods_value // 3)
        print(f"⚖️  Sheriff counters: 'I want {counter_demand} gold.'")
        sheriff_respond_to_bribe(negotiation, "counter", counter_demand)
        print()
        
        # Merchant responds to counter
        continues, merchant_response = merchant_respond_to_counter(negotiation)
        
        if not continues:
            print(f"😤 {merchant.name}: 'This is too much. Just inspect the bag and be done with it.'")
            print(f"\n❌ Result: Merchant gives up (greedy/bold personality)")
        elif merchant_response == counter_demand:
            print(f"😰 {merchant.name}: 'Fine... {merchant_response} gold it is.'")
            print(f"\n✅ Result: Bribe accepted at {merchant_response} gold (cautious personality)")
        else:
            print(f"🤝 {merchant.name}: 'How about {merchant_response} gold instead?'")
            print(f"   [Counter-offering {int(merchant_response/goods_value*100)}% of value]")
            print(f"\n🔄 Result: Negotiation continues (moderate personality)")
    else:
        # Reasonable offer, accept it
        sheriff_respond_to_bribe(negotiation, "accept", 0)
        print(f"✅ Sheriff accepts: {initial_offer} gold")
        print(f"\n✅ Result: Bribe accepted (merchant offered fair amount)")
    
    print()


def main():
    """Run demonstration scenarios."""
    print("\n" + "="*70)
    print("SHERIFF OF NOTTINGHAM - NEGOTIATION SYSTEM DEMO")
    print("="*70)
    print("\nThis demo shows how different merchant personalities affect negotiation.")
    print("Watch how cautious, moderate, and bold merchants behave differently!")
    
    # Load merchants
    merchants = load_merchants()
    sheriff = Sheriff(perception=5, authority=6, reputation=7)
    
    # Find specific merchants for demos
    alice = next((m for m in merchants if m.id == "alice"), None)
    bob = next((m for m in merchants if m.id == "bob"), None)
    cedric = next((m for m in merchants if m.id == "cedric"), None)
    broker = next((m for m in merchants if m.id == "info-broker"), None)
    
    # Scenario 1: Cautious merchant with moderate contraband
    if alice:
        demo_scenario(
            alice, sheriff,
            [SILK, SILK],  # 12 gold worth
            "Cautious Merchant with Moderate Contraband"
        )
    
    # Scenario 2: Bold merchant with high-value contraband
    if bob:
        demo_scenario(
            bob, sheriff,
            [CROSSBOW, PEPPER],  # 14 gold worth
            "Bold Merchant with High-Value Contraband"
        )
    
    # Scenario 3: Greedy merchant with low-value contraband
    if cedric:
        demo_scenario(
            cedric, sheriff,
            [SILK],  # 6 gold worth
            "Greedy Merchant with Low-Value Contraband"
        )
    
    # Scenario 4: Information broker with multiple items
    if broker:
        demo_scenario(
            broker, sheriff,
            [PEPPER, PEPPER, SILK],  # 18 gold worth
            "Information Broker with Multiple Contraband"
        )
    
    # Summary
    print("\n" + "="*70)
    print("DEMO COMPLETE - KEY INSIGHTS")
    print("="*70)
    print("""
🎯 Personality Traits Drive Behavior:
   • Cautious merchants (low risk) → Offer generous bribes quickly
   • Bold merchants (high risk) → Sometimes refuse to bribe at all
   • Greedy merchants (high greed) → Offer minimal bribes, give up easily
   • Moderate merchants → Create interesting back-and-forth negotiations

💰 Bribe Calculation is Smart:
   • Based on contraband value (not random)
   • Adjusted by merchant greed level
   • Scaled by threat level from Sheriff
   • Merchants won't overpay for low-value goods

🤝 Multi-Round Negotiation:
   • Sheriff can accept, reject, or counter-offer
   • Merchants evaluate each counter-demand
   • Each round reduces merchant's willingness
   • Merchants give up when demands are unreasonable

🎲 AI Decision-Making:
   • Personality traits create unique behaviors
   • Merchants calculate risk vs. reward
   • Different merchants = different strategies
   • Unpredictable outcomes keep gameplay interesting
    """)
    
    print("="*70)
    print("\n💡 Try playing the full game: python main.py")
    print("📖 Add your own merchants: see MERCHANT_EXPANSION_GUIDE.md\n")


if __name__ == "__main__":
    main()
