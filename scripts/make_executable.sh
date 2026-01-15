#!/bin/bash
# Make Python scripts executable

echo "Making scripts executable..."

chmod +x scripts/setup.sh
chmod +x scripts/run_tests.sh
chmod +x scripts/download_models.py
chmod +x scripts/check_setup.py
chmod +x scripts/cleanup.py

echo "✅ All scripts are now executable"
echo ""
echo "You can now run:"
echo "  ./scripts/setup.sh"
echo "  ./scripts/download_models.py"
echo "  ./scripts/check_setup.py"
echo "  ./scripts/cleanup.py"
echo "  ./scripts/run_tests.sh"