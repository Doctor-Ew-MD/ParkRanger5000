from __future__ import annotations

import discord

import calendar
from collections import OrderedDict


ERROR_MSG = ("Please include a month, day (or range of dates like 23-25), and description, like this:"
             "\n**!create dec 31 nye dance party**")
EVENTS_CATEGORY_NAME = "Events"
ALLOWED_CHANNELS = ["event-planner"]  # Channels where users can use the !create command
IGNORE_POSITION = ["event-planner"]
MONTHS_ABBR = list(map(lambda x: x.lower(), list(calendar.month_abbr)))


class ChannelError(Exception):
    pass


class ChannelHandler:
    """
    Controls channel creation and data validation.
    """
    def __init__(self, ctx, args):
        self.ctx = ctx
        self.args = args
        self.channel_name = "-".join(self.args)
        self.user_name = f"{self.ctx.author.name}/{self.ctx.author.display_name}"

    async def create(self):
        """
        Create a new channel.
        """
        category = discord.utils.get(self.ctx.guild.categories, name=EVENTS_CATEGORY_NAME)
        await self.overwrite_channel_positions(category)
        position = self.calculate_channel_position(category)

        print(f"Attempting to create channel **{self.channel_name}** from {self.user_name}")
        channel = await self.ctx.guild.create_text_channel(
            self.channel_name,
            overwrites={},
            category=category,
            reason=f"created by {self.user_name}",
            position=position,
        )
        print(f"New channel **{self.channel_name}** created by {self.user_name}")
        await self.ctx.send(f"Here ya go! {channel.jump_url}")

    async def validate(self) -> bool:
        """
        Run through validation for channel creation and attempt to create a new channel.
        """
        if not self.ctx:  # This will probably never be True
            print("No context provided")
            return False

        if not self.args:
            print(f"Failed args test-- no args found-- from {self.user_name}")
            await self.ctx.send(f"It looks like you forgot to submit a channel name.")
            await self.ctx.send(ERROR_MSG)
            return False

        if self.ctx.message.channel.name.lower() in ALLOWED_CHANNELS:
            try:
                await self.validate_args()
                await self.validate_dates()
                await self.validate_unique()
                await self.validate_name()
            except ChannelError:
                return False
            else:
                return True
        else:
            print(f"Failed event-planner check from {self.user_name}")
            await self.ctx.send(f"That command only works in the following channel(s):")
            await self.ctx.send(f"{','.join(ALLOWED_CHANNELS)}")
            return False

    async def validate_args(self):
        """
        Verify that the minimum number of args has been found.
        """
        if len(self.args) < 3:
            print(f"Failed args or len(args) check from {self.user_name}")
            print(f"args: {self.args}")
            await self.ctx.send(f"I think that channel name is missing some info or some spaces!")
            await self.ctx.send(ERROR_MSG)
            raise ChannelError()

    async def validate_dates(self):
        """
        Handle all date-related verification for the proposed channel name.
        """
        dates = self.args[1].split("-")

        if len(dates) == 1:
            try:
                int(self.args[1])
            except ValueError:
                print(f"Failed single date int check from {self.user_name}")
                await self.ctx.send("That channel name didn't quite meet the format requirements of month-day-title.")
                await self.ctx.send(ERROR_MSG)
                return

        # Handle a range of dates in the channel name
        elif len(dates) == 2:
            try:
                int(dates[0])
                int(dates[1])
            except Exception:
                print(f"Failed date range int check from {self.user_name}")
                await self.ctx.send(
                    "It looks like you tried to use a range of dates, but your message might be malformed.")
                await self.ctx.send("Try something like this: **!create may 23-25 memorial day long weekend**")
                return

        # Send useful error for too many date ranges (not sure when this would happen)
        elif len(dates) > 2:
            print(f"Too many hyphens used for the date range from {self.user_name}")
            await self.ctx.send("That's too many hyphens!")
            await self.ctx.send(ERROR_MSG)
            return

    async def validate_unique(self):
        if existing := discord.utils.get(self.ctx.guild.channels, name=self.channel_name):
            print(f"Failed existing check from {self.user_name}")
            await self.ctx.send(f"A channel named **{self.channel_name}** already exists!")
            raise ChannelError()

    async def validate_name(self):
        if len(self.channel_name) > 40:
            print(f"Channel\"s name exceeded the maximum length from {self.user_name}")
            await self.ctx.send(f"That channel name is a little too long, could you please shorten it and try again?")
            await self.ctx.send(ERROR_MSG)
            raise ChannelError()

    def calculate_channel_position(self, category: discord.CategoryChannel) -> int:
        """
        Determine where to insert the new channel within the existing channels so
        that the entire category is sorted.
        """
        def month_day_key(name: str):
            if name in IGNORE_POSITION:
                return 0, 0  # Always sort first
            parts = name.split("-")
            month, day = int(parts[0]), int(parts[1])
            return month, day

        channels = {}

        for channel in category.channels:
            if channel.name in IGNORE_POSITION:
                channels[channel.name] = channel.position
                continue  # Don't attempt to convert this channel's name to a month-alias, there is no month!

            try:
                if alias_name := self.generate_position_name(channel.name):
                    channels[alias_name] = channel.position
            except ChannelError:
                return 100  # Force the new channel to bottom of the category

        if channels:
            ordered_channels = OrderedDict(channels)
            channel_names = list(ordered_channels.keys())

            try:
                new_channel_alias = self.generate_position_name(self.channel_name)
            except ChannelError:
                return 100

            channel_names.append(new_channel_alias)
            sorted_channels = sorted(channel_names, key=month_day_key)
            insert_index = sorted_channels.index(new_channel_alias) - 1
            if insert_index == -1:
                return 0  # Force the new channel directly below the "event-planner" channel
            return insert_index
        return 100

    @staticmethod
    async def overwrite_channel_positions(category: discord.CategoryChannel):
        """
        Reset the channel positions in a category so that they increment by their
        order as they appear. Discord does not update a channel's position when
        that channel is moved via the UI. The position values of a group of
        channels is not reflective of their order in the UI.
        """
        payload = [
            {"id": channel.id, "position": i}
            for i, channel in enumerate(category.channels)
        ]
        await category.guild._state.http.bulk_channel_update(category.guild.id, payload)

    @staticmethod
    def generate_position_name(channel_name: str) -> str:
        """
        Transcribe a channel name by replacing the month alias with its integer.
        Should handle cases where a full month name is used or an abbreviation.
        """
        name_split = channel_name.split("-")

        try:
            month_abbr = name_split[0][:3]
            month_int = MONTHS_ABBR.index(month_abbr)
        except Exception as exc:
            print(exc)
            raise ChannelError
        else:
            joined_name = "-".join(name_split[1:])
            return f"{month_int}-{joined_name}"
