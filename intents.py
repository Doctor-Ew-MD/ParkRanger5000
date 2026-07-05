import discord


class IntentsHandler:

    @staticmethod
    def set_intents():
        """
        Set the intents necessary for the bot to interact with the server.
        """
        intents = discord.Intents.default()
        intents.members = True
        intents.messages = True
        intents.message_content = True
        intents.reactions = True
        return intents
