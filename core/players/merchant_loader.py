"""
Merchant Loading
Handles loading merchant data from JSON files
"""

import json
import random
from pathlib import Path
from typing import Optional
from core.systems.logger import log_error, log_warning, log_info, log_debug


def characters_dir() -> Path:
    """Return the path to the characters directory."""
    return Path(__file__).parent.parent / "characters"


def load_merchants(limit: Optional[int] = None) -> list:
    """
    Load merchants from characters/data/*.json, randomly ordered.
    
    Args:
        limit: Optional maximum number of merchants to load
    
    Returns:
        list: List of Merchant objects (randomly ordered)
    """
    from core.players.merchants import Merchant, InformationBroker
    
    chars_dir = characters_dir() / "data"
    if not chars_dir.exists():
        log_warning(f"Characters directory not found: {chars_dir}")
        return []

    jsons = list(chars_dir.glob("*.json"))
    if not jsons:
        log_warning(f"No merchant JSON files found in {chars_dir}")
        return []
    
    log_info(f"Found {len(jsons)} merchant files")
    
    if limit is not None:
        # Use random.sample for efficient random selection
        jsons = random.sample(jsons, min(limit, len(jsons)))
    else:
        random.shuffle(jsons)

    merchants: list[Merchant] = []
    for path in jsons:
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            
            # Validate required fields
            if "name" not in data:
                log_warning(f"Merchant file missing 'name' field: {path.name}")
                continue
            
            role = data.get("role")
            cls = Merchant
            if role == "broker":
                cls = InformationBroker
            
            m = cls(
                id=data.get("id", path.stem),
                name=data.get("name", path.stem),
                intro=data.get("intro", ""),
                tells_honest=data.get("tells_honest", []),
                tells_lying=data.get("tells_lying", []),
                bluff_skill=int(data.get("bluff_skill", 5)),
                portrait_file=data.get("portrait_file"),
                appearance=data.get("appearance", ""),
                risk_tolerance=int(data.get("risk_tolerance", 5)),
                greed=int(data.get("greed", 5)),
                honesty_bias=int(data.get("honesty_bias", 5)),
            )
            merchants.append(m)
            log_debug(f"Successfully loaded merchant: {m.name}")
            
        except json.JSONDecodeError as e:
            log_error(f"Invalid JSON in merchant file: {path.name}", e)
            continue
        except (KeyError, ValueError, TypeError) as e:
            log_error(f"Error loading merchant from {path.name}", e)
            continue
        except Exception as e:
            log_error(f"Unexpected error loading merchant from {path.name}", e)
            continue
    
    log_info(f"Successfully loaded {len(merchants)} merchants")
    return merchants
