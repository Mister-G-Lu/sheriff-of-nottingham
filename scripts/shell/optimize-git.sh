#!/bin/bash
# Git repository optimization script
# Reduces .git directory size by cleaning up unnecessary objects

echo "🔧 Optimizing Git repository..."
echo ""
echo "Before optimization:"
du -sh .git
echo ""

# Step 1: Clean up unreachable objects
echo "Step 1: Cleaning up unreachable objects..."
git reflog expire --expire=now --all
git gc --prune=now --aggressive

echo ""
echo "Step 2: Repacking objects..."
git repack -a -d --depth=250 --window=250

echo ""
echo "Step 3: Pruning old reflog entries..."
git reflog expire --expire-unreachable=now --all

echo ""
echo "Step 4: Final garbage collection..."
git gc --aggressive --prune=all

echo ""
echo "✅ Optimization complete!"
echo ""
echo "After optimization:"
du -sh .git
echo ""
echo "Git object statistics:"
git count-objects -vH
echo ""
echo "⚠️  Note: This optimization is aggressive and removes:"
echo "   - Unreachable commits"
echo "   - Old reflog entries"
echo "   - Loose objects"
echo ""
echo "💡 If you need to recover old commits, do NOT run this script!"
