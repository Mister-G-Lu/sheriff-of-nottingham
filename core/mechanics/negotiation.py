"""Negotiation system: handle bribe offers, threats, and counter-offers between Sheriff and Merchant."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from core.players.merchants import Merchant
from core.players.sheriff import Sheriff


class NegotiationOutcome(str, Enum):
    """Possible outcomes of a negotiation."""

    BRIBE_ACCEPTED = "bribe_accepted"  # Sheriff accepts bribe, lets merchant pass
    BRIBE_REJECTED = "bribe_rejected"  # Sheriff rejects bribe, inspects anyway
    NO_BRIBE_OFFERED = "no_bribe_offered"  # Merchant refuses to bribe
    MERCHANT_GAVE_UP = "merchant_gave_up"  # Merchant gave up during negotiation


@dataclass
class NegotiationState:
    """Tracks the state of a negotiation between Sheriff and Merchant."""

    merchant: Merchant
    sheriff: Sheriff
    goods_value: int  # Total value of contraband in bag
    threat_level: int = 5  # How serious the inspection threat is (1-10)

    # Negotiation history
    merchant_offers: list[int] = None  # Gold amounts offered by merchant
    sheriff_demands: list[int] = None  # Gold amounts demanded by sheriff
    round_number: int = 1
    outcome: Optional[NegotiationOutcome] = None
    final_bribe_amount: int = 0

    def __post_init__(self):
        if self.merchant_offers is None:
            self.merchant_offers = []
        if self.sheriff_demands is None:
            self.sheriff_demands = []


def initiate_threat(
    sheriff: Sheriff, merchant: Merchant, goods_value: int
) -> NegotiationState:
    """Sheriff threatens to inspect. Returns negotiation state.

    Args:
        sheriff: The Sheriff character
        merchant: The Merchant being threatened
        goods_value: Total value of contraband in the bag

    Returns:
        NegotiationState object to track the negotiation
    """
    # Calculate threat level based on Sheriff's authority and reputation
    threat_level = min(10, (sheriff.authority + sheriff.reputation) // 2)

    return NegotiationState(
        merchant=merchant,
        sheriff=sheriff,
        goods_value=goods_value,
        threat_level=threat_level,
    )


def merchant_respond_to_threat(negotiation: NegotiationState) -> tuple[bool, int]:
    """Merchant decides whether to offer a bribe in response to threat.

    Args:
        negotiation: Current negotiation state

    Returns:
        Tuple of (wants_to_negotiate, bribe_offer_amount)
        If wants_to_negotiate is False, bribe_offer_amount will be 0
    """
    merchant = negotiation.merchant

    # Merchant decides whether to negotiate
    wants_to_negotiate = merchant.should_negotiate(
        threat_level=negotiation.threat_level,
        goods_value=negotiation.goods_value,
        round_number=negotiation.round_number,
    )

    if not wants_to_negotiate:
        negotiation.outcome = NegotiationOutcome.NO_BRIBE_OFFERED
        return False, 0

    # Calculate bribe offer
    bribe_amount = merchant.calculate_bribe_offer(
        goods_value=negotiation.goods_value, threat_level=negotiation.threat_level
    )

    negotiation.merchant_offers.append(bribe_amount)
    return True, bribe_amount


def sheriff_respond_to_bribe(
    negotiation: NegotiationState, player_choice: str, player_demand: int = 0
) -> bool:
    """Sheriff (player) responds to merchant's bribe offer.

    Args:
        negotiation: Current negotiation state
        player_choice: 'accept', 'reject', or 'counter'
        player_demand: If counter, the amount demanded (must be > last merchant offer)

    Returns:
        True if negotiation continues, False if it ends
    """
    if player_choice == "accept":
        negotiation.outcome = NegotiationOutcome.BRIBE_ACCEPTED
        negotiation.final_bribe_amount = negotiation.merchant_offers[-1]
        return False  # Negotiation ends

    elif player_choice == "reject":
        negotiation.outcome = NegotiationOutcome.BRIBE_REJECTED
        return False  # Negotiation ends, inspection happens

    elif player_choice == "counter":
        if player_demand <= negotiation.merchant_offers[-1]:
            # Invalid counter - must demand more than offered
            return True  # Continue negotiation, let player try again

        negotiation.sheriff_demands.append(player_demand)
        negotiation.round_number += 1
        return True  # Continue to next round

    return False


def merchant_respond_to_counter(negotiation: NegotiationState) -> tuple[bool, int]:
    """Merchant responds to Sheriff's counter-demand.

    Args:
        negotiation: Current negotiation state

    Returns:
        Tuple of (accepts_or_continues, new_offer_amount)
        - If accepts: (True, sheriff_demand) - pays the demanded amount
        - If gives up: (False, 0) - refuses and allows inspection
        - If continues: (True, new_offer) - makes a new counter-offer
    """
    merchant = negotiation.merchant
    sheriff_demand = negotiation.sheriff_demands[-1]
    original_offer = negotiation.merchant_offers[0]

    # First, check if merchant wants to continue negotiating at all
    wants_to_continue = merchant.should_negotiate(
        threat_level=negotiation.threat_level,
        goods_value=negotiation.goods_value,
        round_number=negotiation.round_number,
    )

    if not wants_to_continue:
        negotiation.outcome = NegotiationOutcome.MERCHANT_GAVE_UP
        return False, 0

    # Decide whether to accept the counter-demand
    accepts = merchant.should_accept_counter(
        sheriff_demand=sheriff_demand,
        original_offer=original_offer,
        goods_value=negotiation.goods_value,
    )

    if accepts:
        negotiation.outcome = NegotiationOutcome.BRIBE_ACCEPTED
        negotiation.final_bribe_amount = sheriff_demand
        return True, sheriff_demand

    # Make a new counter-offer (between last offer and sheriff's demand)
    last_offer = negotiation.merchant_offers[-1]
    # Offer something between last offer and demand, weighted by greed
    greed_factor = merchant.greed / 10  # 0 to 1
    increment = int(
        (sheriff_demand - last_offer) * (0.3 + greed_factor * 0.3)
    )  # 30-60% of gap
    new_offer = min(sheriff_demand - 1, last_offer + max(1, increment))

    negotiation.merchant_offers.append(new_offer)
    return True, new_offer


def resolve_negotiation(negotiation: NegotiationState) -> dict:
    """Get the final result of the negotiation.

    Returns:
        Dict with keys:
        - 'outcome': NegotiationOutcome enum value
        - 'bribe_paid': int (gold amount)
        - 'sheriff_inspects': bool
        - 'rounds': int (number of negotiation rounds)
    """
    inspects = negotiation.outcome in [
        NegotiationOutcome.BRIBE_REJECTED,
        NegotiationOutcome.NO_BRIBE_OFFERED,
        NegotiationOutcome.MERCHANT_GAVE_UP,
    ]

    return {
        "outcome": negotiation.outcome,
        "bribe_paid": negotiation.final_bribe_amount,
        "sheriff_inspects": inspects,
        "rounds": negotiation.round_number,
    }
