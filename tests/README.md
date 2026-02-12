# Sheriff of Nottingham - Test Suite

```
tests/
├── unit/
│   ├── core/              # Core game logic tests
│   │   ├── test_game_manager*.py
│   │   └── ...
│   ├── ui/                # UI component tests
│   │   ├── test_menu.py
│   │   ├── ...
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

### ⚠️ Testing Silas Voss (Information Broker)
**CRITICAL:** Silas's sheriff detection requires game state history. Always record events:

```python
from tests.simulations.simulation_helpers import record_round_to_game_state

# After each round:
record_round_to_game_state(
    merchant_name=merchant.name,
    declaration=declaration,
    actual_goods=actual_goods,
    should_inspect=should_inspect,
    caught=caught,
    bribe_offered=bribe_offered,
    accept_bribe=accept_bribe
)
```

Without this, Silas will always detect sheriffs as "unknown" and perform significantly worse.

### Headless Mode for Pygame Tests
All tests that use pygame should run in headless mode.
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

**Note:** Coverage reports are generated in `htmlcov/` directory and `coverage.json` file.
Run `pytest --cov=.` to update coverage data.
