#!/bin/bash
echo "Installing latest version of Gooey!"
echo -e "\nStep 1: Fetching the latest Gooey source code..."
git reset --hard
git checkout master
git fetch origin --prune
git pull
echo "Complete!"
echo -e "\nStep 2: Installing dependencies...\n"
echo "(Please note that this step can take several minutes.)"

echo "Complete!"
echo -e "\nStep 3: Configuring Gooey...\n"
echo "Gooey requires an environment configuration file (env.py) in order to run."
echo -e "\nIf this is your first time running Gooey, it's recommended to generate this file now."
echo "Otherwise, you may opt to manually copy the example configuration and edit as needed."
read -p "Would you like to do this now? [Y/n] " answer
if [ "$answer" != "${answer#[Yy]}" ] ;then
    rm gooey/env.py
    cp gooey/env.py.example gooey/env.py
    echo -e "\n\n"
else
    echo -e "\nYou will need to manually copy env.py.example to env.py and edit with your credentials.\n"
fi
echo "Installation complete!"