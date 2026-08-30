#!/usr/bin/env bash
# make executable with sudo chmod +x cmds/git-pull.sh
set -e  # stop immediately if any command fails, rather than continuing past an error

echo "Pulling from git..."
sudo git pull

echo "Reloading systemd daemon..."
sudo systemctl daemon-reload

echo "Restarting bot service..."
sudo systemctl restart bot

echo "Done."