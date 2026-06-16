import discord
from discord.ext import commands

import os

# TODO Add better, cleaner logging. Currently the print statements end up in the Railway logs.

TOKEN = os.getenv('PARKRANGER5000_TOKEN')  # Stored in Railway's env secrets
ERROR_MSG = 'Please include a month, day, and description when you create your channel, like this: **!create dec 31 nye dance party**'
EVENTS_CATEGORY_NAME = 'Events'
EVENTS_CHANNEL_NAME = 'event-planner'
BOT_ROLE_NAMES = {'ParkRanger5000', 'ParkRanger'}

intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')


@bot.command()
async def hello(ctx, *args):
    """
    Some helpful data to check if the bot is working properly and debug messages.
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
    """

    if not ctx:  # This will probably never be True
        print('No context provided')
        return

    if bot.user.name in args:
        print('bot mentioned')
        return
    
    user_name = f'{ctx.author.name}/{ctx.author.display_name}'

    if ctx.message.channel.name.lower() != EVENTS_CHANNEL_NAME:
        print(f'Failed event-planner check from {user_name}')
        await ctx.send(f'That command only works in the **{EVENTS_CHANNEL_NAME}** channel!')
        return

    if not args or len(args) < 3:
        print(f'Failed args or len(args) check from {user_name}')
        await ctx.send(f'That channel name isn\'t quite detailed enough!')
        await ctx.send(ERROR_MSG)
        return

    try:
        int(args[1])
    except ValueError:
        print(f'Failed int check from {user_name}')
        await ctx.send('That channel name didn\'t meet the format requirements of month-day-title.')
        await ctx.send(ERROR_MSG)
        return

    channel_name = '-'.join(args)

    if existing := discord.utils.get(ctx.guild.channels, name=channel_name):        
        print(f'Failed existing check from {user_name}')
        await ctx.send(f'A channel named **{channel_name}** already exists!')
        return

    if len(channel_name) > 40:
        print(f'Channel\'s name exceeded the maximum length from {user_name}')
        await ctx.send(f'That channel name is a little too long, could you please shorten it and try again?')
        await ctx.send(ERROR_MSG)
        return

    category = discord.utils.get(ctx.guild.categories, name=EVENTS_CATEGORY_NAME)

    print(f'Attempting to create channel **{channel_name}** from {user_name}')
    channel = await ctx.guild.create_text_channel(
        channel_name,
        overwrites={},
        category=category,
        reason=f'created by {user_name}',
    )
    print(f'New channel **{channel_name}** created by {user_name}')
    await ctx.send(f'Here ya go! {channel.jump_url}')


@bot.event
async def on_message(message):
    """
    Reads all messages to check whether the ParkRanger role has been mentioned,
    or the ParkRanger5000 name. Not sure why anyone would do this, but it should
    help prevent DMs and assist anyone who is not familiar with the bot.
    """
    if message.author.id == bot.user.id:
        return

    bot_mentioned = bot.user in message.mentions
    role_mentioned = any(role.name in BOT_ROLE_NAMES for role in message.role_mentions)

    if bot_mentioned or role_mentioned:
        print('Bot was mentioned!')
        ctx = await bot.get_context(message)
        events_channel = discord.utils.get(ctx.guild.channels, name=EVENTS_CHANNEL_NAME)
        await message.channel.send(f'Hi, I\'m a bot made to help you create channels in {events_channel.jump_url}.')
        await message.channel.send(f'Head over there to create a channel, or DM an admin if you need help.')
        await message.channel.send(ERROR_MSG)

    await bot.process_commands(message)


bot.run(TOKEN)