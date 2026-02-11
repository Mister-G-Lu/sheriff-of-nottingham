# Sheriff of Nottingham - Test Suite

## 📊 Test Coverage Status

Current test coverage: **~19%** (Target: 40%+)

### Coverage by Module

| Module | Coverage | Status |
|--------|----------|--------|
| `ui/` | 0-28% | 🔴 Needs Improvement |
| `core/game/` | 9-55% | 🟡 In Progress |
| `core/mechanics/` | 14-90% | 🟡 Mixed |
| `core/players/` | 5-73% | 🔴 Needs Improvement |
| `ai_strategy/` | 19% | 🔴 Needs Improvement |

## 🗂️ Test Organization

Tests are organized by module to match the project structure:

```
tests/
├── unit/
│   ├── core/              # Core game logic tests
│   │   ├── test_game_manager*.py
│   │   ├── test_black_market.py
│   │   ├── test_end_game.py
│   │   ├── test_goods.py
│   │   ├── test_merchants.py
│   │   ├── test_negotiation.py
│   │   ├── test_rounds.py
│   │   ├── test_sheriff*.py
│   │   └── ...
│   ├── ui/                # UI component tests
│   │   ├── test_menu.py
│   │   ├── test_price_menu.py
│   │   ├── test_pygame_input.py
│   │   ├── test_pygame_text.py
│   │   ├── test_stats_bar.py
│   │   └── test_narration.py
│   ├── ai_strategy/       # AI strategy tests
│   │   └── test_ai_strategy.py
│   └── characters/        # Character-specific tests
├── demos/                 # Demo/visual tests
├── test_config.py         # Test configuration utilities
└── README.md             # This file
```

## 🚀 Running Tests

### Run All Tests
```bash
pytest
```

### Run Tests with Coverage Report
```bash
pytest --cov=. --cov-report=term-missing
```

### Run Tests for Specific Module
```bash
# Core tests
pytest tests/unit/core/

# UI tests
pytest tests/unit/ui/

# AI strategy tests
pytest tests/unit/ai_strategy/
```

### Run Tests with HTML Coverage Report
```bash
pytest --cov=. --cov-report=html
# Open htmlcov/index.html in browser
```

### Run Tests in Headless Mode (for CI/CD)
Tests automatically run in headless mode to prevent pygame windows from appearing.
This is configured via `SDL_VIDEODRIVER=dummy` environment variable.

## 📝 Writing Tests

### Test File Naming Convention
- Test files should be named `test_<module_name>.py`
- Place tests in the appropriate subdirectory matching the source code structure

### Headless Mode for Pygame Tests
All tests that use pygame should run in headless mode:

```python
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Setup headless mode before importing pygame modules
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

import pygame
# ... rest of imports
```

### Test Structure
```python
class TestFeatureName:
    """Tests for specific feature"""
    
    def test_basic_functionality(self):
        """Test basic functionality"""
        # Arrange
        # Act
        # Assert
        pass
    
    def test_edge_case(self):
        """Test edge case"""
        pass
```

## 🎯 Coverage Goals

### Priority Areas for Improvement

1. **UI Module** (0-28% coverage)
   - `ui/menu.py` - 0%
   - `ui/price_menu.py` - 0%
   - `ui/pygame_input.py` - 0%
   - `ui/pygame_text.py` - 0%
   - `ui/stats_bar.py` - 0%
   - `ui/pygame_ui.py` - 0%

2. **Core Players** (5-73% coverage)
   - `core/players/sheriff_analysis.py` - 5%
   - `core/players/merchant_loader.py` - 15%
   - `core/players/merchants.py` - 29%

3. **Game Manager** (9% coverage)
   - `core/game/game_manager.py` - 9%
   - Multiple test files exist but need consolidation

## 🔧 Test Utilities

### `test_config.py`
Provides utility functions for test setup:
- `setup_headless_mode()` - Configure pygame for headless testing
- `teardown_headless_mode()` - Clean up headless mode
- `create_headless_window()` - Create a headless pygame window

## 📈 Tracking Progress

### Check Current Coverage
```bash
pytest --cov=. --cov-report=term-missing --cov-report=json
```

### Generate Coverage Badge
```bash
coverage-badge -o coverage.svg -f
```

### View Detailed Coverage Report
```bash
pytest --cov=. --cov-report=html
open htmlcov/index.html  # macOS
# or
xdg-open htmlcov/index.html  # Linux
```

## 🐛 Debugging Tests

### Run Tests with Verbose Output
```bash
pytest -v
```

### Run Specific Test
```bash
pytest tests/unit/core/test_game_manager.py::TestGameManagerImports::test_import_game_manager
```

### Run Tests with Print Statements
```bash
pytest -s
```

### Run Tests with Debugger
```bash
pytest --pdb
```

## 📚 Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [Python unittest Documentation](https://docs.python.org/3/library/unittest.html)

## 🤝 Contributing

When adding new features:
1. Write tests first (TDD approach recommended)
2. Ensure tests pass: `pytest`
3. Check coverage: `pytest --cov=.`
4. Aim for >80% coverage on new code
5. Place tests in appropriate subdirectory

## 📊 Coverage History

| Date | Coverage | Notes |
|------|----------|-------|
| 2026-02-11 | 19% | Initial organization, UI tests added |

---

**Note:** Coverage reports are generated in `htmlcov/` directory and `coverage.json` file.
Run `pytest --cov=.` to update coverage data.
