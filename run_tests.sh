#!/bin/bash

# Test Runner Script for Mushanai Platform
# Usage: ./run_tests.sh [option]

set -e

echo "═══════════════════════════════════════════════════════════════"
echo "🧪 MUSHANAI TEST RUNNER"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo "❌ pytest is not installed!"
    echo "   Installing test dependencies..."
    pip install -r requirements.txt
    echo ""
fi

# Parse option
OPTION="${1:-all}"

case $OPTION in
    "all")
        echo "Running all tests with coverage..."
        pytest --cov --cov-report=term-missing --cov-report=html
        ;;
    
    "critical")
        echo "Running critical tests only..."
        pytest -m critical -v
        ;;
    
    "unit")
        echo "Running unit tests only..."
        pytest -m unit -v
        ;;
    
    "integration")
        echo "Running integration tests only..."
        pytest -m integration -v
        ;;
    
    "fast")
        echo "Running tests in parallel (fast mode)..."
        pytest -n auto --maxfail=3
        ;;
    
    "coverage")
        echo "Generating coverage report..."
        pytest --cov --cov-report=html --cov-report=term-missing
        echo ""
        echo "📊 Coverage report generated: htmlcov/index.html"
        echo "   Open with: open htmlcov/index.html"
        ;;
    
    "smoke")
        echo "Running smoke tests (quick sanity check)..."
        pytest -m smoke --maxfail=1 -x
        ;;
    
    "failed")
        echo "Re-running last failed tests..."
        pytest --lf -v
        ;;
    
    "debug")
        echo "Running tests in debug mode..."
        pytest --pdb -s
        ;;
    
    "verbose")
        echo "Running tests with verbose output..."
        pytest -vv
        ;;
    
    "help")
        echo "Usage: ./run_tests.sh [option]"
        echo ""
        echo "Options:"
        echo "  all          - Run all tests with coverage (default)"
        echo "  critical     - Run only critical tests"
        echo "  unit         - Run only unit tests"
        echo "  integration  - Run only integration tests"
        echo "  fast         - Run tests in parallel"
        echo "  coverage     - Generate HTML coverage report"
        echo "  smoke        - Quick sanity check"
        echo "  failed       - Re-run last failed tests"
        echo "  debug        - Run with debugger"
        echo "  verbose      - Run with verbose output"
        echo "  help         - Show this help message"
        echo ""
        exit 0
        ;;
    
    *)
        echo "❌ Unknown option: $OPTION"
        echo "   Run './run_tests.sh help' for usage information"
        exit 1
        ;;
esac

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "✅ Tests completed!"
echo "═══════════════════════════════════════════════════════════════"

