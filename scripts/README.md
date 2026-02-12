# Scripts Directory

Utility scripts for Sheriff of Nottingham project maintenance and distribution.

## Directory Structure

```
scripts/
├── shell/              # Shell scripts for maintenance
│   ├── clean.sh        # Clean development artifacts
│   ├── optimize-git.sh # Optimize git repository
│   └── package.sh      # Create distribution package
└── README.md           # This file
```

## Available Scripts

### `shell/clean.sh` - Cleanup Development Artifacts

Removes temporary files, caches, and coverage artifacts to reduce repository size.

**Usage:**
```bash
./scripts/shell/clean.sh
```

**What it removes:**
- Python cache files (`__pycache__/`, `*.pyc`, `*.pyo`)
- Pytest cache (`.pytest_cache/`)
- Coverage reports (`htmlcov/`, `.coverage`)
- Test backup files (`*.backup`)
- Log files (`*.log`)
- macOS system files (`.DS_Store`)
- Virtual environments (if present)

**Size reduction:** ~5MB (from 47MB to 42MB)

### `shell/optimize-git.sh` - Optimize Git Repository

Aggressively optimizes the git repository by removing unreachable objects and repacking.

**Usage:**
```bash
./scripts/shell/optimize-git.sh
```

**What it does:**
- Removes unreachable commits
- Prunes old reflog entries
- Repacks objects efficiently
- Runs aggressive garbage collection

**Size reduction:** ~38MB (from 40MB to 1.6MB - 96% reduction!)

**⚠️ Warning:** This is aggressive and removes old reflog entries. Don't run if you need to recover deleted branches.

### `shell/package.sh` - Create Distribution Package

Creates a clean distribution zip file without development artifacts. **Automatically runs `clean.sh` and `optimize-git.sh` first.**

**Usage:**
```bash
./scripts/shell/package.sh
```

**What's included:**
- ✅ Source code (`core/`, `ui/`, `ai_strategy/`)
- ✅ Game data (`data/`, `characters/`)
- ✅ Configuration files
- ✅ Documentation (`README.md`, `requirements.txt`)

**What's excluded:**
- ❌ Tests (`tests/`)
- ❌ Git history (`.git/`)
- ❌ Development artifacts (coverage, caches)
- ❌ Virtual environments

**Expected package size:** ~1-2MB (vs 47MB full repo)

## Repository Size Breakdown

```
Total: 42MB (after cleanup)
├── .git/         40MB  (Git history - normal)
├── tests/        624KB (Test suite)
├── characters/   768KB (Game assets - portraits)
├── core/         304KB (Core game logic)
├── ui/           76KB  (UI code)
├── ai_strategy/  68KB  (AI strategies)
└── data/         32KB  (Game data - JSON files)
```

## When to Use

**Use `shell/clean.sh` when:**
- Before committing to git
- After running tests with coverage
- Repository size grows unexpectedly
- Regular maintenance

**Use `shell/optimize-git.sh` when:**
- .git directory grows large (>10MB)
- Monthly maintenance
- Before creating releases
- After major refactoring with many commits

**Use `shell/package.sh` when:**
- Creating a release (runs all cleanup automatically)
- Sharing the game with others
- Deploying to a server
- Creating a backup of just the game code

## Notes

- Both scripts are safe to run multiple times
- `clean.sh` is automatically called by `package.sh`
- Virtual environments are excluded from packages
- Git history (`.git/`) is the largest component but necessary for version control
