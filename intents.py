import discord


class IntentsHandler:

    @staticmethod
    def set():
        intents = discord.Intents.default()
        intents.members = True
        intents.messages = True
        intents.message_content = True
        intents.reactions = True
        return intents
