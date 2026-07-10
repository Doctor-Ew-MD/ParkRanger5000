from __future__ import annotations

import re

import discord
from discord import utils

from utils import CHANNEL_NAME_CHARS, MONTHS_ABBR, VALID_MONTHS


class ChannelError(Exception):
    pass


class ChannelFormatError(Exception):
    pass


BANNED_CHANNELS = ["event-planner"]


class BaseChannel:
    def __init__(self, ctx, name):
        self.ctx = ctx
        self.name = name

    async def get_channel(self) -> discord.TextChannel:
        if channel := discord.utils.get(self.ctx.guild.channels, name=self.name):
             return channel
        else:
            raise ChannelError(f"Channel '{self.name}' doesn't exist!")

    def sanitize_channel_name(self):
        """
        Remove any characters which are not allowed in a channel name, and update self.name.
        """
        self.name = "".join(c for c in self.name if c in CHANNEL_NAME_CHARS)

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
    def __init__(self, ctx, name):
        super().__init__(ctx, name)

    async def validate_unique(self, channel_name):
        """
        Verify that a channel called <channel_name> doesn't exist.
        """
        if utils.get(self.ctx.guild.channels, name=self.name):
            raise ChannelError(f"Channel {self.name} already exists!")


class ExistingChannel(BaseChannel):
    def __init__(self, ctx, name):
        super().__init__(ctx, name)

    async def validate_exists(self, category_name: str = ""):
        """
        Verify a channel called <channel_name> exists.
        """
        if channel := await self.get_channel():
            if channel.name in BANNED_CHANNELS:
                raise ChannelError(f"Hey! Leave **{channel.name}** alone!")
            if channel.category.name != category_name:
                raise ChannelError(f"Channel **{self.name}** doesn't exist in the **{category_name}** category.")
        else:
            raise ChannelError(f"Channel **{self.name}** doesn't exist in any category.")


class EventChannel(NewChannel):
    """
    Handles the creation and verification of a new event channel.
    Follows a strict pattern which requires the name to start with
    a month and date(s). (e.g., jan-31-new-years-party)

    Transcribes full or partial months to 3 or 4 character abbreviations.

    Doesn't allow any characters which don't appear in utils.CHANNEL_NAME_CHARS.
    """
    def __init__(self, ctx, name):
        super().__init__(ctx, name)

    async def validate_name(self):
        """
        A collection of methods for validating an Event channel's name prior to creating it.
        Each validation method should raise an error if something unexpected happens.
        """
        self.validate_month()
        self.validate_dates()
        self.validate_description()

        # Kinda awkward to do these post-validation, but previous errors are more helpful to the user this way
        self.update_month()
        # self.sanitize_channel_name()

        await self.validate_unique(self.name)

    def validate_month(self):
        """
        Approve a full or partial month name.
        """
        month = self.name.split("-")[0]
        if month not in VALID_MONTHS:
            raise ChannelError(f"Sorry, I didn't recognize the month **{month}**.")

        for month_abbr in MONTHS_ABBR:
            if month[:3].lower() in month_abbr:
                return
        else:
            raise ChannelFormatError(f"Sorry, I didn't recognize the month **{month}**.")

    def validate_dates(self):
        """
        This isn't properly checking a date against a month, rather it's looking
        for a single date or range (e.g., 10 or 10-12).
        """
        pattern = r"-(\d+)-(\d+)-"  # pattern for a date range
        if match := re.search(pattern, self.name):
            try:
                date_one = int(match.group(1))
                date_two = int(match.group(2))
                if date_one > date_two or date_one not in range(1,32) or date_two not in range(1,32):
                    raise ChannelFormatError("There's something up with those dates, are you sure they're correct?")
            except ValueError:
                raise ChannelFormatError(f"I didn't understand the date range **{match.group(0)[1:-1]}**.")
        else:
            try:
                date = int(self.name.split("-")[1])
                if date not in range(1,32):
                    raise ChannelFormatError(f"That doesn't look like a valid date.")
            except ValueError:
                raise ChannelFormatError(f"I didn't understand the date in that command.")

    def validate_description(self, name_length: int = 40):
        if len(self.name) > name_length:
            raise ChannelError(f"That channel's name is too long! (The maximum length is {name_length} characters).")

        if self.name.split("-")[2] in ("", " ", None):
            raise ChannelFormatError(f"Something's up with the description in that command.")

    def update_month(self):
        """
        Transcribe the member's input-month to the correct abbreviation, and overwrite self.name.
        Shouldn't be a problem as long as the user's input passed validate_month above.
        """
        full_month = self.name.split("-")[0]
        month_code = self.name.split("-")[0][:3].lower()
        for month_abbr in MONTHS_ABBR:
            if month_code in month_abbr:
                self.name = self.name.replace(full_month, month_abbr, 1)
                return
        raise ChannelError(
            f"Whoops, I was unable to abbreviate the month **{full_month}**.\n"
            "Make sure the first 3 characters of your channel's month are valid."
            "  (They should match the first 3 letters of any month.)"
        )

    async def create_channel(self, category = discord.CategoryChannel):
        """
        Creates a new channel called <self.name> in the set category.
        """
        try:
            await self.ctx.guild.create_text_channel(
                self.name,
                overwrites={},
                category=category,
                reason=f"created by {self.ctx.author.name}/{self.ctx.author.display_name}",
            )
        except Exception:
            raise ChannelError(
                "You did everything right, but an error occurred while attempting to create a new channel!\n"
                "I might be broken. Please reach out to a ParkRanger and they should be able to help you."
            )
