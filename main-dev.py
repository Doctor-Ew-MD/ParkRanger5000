from __future__ import annotations

import traceback

from discord.ext import commands

from categories import EventCategory, CategoryError
from utils import CHANNEL_ERROR_MSG, STATIC_TOKEN, BOT_ROLE_NAMES
from channels import ExistingChannel, EventChannel, ChannelFormatError
from commands import SimpleCommand, CommandWithArgs
from intents import IntentsHandler
from messages import MessageHandler

if STATIC_TOKEN:
    intents = IntentsHandler().set_intents()
    bot = commands.Bot(command_prefix="!", intents=intents)
else:
    raise Exception("You must set the STATIC_TOKEN environment variable to run the bot.")


@bot.command()
async def hello(ctx):
    """
    Some helpful debug data to check if the bot is working properly.
    """
    await SimpleCommand.hello(ctx, bot)


@bot.command()
async def create(ctx, *args):
    """
    Allow members to create a new channel and receive useful errors.
    Expected syntax: '!create dec 31 nye party' or '!create dec-31-nye-party'
    """
    allowed_roles = ["Verified"]
    allowed_channels = ["event-planner"]
    category_name = "Events"

    cmd = CommandWithArgs(ctx, allowed_roles, allowed_channels)
    await cmd.validate_permissions()

    if len(ctx.args) > 2:  # input uses spaces, sanitize to use hyphens
        ctx.args = [ctx.args[0], ("-".join(ctx.args[1:]))]
    cmd.validate_args_len(1)

    channel_name = ctx.args[1].lower()
    event_channel = EventChannel(ctx, name=channel_name)
    await event_channel.validate_name()

    event_category = EventCategory(ctx, category_name)
    category_obj = await event_category.get_category()

    await event_channel.create_channel(category_obj)
    channel_obj = await event_channel.get_channel()

    await ctx.send(f"Your channel awaits, have fun! {channel_obj.jump_url}")
    await event_category.sort()


@bot.command()
async def rename(ctx, *args):
    """
    Allows members to rename an existing channel.
    """
    allowed_roles = ["Verified"]
    allowed_channels = ["event-planner"]
    category_name = "Events"
    arrow = "->"

    cmd = CommandWithArgs(ctx, allowed_roles, allowed_channels)
    await cmd.validate_permissions()
    cmd.validate_syntax(arrow)

    arrow_index = ctx.args.index(arrow)
    if len(ctx.args) > 4 and arrow_index != 2:  # input uses spaces, sanitize to use hyphens
        arg_one = "-".join(ctx.args[1:arrow_index])
        arg_two = "-".join(ctx.args[arrow_index + 1:])
        ctx.args = [ctx.args[0], arg_one, arrow, arg_two]
    cmd.validate_args_len(3)

    existing_channel_name = ctx.args[1]
    existing_channel = ExistingChannel(ctx, existing_channel_name.lower())
    await existing_channel.validate_exists(category_name)

    updated_channel_name = ctx.args[3]
    updated_channel = EventChannel(ctx, updated_channel_name.lower())
    await updated_channel.validate_name()

    channel_obj = await existing_channel.get_channel()
    await channel_obj.edit(name=updated_channel.name)
    await ctx.send(f"As you wish! **{existing_channel_name}** has been renamed to **{channel_obj.jump_url}**!")

    event_category = EventCategory(ctx, category_name)  # Safe to assume Events exists since channel validation passed
    await event_category.sort()


@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")


@bot.event
async def on_message(message):
    """
    Handle all message-related actions from/to the bot.
    """
    if message.author.id == bot.user.id:
        return  # Stop the bot from talking to itself

    bot_mentioned = bot.user in message.mentions
    role_mentioned = any(role.name in BOT_ROLE_NAMES for role in message.role_mentions)

    if bot_mentioned or role_mentioned:
        await MessageHandler(bot, message).at_mention()

    await bot.process_commands(message)


# @bot.event
# async def on_raw_reaction_add(payload):
#     """
#     Handles all functionality triggered by reactions.
#     """
#     channel = bot.get_channel(payload.channel_id)
#     if channel.name.lower() == INTRODUCTION_CHANNEL_NAME:
#         reaction = VerificationReaction(bot, payload, channel)
#         await reaction.verification_check()


@bot.event
async def on_command_error(ctx, error):
    """
    Unhandled exceptions in discord.py are caught internally by the library
    and may not always produce a traceback in the logs. This error handler
    explicitly prints them.

    discord.py wraps errors in a CommandInvokeError before passing them to
    on_command_error, so we need to unwrap it.
    """
    if isinstance(error, commands.CommandInvokeError):
        error = error.original
        traceback.print_exception(type(error), error, error.__traceback__)

        if isinstance(error, ChannelFormatError):
            await ctx.send(f"{error}\n\n{CHANNEL_ERROR_MSG}")
        elif not isinstance(error, CategoryError):
            await ctx.send(error)
    else:
        traceback.print_exception(type(error), error, error.__traceback__)
        raise error


bot.run(STATIC_TOKEN)
