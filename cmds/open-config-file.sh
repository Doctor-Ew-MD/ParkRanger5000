#!/usr/bin/env bash
# make executable with sudo chmod +x cmds/open-config-file.sh
set -e  # stop immediately if any command fails, rather than continuing past an error

sudo nano /etc/systemd/system/bot.service