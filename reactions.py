from discord import utils


UNVERIFIED_ROLE = "unverified"
VERIFIED_ROLE = "verified"
VERIFICATION_REACTION_COUNT = 1


class ReactionHandler:
    def __init__(self, bot, channel, payload):
        self.bot = bot
        self.channel = channel
        self.payload = payload

    async def verification_check(self):
        """
        Used primarily to check whether a message in the intro channel
        has recieved reactions from n users, where n is the required
        number to add a Verified role to a user.
        """
        print("checking verification....")
        message = await self.channel.fetch_message(self.payload.message_id)

        if len(message.reactions) >= VERIFICATION_REACTION_COUNT:
            print("expected number of reactions found...")
            guild = self.bot.get_guild(self.payload.guild_id)
            member = guild.get_member(self.payload.user_id)
            verified_role = utils.get(guild.roles, name=VERIFIED_ROLE)

            if verified_role in member.roles:
                print("member is verified....")
                unique_users = set()
                for reaction in message.reactions:
                    async for user in reaction.users():
                        if verified_role in user.roles and not user.bot:
                            unique_users.add(user.id)

                print(f"unique users: {unique_users}")
                unique_count = len(unique_users)
                if unique_count >= VERIFICATION_REACTION_COUNT:
                    print("verified!")
                    unverified_role = utils.get(guild.roles, name=UNVERIFIED_ROLE)
                    message_author = guild.get_member(message.author.id)
                    await message_author.remove_roles(unverified_role)
                    await message_author.add_roles(verified_role)
                    await message_author.send(
                        f"Welcome to {guild}, {message_author.mention}! You are now verified!")  # Send DM
                    