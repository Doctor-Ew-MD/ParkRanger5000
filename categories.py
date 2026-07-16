import datetime

import discord

from utils import MONTHS_ABBR, SilentError


class CategoryError(Exception):
    pass


class BaseCategory:
    def __init__(self, ctx, name):
        self.ctx = ctx
        self.name = name

    async def get_category(self) -> discord.CategoryChannel:
        """
        Returns the first category found with the given name.
        """
        if category := discord.utils.get(self.ctx.guild.categories, name=self.name):
            return category

        raise CategoryError(f"Category **{self.name}** doesn't exist!")


class EventCategory(BaseCategory):

    def __init__(self, ctx, name):
        super().__init__(ctx, name)
        self.ignore_channels = ["event-planner"]

    async def sort(self):
        """
        Sort the channels in a category based on month and day.
        Channels created for dates that have passed are assumed to be for
        the next year, and are sorted below "current year" events.
        """
        def month_day_key(channel):
            if channel.name in self.ignore_channels:
                return 0, 0, 0, 0

            month, day = self.generate_position_name(channel.name)

            if "-" in day and len(day.split("-")[1]) < 3:
                is_range = 1
                day = int(day.split("-")[0])
            else:
                is_range = 0
                day = int(day)

            today = datetime.date.today()
            channel_date = datetime.date(today.year, month, day)

            # if the date has already passed, assume it's next year
            if channel_date < today:
                year_offset = 1
            else:
                year_offset = 0

            return year_offset, month, day, is_range

        try:
            category_obj = await self.get_category()
            sorted_channels = sorted(category_obj.channels, key=month_day_key)
        except Exception as exc:
            raise SilentError(exc)

        payload = [
            {"id": channel.id, "position": i}
            for i, channel in enumerate(sorted_channels)
        ]
        try:
            await category_obj.guild._state.http.bulk_channel_update(category_obj.guild.id, payload)
        except Exception as exc:
            raise SilentError(exc)

    @staticmethod
    def generate_position_name(channel_name: str) -> tuple:
        """
        Transcribe a channel name by replacing the month alias with its integer.
        Should handle cases where a full month name is used or an abbreviation.
        """
        name_split = channel_name.split("-")
        try:
            month_int = MONTHS_ABBR.index(name_split[0])
        except Exception as exc:
            raise SilentError(exc)
        else:
            return month_int, name_split[1]