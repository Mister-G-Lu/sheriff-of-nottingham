# Sharing the Project

## Quick Zip & Share

Use the included shell script to create a clean zip file:

```bash
./zip_project.sh
```

This will:
- Create a timestamped zip file in the parent directory
- Exclude unnecessary files (cache, build artifacts, git files)
- Show the file location and size
- Ready to share!

## What Gets Excluded

The script automatically excludes:
- `__pycache__/` directories
- `.git/` directory
- `.DS_Store` files
- `build/` and `dist/` directories
- `.spec` files
- Virtual environment folders (`venv/`, `.venv/`)
- Compiled Python files (`*.pyc`)

## Output

The zip file will be created in the parent directory with a timestamp:
```
sheriff-of-nottingham_YYYYMMDD_HHMMSS.zip
```

Example:
```
sheriff-of-nottingham_20260210_144417.zip
```

## Manual Zip (Alternative)

If you prefer to create the zip manually:

```bash
# From the parent directory of the project
cd /path/to/parent/directory
zip -r sheriff-of-nottingham.zip sheriff-of-nottingham \
    -x "sheriff-of-nottingham/__pycache__/*" \
    -x "sheriff-of-nottingham/.git/*" \
    -x "sheriff-of-nottingham/build/*" \
    -x "sheriff-of-nottingham/dist/*"
```

## Sharing Options

Once zipped, you can share via:
- Email attachment
- Cloud storage (Google Drive, Dropbox, etc.)
- GitHub release
- File transfer services

Typical file size: ~600KB (compressed)
