# Sheriff of Nottingham Prototype

## Folder Structure
- `core/` - Main game logic (merchants, sheriff, rounds, goods)
- `ui/` - ASCII/narration helpers
- `characters/` - ASCII portraits and JSON character data
- `data/` - Reserved for saves or future configs
- `main.py` - Entry point (run from root folder)

## How it works
- Merchants are loaded randomly from `characters/`
- Each merchant has a personality, lore, and tells (honest or lying cues)
- Sheriff has stats: Perception, Authority, Reputation, and can level up experience
- ASCII art is loaded from files in `characters/` folder
- Gameplay currently supports:
  - Merchant arrival narration
  - Displaying declaration and bribe
  - Lie detection based on Perception vs Merchant bluff skill
- Add your own ASCII art for merchants in their `.txt` files

## Run
```bash
cd sheriff_game_final
python main.py
