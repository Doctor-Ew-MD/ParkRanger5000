from __future__ import annotations

import os
import traceback

from discord import utils
from discord.ext import commands

from channels import ExistingChannel, NewChannel, EventChannel, ChannelError, CHANNEL_ERROR_MSG
from commands import SimpleCommand, CommandWithArgs
from intents import IntentsHandler
from messages import MessageHandler
from reactions import VerificationReaction

STATIC_TOKEN = os.getenv("STATIC_TOKEN")

BOT_ROLE_NAMES = {"ParkRanger5000",}
INTRODUCTION_CHANNEL_NAME = "introduction"

intents = IntentsHandler().set_intents()
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.command()
async def hello(ctx):
    """
    Some helpful debug data to check if the bot is working properly.
    """
    await SimpleCommand.hello(ctx, bot)


@bot.command()
async def create(ctx, *args):
    """
    Allow members to create a new channel, but prevent spamming and report errors.
    Fun fact: it looks like Discord auto-strips prefixed "#" from channel names.
    Expected syntax: '!create jan 1 new years party' or '!create jan-1-new-years-party'
    """
    cmd = CommandWithArgs(ctx, args)
    cmd.validate_context()

    await cmd.validate_channel(["event-planner"])

    # allow for hyphens; treats any input as though spaces were used
    if len(args) == 1:
        args = tuple(args[0].split("-"))
        cmd.args = args

    cmd.validate_args(3)

    event_channel = EventChannel(ctx, args)
    event_channel.validate_month()
    event_channel.validate_dates()

    channel_name = "-".join(args)
    await event_channel.validate_unique(channel_name)
    event_channel.validate_name(channel_name)

    category_name = "Events"
    await event_channel.validate_category(category_name)
    await event_channel.create_channel(category_name, channel_name, sort=True)


@bot.command()
async def rename(ctx, *args):
    """
    Allows members to rename an existing channel.

    Allows for channel names with spaces or hyphens.
    e.g. "oct-8-party" or "oct 8 party".
    """
    cmd = CommandWithArgs(ctx, args)
    cmd.validate_context()

    await cmd.validate_channel(["event-planner"])

    cmd.validate_syntax("->")

    args_str = " ".join(args)
    args_parts = args_str.split("->")
    cmd.validate_args_len(args_parts, 2)

    existing_channel_name = args_parts[0].strip().replace(" ", "-")
    new_channel_name = args_parts[1].strip().replace(" ", "-")

    existing_channel = ExistingChannel(ctx)
    await existing_channel.validate_exists(existing_channel_name)

    new_channel = NewChannel(ctx)
    await new_channel.validate_unique(new_channel_name)

    # TODO use EventChannel, not NewChannel

    channel_to_update = utils.get(ctx.guild.channels, name=existing_channel_name)
    await channel_to_update.edit(name=new_channel_name)
    await ctx.send(f"I've successfully updated {existing_channel_name} to {new_channel_name}!")


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

    # Handles @-mentions for the bot and related role(s)
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
#         await VerificationReaction(bot, channel, payload).verification_check()


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

        if isinstance(error, ChannelError):
            await ctx.send(f"{error}\n\n{CHANNEL_ERROR_MSG}")
        else:
            await ctx.send(error)
    else:
        traceback.print_exception(type(error), error, error.__traceback__)
        raise error

bot.run(STATIC_TOKEN)
