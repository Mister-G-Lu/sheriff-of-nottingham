"""
Sheriff Behavior Analysis Utilities

Shared utilities for analyzing sheriff behavior patterns from encounter history.
Used by both base merchants and sophisticated strategists like Silas.
"""


def calculate_catch_rate(history: list[dict]) -> float:
    """
    Calculate simple catch rate: % of liars caught by sheriff.
    
    Used by base merchants for simple risk assessment.
    
    Args:
        history: List of previous encounters with keys:
            - 'declaration': {'good_id': str, 'count': int}
            - 'actual_ids': list[str]
            - 'caught_lie': bool
            - 'opened': bool
    
    Returns:
        float: Catch rate from 0.0 to 1.0 (default 0.5 if no data)
    """
    if not history:
        return 0.5  # Default assumption
    
    # Count total lies and caught lies
    total_lies = 0
    lies_caught = 0
    
    for h in history:
        decl = h.get('declaration', {})
        actual_ids = h.get('actual_ids', [])
        
        # Check if this was a lie
        is_lie = (len(actual_ids) != decl.get('count') or
                 any(aid != decl.get('good_id') for aid in actual_ids))
        
        if is_lie:
            total_lies += 1
            if h.get('caught_lie'):
                lies_caught += 1
    
    # Calculate catch rate
    if total_lies > 0:
        return lies_caught / total_lies
    return 0.5  # No lies yet, assume 50%


def analyze_sheriff_detailed(history: list[dict]) -> dict:
    """
    Detailed sheriff behavior analysis with multiple metrics.
    
    Used by sophisticated strategists (like Silas) for advanced decision-making.
    Tracks both inspection patterns and catch effectiveness.
    
    Args:
        history: List of previous encounters with keys:
            - 'declaration': {'good_id': str, 'count': int}
            - 'actual_ids': list[str]
            - 'caught_lie': bool
            - 'opened': bool
    
    Returns:
        dict with keys:
            - inspection_rate: % of merchants inspected (0.0 to 1.0)
            - catch_rate: % of smugglers caught (0.0 to 1.0)
            - total_rounds: Number of encounters analyzed
            - lies_caught: Number of smugglers caught
            - lies_successful: Number of smugglers who got through
            - truths_inspected: Number of honest merchants inspected
    """
    total_rounds = len(history)
    lies_caught = 0
    lies_successful = 0
    truths_inspected = 0
    
    if not history:
        # Return default values if no history
        return {
            'inspection_rate': 0.5,
            'catch_rate': 0.5,
            'total_rounds': 0,
            'lies_caught': 0,
            'lies_successful': 0,
            'truths_inspected': 0
        }
    
    for item in history:
        decl = item.get("declaration", {})
        actual = item.get("actual_ids", [])
        was_opened = item.get("opened", False)
        caught = item.get("caught_lie", False)
        
        # Determine if merchant was honest
        declared_ok = (
            decl.get("count") == len(actual)
            and all(a == decl.get("good_id") for a in actual)
        )
        
        if declared_ok:
            # Honest merchant
            if was_opened:
                truths_inspected += 1
        else:
            # Lying merchant
            if caught:
                lies_caught += 1
            else:
                lies_successful += 1
    
    # Calculate key metrics
    total_inspections = lies_caught + truths_inspected
    inspection_rate = total_inspections / total_rounds if total_rounds > 0 else 0.5
    
    total_lies = lies_caught + lies_successful
    catch_rate = lies_caught / total_lies if total_lies > 0 else 0.5
    
    return {
        'inspection_rate': inspection_rate,
        'catch_rate': catch_rate,
        'total_rounds': total_rounds,
        'lies_caught': lies_caught,
        'lies_successful': lies_successful,
        'truths_inspected': truths_inspected
    }
