from discord import utils

from ParkRanger5000.utils import EVENTS_CHANNEL_NAME


class MessageHandler:
    def __init__(self, bot, message):
        self.bot = bot
        self.message = message

    async def at_mention(self):
        """
        Check whether the ParkRanger role has been mentioned, or the ParkRanger5000 name.
        Should help lighten work for Park Rangers and assist anyone who is not familiar with the bot.
        """
        print("Bot was mentioned!")
        ctx = await self.bot.get_context(self.message)
        events_channel = utils.get(ctx.guild.channels, name=EVENTS_CHANNEL_NAME)
        await self.message.channel.send(
            f"Hi, I'm a bot who can help you manage event channels in {events_channel.jump_url}!\n"
            f"Check out my profile to see what commands I can offer, or wait for a response from a human Park Ranger."
        )
