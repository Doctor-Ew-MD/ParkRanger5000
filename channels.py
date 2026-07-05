from __future__ import annotations

import datetime

import discord
from discord import utils

import calendar
from collections import OrderedDict


CHANNEL_ERROR_MSG = (
    "Please include a month, day (or range of dates like 23-25), and description, like this:"
    "\n**!create dec 31 nye dance party**"
)
IGNORE_POSITION = ["event-planner"]
MONTHS_ABBR = list(map(lambda x: x.lower(), list(calendar.month_abbr)))


class ChannelError(Exception):
    pass


class BaseChannel:
    def __init__(self, ctx):
        self.ctx = ctx

    async def validate_category(self, category_name: str):
        """
        Verify that the channel's category name is valid.
        """
        category = discord.utils.get(self.ctx.guild.categories, name=category_name)
        if not category:
            raise ChannelError(f"Category '{category_name}' doesn't exist!")

    async def get_category(self, category_name: str) -> discord.CategoryChannel:
        """
        Returns the first category found with the given name.
        """
        category = discord.utils.get(self.ctx.guild.categories, name=category_name)

        if not category:
            raise ChannelError(f"Category '{category_name}' doesn't exist!")

        return category

    @staticmethod
    async def overwrite_channel_positions(category: discord.CategoryChannel) -> bool:
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
        try:
            await category.guild._state.http.bulk_channel_update(category.guild.id, payload)
        except Exception as exc:
            print(f"hit exception in overwrite_channel_positions: {exc}")
            return False
        else:
            return True


class NewChannel(BaseChannel):
    def __init__(self, ctx):
        super().__init__(ctx)

    async def validate_unique(self, channel_name):
        """
        Verify that a channel called <channel_name> doesn't exist.
        """
        if utils.get(self.ctx.guild.channels, name=channel_name):
            raise ChannelError(f"Channel {channel_name} already exists!")

    def create_channel(self):
        pass  # Not implemented


class ExistingChannel(BaseChannel):
    def __init__(self, ctx):
        super().__init__(ctx)

    async def validate_exists(self, channel_name: str):
        """
        Verify a channel called <channel_name> does exist.
        """
        if not utils.get(self.ctx.guild.channels, name=channel_name):
            raise ChannelError(f"Channel {channel_name} doesn't exist.")


class EventChannel(NewChannel):
    """
    Handles the creation and verification of a new event channel.
    Follows a somewhat strict pattern which requires the name to start with
    a month and date(s).
    e.g., jan-31-new-years-party
    """
    def __init__(self, ctx, args):
        super().__init__(ctx)
        self.args = args

    def validate_month(self):
        """
        Approve a full or partial month name.
        """
        month = self.args[0]
        if month[:3].lower() not in MONTHS_ABBR:
            raise ChannelError(f"Sorry, I didn't recognize the month '{month}'.")

    def validate_dates(self):
        """
        This isn't properly checking a date against a month, rather it's looking
        for an integer or "range" (e.g., 10-12).
        """
        dates = self.args[1]
        if "-" in dates:
            split_dates = dates.split("-")
            try:
                int(split_dates[0])
                int(split_dates[1])
            except ValueError:
                raise ChannelError(f"I didn't understand the date range '{dates}'.")
        else:
            try:
                int(dates)
            except ValueError:
                raise ChannelError(f"I didn't understand the date '{dates}'.")

    @staticmethod
    def validate_name(channel_name: str, name_length: int = 40):
        if len(channel_name) > name_length:
            raise ChannelError(f"That channel's name is too long! (The maximum length is {name_length} characters).")

    async def create_channel(self, category_name: str, channel_name: str, sort: bool = False):
        """
        Creates a new channel called <channel_name>.

        The 'sort' param will add some overhead as it reassigns the position
        attribute of all the channels in the given category, but will attempt
        to create the channel in the properly sorted position relative to other channels.
        If you want to speed things up, set sort to False and move channels via the UI.
        """
        category = await self.get_category(category_name)

        if sort and await self.overwrite_channel_positions(category):
            position = self.calculate_channel_position(category, channel_name)
        else:
            position = 50  # represents the bottom of a category

        channel = await self.ctx.guild.create_text_channel(
            channel_name,
            overwrites={},
            category=category,
            reason=f"created by {self.ctx.author.name}/{self.ctx.author.display_name}",
            position=position,
        )
        await self.ctx.send(f"Here ya go! {channel.jump_url}")

    def calculate_channel_position(self, category: discord.CategoryChannel, new_channel_name: str) -> int:
        """
        Determine where to insert the new channel within the existing channels
        to sort the entire category by month and date. When a range is used in
        the channel name, the channel will appear after any matching single dates.

        If the month is earlier than the current month, the event is happening
        during the next year, so it needs to appear after any events happening
        in the current year.
        """
        def month_day_key(name: str):
            if name in IGNORE_POSITION:
                return 0, 0, 0, 0  # Always sort first
            parts = name.split("-")
            month, day = int(parts[0]), int(parts[1])

            current_month = datetime.datetime.now().month
            year_offset = 1 if month < current_month else 0

            try:
                is_range_date = int(parts[2])  # ranges sort after single dates
            except (ValueError, IndexError):
                is_range_date = 0

            return year_offset, month, day, is_range_date

        channels = {}

        for channel in category.channels:
            if channel.name in IGNORE_POSITION:
                continue

            try:
                if alias_name := self.generate_position_name(channel.name):
                    channels[alias_name] = channel.position
            except ChannelError:
                return 100  # Force the new channel to bottom of the category

        if channels:
            ordered_channels = OrderedDict(channels)
            channel_names = list(ordered_channels.keys())

            try:
                new_channel_alias = self.generate_position_name(new_channel_name)
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