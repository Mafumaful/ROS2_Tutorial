#!/bin/bash

echo "======================================================"
echo "    A* Algorithm Interactive Debugger Demo"
echo "======================================================"
echo ""
echo "This script demonstrates different ways to run the"
echo "A* algorithm with step-by-step visualization."
echo ""
echo "======================================================"
echo ""

echo "Choose an option:"
echo ""
echo "1. Run dedicated debug demo (simplified map)"
echo "2. Run main demo with debug mode (full map)"
echo "3. Run main demo normally (no step-by-step)"
echo ""
read -p "Enter your choice (1-3): " choice

case $choice in
    1)
        echo ""
        echo "Starting dedicated debug demo..."
        echo "Use ← → (or A/D) keys to navigate steps"
        echo ""
        python examples/lesson1_debug.py
        ;;
    2)
        echo ""
        echo "Starting main demo in debug mode..."
        echo "Use ← → (or A/D) keys to navigate steps"
        echo ""
        python examples/lesson1_demo.py --debug
        ;;
    3)
        echo ""
        echo "Starting main demo in normal mode..."
        echo ""
        python examples/lesson1_demo.py
        ;;
    *)
        echo ""
        echo "Invalid choice. Please run again and select 1-3."
        exit 1
        ;;
esac

echo ""
echo "======================================================"
echo "Demo completed!"
echo "======================================================"
