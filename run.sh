#!/bin/bash
# Termivox launcher script
# Activates the virtual environment and starts voice recognition

cd "$(dirname "$0")"

source termivox-env/bin/activate

echo "🎤 Termivox Voice Recognition Bridge"
echo "======================================"
echo ""
echo "Starting voice recognition..."
echo "Speak commands and they will be typed in your active window."
echo ""
echo "Commands:"
echo "  - Say punctuation names: 'comma', 'period', 'question mark', etc."
echo "  - 'new line', 'new paragraph', 'tab'"
echo "  - 'copy', 'paste', 'click', 'scroll up/down'"
echo ""
echo "Press Ctrl+C to stop."
echo ""

python src/main.py --lang en
