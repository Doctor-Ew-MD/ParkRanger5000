from __future__ import annotations

import os

from channels import ChannelHandler
from commands import CommandHandler
from intents import IntentsHandler
from messages import MessageHandler
from reactions import ReactionHandler

from discord.ext import commands


# TODO Add better, cleaner logging

TOKEN = os.getenv('DISCORD_TOKEN')

BOT_ROLE_NAMES = {'ParkRanger5000', 'ParkRanger'}
INTRODUCTION_CHANNEL_NAME = "introduction"

intents = IntentsHandler().set()
bot = commands.Bot(command_prefix='!', intents=intents)


@bot.command()
async def hello(ctx, *args):
    """
    Some helpful debug data to check if the bot is working properly.
    """
    await CommandHandler.hello(ctx, bot, args)


@bot.command()
async def create(ctx, *args):
    """
    Allow users to create a new channel, but prevent spamming and report errors.
    Fun fact: it looks like Discord auto-strips prefixed '#' from channel names
    """
    channel = ChannelHandler(ctx, args)
    if await channel.validate():
        await channel.create()


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')


@bot.event
async def on_message(message):
    """
    Handle all message-related actions from/to the bot.
    """
    if message.author.id == bot.user.id:
        return  # Stop the bot from talking to itself

    # Handles @-mentions for the bot and related role(s)
    bot_mentioned = bot.user in message.mentions
    role_mentioned = any(role.name in BOT_ROLE_NAMES for role in message.role_mentions)
    if bot_mentioned or role_mentioned:
        await MessageHandler(bot, message).at_mention()

    await bot.process_commands(message)


@bot.event
async def on_raw_reaction_add(payload):
    """    
    Handles all functionality triggered by reactions.
    """
    channel = bot.get_channel(payload.channel_id)
    if channel.name.lower() == INTRODUCTION_CHANNEL_NAME:
        print("we're in teh right channel")
        await ReactionHandler(bot, channel, payload).verification_check()

bot.run(TOKEN)
