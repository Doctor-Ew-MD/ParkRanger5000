from discord import utils

from utils import VERIFICATION_REACTION_COUNT, VERIFIED_ROLE, UNVERIFIED_ROLE, VERIFICATION_REACTION_BLOCK


class BaseReaction:
    def __init__(self, bot, payload):
        self.bot = bot
        self.payload = payload


class VerificationReaction(BaseReaction):
    def __init__(self, bot, payload, channel):
        super().__init__(bot, payload)
        self.channel = channel

    async def verification_check(self):
        """
        Used primarily to check whether a message in the intro channel
        has received reactions from n users, where n is the required
        number to add a Verified role to a user.
        """
        guild = self.bot.get_guild(self.payload.guild_id)
        message = await self.channel.fetch_message(self.payload.message_id)
        message_author = guild.get_member(message.author.id)

        if len(message.reactions) >= VERIFICATION_REACTION_COUNT:
            unique_users = set()
            for reaction in message.reactions:
                if reaction.emoji == VERIFICATION_REACTION_BLOCK:
                    return  # we don't verify a member if the ❌ reaction is present
                async for user in reaction.users():
                    if VERIFIED_ROLE in [r.name for r in user.roles] and not user.bot:
                        unique_users.add(user.id)

            unique_count = len(unique_users)
            if unique_count >= VERIFICATION_REACTION_COUNT:
                unverified_role = utils.get(guild.roles, name=UNVERIFIED_ROLE)
                verified_role = utils.get(guild.roles, name=VERIFIED_ROLE)
                await message_author.remove_roles(unverified_role)  # Works even if the author doesn't have this role
                await message_author.add_roles(verified_role)
                await message_author.send(
                    f"Welcome to {guild}, {message_author.mention}! You are now verified!")  # Send DM
