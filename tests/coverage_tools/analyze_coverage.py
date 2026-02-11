#!/usr/bin/env python3
"""
Coverage Analysis Tool

Analyzes test coverage and identifies areas needing more tests.
"""

import sys
import subprocess
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def run_coverage():
    """Run tests with coverage and generate report."""
    print("=" * 70)
    print("RUNNING TESTS WITH COVERAGE")
    print("=" * 70)
    print()
    
    # Run tests with coverage
    result = subprocess.run(
        [sys.executable, '-m', 'coverage', 'run', '--source=core,ui', 
         'run_tests_with_coverage.py'],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print("⚠️  Some tests failed, but continuing with coverage analysis...")
    
    print()
    print("=" * 70)
    print("COVERAGE REPORT")
    print("=" * 70)
    print()
    
    # Generate coverage report
    result = subprocess.run(
        [sys.executable, '-m', 'coverage', 'report', '--skip-empty'],
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    
    # Parse coverage data
    lines = result.stdout.strip().split('\n')
    coverage_data = []
    
    for line in lines[2:-2]:  # Skip header and footer
        if line.strip():
            parts = line.split()
            if len(parts) >= 4:
                name = parts[0]
                stmts = parts[1]
                miss = parts[2]
                cover = parts[3].rstrip('%')
                try:
                    coverage_data.append((name, int(stmts), int(miss), int(cover)))
                except ValueError:
                    pass
    
    # Analyze coverage
    print()
    print("=" * 70)
    print("COVERAGE ANALYSIS")
    print("=" * 70)
    print()
    
    # Files with low coverage (< 80%)
    low_coverage = [item for item in coverage_data if item[3] < 80]
    
    if low_coverage:
        print("📊 Files with < 80% coverage:")
        print()
        for name, stmts, miss, cover in sorted(low_coverage, key=lambda x: x[3]):
            print(f"  {cover:3d}% - {name} ({miss} of {stmts} lines not covered)")
        print()
    
    # Files with good coverage (>= 80%)
    good_coverage = [item for item in coverage_data if item[3] >= 80]
    
    if good_coverage:
        print("✅ Files with >= 80% coverage:")
        print()
        for name, stmts, miss, cover in sorted(good_coverage, key=lambda x: x[3], reverse=True):
            print(f"  {cover:3d}% - {name}")
        print()
    
    # Overall stats
    total_stmts = sum(item[1] for item in coverage_data)
    total_miss = sum(item[2] for item in coverage_data)
    overall_coverage = int((total_stmts - total_miss) / total_stmts * 100) if total_stmts > 0 else 0
    
    print("=" * 70)
    print("OVERALL STATISTICS")
    print("=" * 70)
    print()
    print(f"Total statements: {total_stmts}")
    print(f"Covered: {total_stmts - total_miss}")
    print(f"Missing: {total_miss}")
    print(f"Overall coverage: {overall_coverage}%")
    print()
    
    if overall_coverage >= 80:
        print("🎉 TARGET ACHIEVED: >= 80% coverage!")
    else:
        print(f"📈 PROGRESS: {overall_coverage}% / 80% target")
        print(f"   Need to cover {int((80 - overall_coverage) * total_stmts / 100)} more statements")
    
    print()
    
    # Generate HTML report
    print("=" * 70)
    print("GENERATING HTML REPORT")
    print("=" * 70)
    print()
    
    subprocess.run(
        [sys.executable, '-m', 'coverage', 'html'],
        capture_output=True
    )
    
    html_report = project_root / 'coverage_html_report' / 'index.html'
    if html_report.exists():
        print(f"✅ HTML report generated: {html_report}")
        print(f"   Open in browser: file://{html_report}")
    else:
        print("⚠️  HTML report generation failed")
    
    print()
    
    return overall_coverage >= 80


def main():
    """Run coverage analysis."""
    success = run_coverage()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
