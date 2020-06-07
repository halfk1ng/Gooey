#!/bin/bash
echo "Installing latest version of Gooey!"
echo "Step 1: Fetching the latest Gooey source code..."
git reset --hard
git checkout master
git fetch origin --prune
git pull
echo "\nComplete!\n"
echo "Step 2: Setting up venv..."
python -m venv venv
source venv/bin/activate
echo "Step 3: Installing dependencies..."
echo "(Please note that this step can take several minutes.)"
pip install -r requirements.txt
echo "\nInstallation complete!"