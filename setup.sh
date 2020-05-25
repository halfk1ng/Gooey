#!/bin/bash
echo "Installing latest version of Gooey!"
echo "Step 1: Fetching the latest Gooey source code..."
git reset --hard
git checkout master
git fetch origin --prune
git pull
echo "\nComplete!\n"
echo "Step 2: Installing dependencies..."
echo "(Please note that this step can take several minutes.)"
pip install -r requirements.txt
echo "\nComplete!\n"
echo "Step 3: Configuring Gooey...\n"
echo "Gooey requires an environment configuration file (env.py) in order to run."
echo "\nIf this is your first time running Gooey, it's recommended to generate this file now."
echo "Otherwise, you may opt to manually copy the example configuration and edit as needed."
read -p "Would you like to do this now? [Y/n] " answer
if [ "$answer" != "${answer#[Yy]}" ] ;then
    rm gooey/env.py
    cp gooey/env.py.example gooey/env.py
else
    echo "\nYou will need to manually copy env.py.example to env.py and edit with your credentials."
fi
echo "\nInstallation complete!"