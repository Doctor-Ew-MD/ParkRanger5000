#!/usr/bin/env python3
"""
Send a message to a Discord channel from the terminal.

Usage:
    python3 send_message.py <channel_id> "<message>"

Example:
    export STATIC_TOKEN=<token>
    venv/bin/python3.13 tasks/send_message.py 123456789012345678 "Hello from EC2!"
"""
import os
import sys

import discord

if len(sys.argv) < 3:
    print('Usage: send_message.py <channel_id> "<message>"', file=sys.stderr)
    sys.exit(1)

try:
    CHANNEL_ID = int(sys.argv[1])
except ValueError:
    print("channel_id must be a number", file=sys.stderr)
    sys.exit(1)

MESSAGE = " ".join(sys.argv[2:])

TOKEN = os.environ.get("STATIC_TOKEN")
if not TOKEN:
    print("STATIC_TOKEN environment variable is not set", file=sys.stderr)
    sys.exit(1)

client = discord.Client(intents=discord.Intents.default())
failed = False


@client.event
async def on_ready():
    global failed
    try:
        channel = await client.fetch_channel(CHANNEL_ID)
        await channel.send(MESSAGE)
        print(f"Sent message to #{channel.name} ({CHANNEL_ID})")
    except Exception as e:
        print(f"Failed to send message: {e}", file=sys.stderr)
        failed = True
    finally:
        await client.close()


if __name__ == "__main__":
    client.run(TOKEN)
    if failed:
        sys.exit(1)
