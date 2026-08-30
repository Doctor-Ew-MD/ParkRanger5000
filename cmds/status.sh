#!/usr/bin/env bash
# make executable with sudo chmod +x cmds/status.sh
set -e  # stop immediately if any command fails, rather than continuing past an error

sudo systemctl status bot