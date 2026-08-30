#!/usr/bin/env bash
set -e  # stop immediately if any command fails, rather than continuing past an error

echo "Pulling from git..."
sudo git pull

echo "Reloading systemd daemon..."
sudo systemctl daemon-reload

echo "Restarting bot service..."
sudo systemctl restart bot

echo "Done."