from __future__ import annotations

from channels import ChannelHandler
from messages import MessageHandler
from reactions import ReactionHandler

import discord
from discord.ext import commands


# TODO Add better, cleaner logging. Currently the print statements end up in the Railway logs.

TOKEN = 'MTUxODczNjgwOTMzOTY1NDE1NA.Gze9Xg.6g6O1S578ap94MYYy9bI-E1Jih23DYUpgKtbos'

BOT_ROLE_NAMES = {'ParkRanger5000', 'ParkRanger'}
INTRODUCTION_CHANNEL_NAME = "introduction"

intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.message_content = True
intents.reactions = True

bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')


@bot.command()
async def hello(ctx, *args):
    """
    Some helpful debug data to check if the bot is working properly.
    """
    await ctx.send('Hello!')

    user_name = f'{ctx.author.name}/{ctx.author.display_name}'
    print(f'"hello" command executed by {user_name}')
    print(f'bot.user.id: {bot.user.id}')
    print(f'bot.user.display_name: {bot.user.display_name}')
    print(f'bot.user.name: {bot.user.name}')
    print(f'bot.user.global_name: {bot.user.global_name}')
    print(f'user mentions: {ctx.message.mentions}')
    print(f'role mentions: {ctx.message.role_mentions}')
    print(f'channel mentions: {ctx.message.channel_mentions}')


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
        await ReactionHandler(bot, channel, payload).verification_check()


bot.run(TOKEN)
