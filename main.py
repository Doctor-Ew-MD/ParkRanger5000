import discord
from discord.ext import commands

import logging
import os


TOKEN = 'MTUxNDAzMzA4MjI0MjY5OTQwNA.GNzj5A.TxCJaVI1M2O7hlm87qKtJkR5LAQQJ9bY7n9R5c'  # GitHub secret
ERROR_MSG = 'Please include a month, day, and name for your channel, such as **dec-31-nye-dance-party**'
EVENTS_CATEGORY = 'Events'
CHANNEL_NAME = 'event-planner'

# Set required intents for handling messages
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True

bot = commands.Bot(command_prefix='!', intents=intents)

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.command()
async def hello(ctx):
    await ctx.send('Hello!')

@bot.command()
async def create(ctx, *args):
    """
    Allow users to create a new channel, but prevent spamming and report errors.
    """
    if not ctx:  # This will probably never be True
        print('No context provided')
        return
    
    user_name = f'{ctx.author.name}/{ctx.author.display_name}'

    if ctx.message.channel.name.lower() != CHANNEL_NAME:
        await ctx.send(f'That command only works in the **{CHANNEL_NAME}** channel!')
        print(f'Failed event-planner check from {user_name}')
        return

    if not args or len(args) < 3:
        await ctx.send(ERROR_MSG)
        print(f'Failed args or len(args) check from {user_name}')
        return

    try:
        int(args[1])
    except ValueError:
        await ctx.send(ERROR_MSG)
        print(f'Failed int check from {user_name}')
        return

    channel_name = '-'.join(args)

    if existing := discord.utils.get(ctx.guild.channels, name=channel_name):
        await ctx.send(f'A channel named **{channel_name}** already exists!')
        print(f'Failed existing check from {user_name}')
        return

    category = discord.utils.get(ctx.guild.categories, name=EVENTS_CATEGORY)

    print(f'Attempting to create channel **{channel_name}** from {user_name}')
    await ctx.guild.create_text_channel(
        channel_name,
        overwrites={},
        category=category,
        reason=f'created by {user_name}',
    )

    await ctx.send(f'Created channel **{channel_name}**!')
    print(f'New channel **{channel_name}** created by {user_name}')

bot.run(TOKEN, log_handler=handler)