# Code Quality Tools

This directory contains tools for maintaining code quality and detecting potential issues.

## Available Tools

### 1. `simple_sanity_check.py` (No Dependencies)

A basic code analyzer using Python's built-in `ast` module.

**What it detects:**
- ✅ Unused imports
- ✅ Unused functions
- ✅ Unused classes  
- ✅ Unused module-level variables

**Usage:**
```bash
python3 tools/simple_sanity_check.py
```

**Limitations:**
- May have false positives (e.g., `__init__.py` exports, constants files)
- Cannot detect unused local variables within functions
- Cannot detect truly dead code paths

### 2. `sanity_check.py` (Requires External Tools)

A more comprehensive checker using professional tools.

**What it detects:**
- ✅ All of the above, plus:
- ✅ Unused local variables
- ✅ Dead code paths
- ✅ Unreachable code
- ✅ More accurate detection

**Installation:**
```bash
pip install vulture flake8 pylint
```

**Usage:**
```bash
python3 tools/sanity_check.py
```

## Current Findings

### Constants File (`core/constants.py`)

The sanity checker reports many "unused" constants. This is **expected and OK** because:
- Constants are meant to be imported and used elsewhere
- They're defined in a central location for maintainability
- The checker can't see cross-file usage easily

**Action:** No action needed - these are intentional exports.

### Init File (`core/__init__.py`)

Many "unused" imports reported. This is **expected and OK** because:
- `__init__.py` re-exports items for convenience
- Allows `from core import Merchant` instead of `from core.players.merchants import Merchant`
- The checker can't detect these re-exports

**Action:** No action needed - these are intentional re-exports.

### True Issues to Investigate

If the checker finds:
- **Unused functions in regular modules** → May be dead code
- **Unused imports in regular files** → Can be safely removed
- **Unused variables in functions** → Can be removed or prefixed with `_`

## Tips for Clean Code

1. **Remove truly unused code** - Don't keep "just in case" code
2. **Prefix intentionally unused items with `_`** - Tells tools to ignore them
3. **Use `# noqa` comments** - For false positives in specific lines
4. **Run checks regularly** - Catch issues early

## False Positives

Common false positives to ignore:
- Constants in `constants.py`
- Re-exports in `__init__.py`
- Test fixtures (pytest automatically uses them)
- Dynamic imports (`importlib`, `__import__`)
- Metaclass magic methods
- Protocol/Interface methods

## Integration with CI/CD

To run automatically in CI:
```yaml
# .github/workflows/code-quality.yml
- name: Check for unused code
  run: python3 tools/simple_sanity_check.py
```

## Recommended Workflow

1. Run `simple_sanity_check.py` regularly during development
2. Review findings and remove truly unused code
3. For deeper analysis, install and run `sanity_check.py`
4. Focus on non-constants, non-init files for real issues
