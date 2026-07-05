from discord import utils

ERROR_MSG = ("Please include a month, day (or range of dates like 23-25), and description, like this:"
             "\n**!create dec 31 nye dance party**")
EVENTS_CHANNEL_NAME = "event-planner"


class MessageHandler:
    def __init__(self, bot, message):
        self.bot = bot
        self.message = message

    async def at_mention(self):
        """
        Reads all messages to check whether the ParkRanger role has been mentioned,
        or the ParkRanger5000 name. Not sure why anyone would do this, but it should
        help prevent DMs and assist anyone who is not familiar with the bot.
        """
        print("Bot was mentioned!")
        ctx = await self.bot.get_context(self.message)
        events_channel = utils.get(ctx.guild.channels, name=EVENTS_CHANNEL_NAME)
        await self.message.channel.send(
            f"Hi, I'm a bot made to help you create channels in {events_channel.jump_url}.\n"
            f"You can go there now to create a channel, or DM an admin if you need help.\n"
            f"When you create a channel, p{ERROR_MSG[1:]}"
        )
