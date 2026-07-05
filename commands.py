from __future__ import annotations


class CommandError(Exception):
    pass


class BaseCommand:
    def __init__(self, ctx):
        self.ctx = ctx

    def validate_context(self):
        if not self.ctx:
            raise CommandError("No context object provided.")

    async def validate_channel(self, expected_channels: list[str]):
        """
        Verifies that the command has been sent from the expected channel.
        """
        if self.ctx.message.channel.name.lower() not in expected_channels:
            channel_str = " ".join(expected_channels)
            raise CommandError(f"This is in invalid Channel for the '{self.ctx.message}' command. Try any of these: {channel_str}")


class CommandWithArgs(BaseCommand):
    def __init__(self, ctx, args):
        super().__init__(ctx)
        self.args = args

    def validate_args(self, expected_min: int = 1):
        """
        Validates the presence and expected amount of args.
        """
        if not self.args:
            raise CommandError("No args provided.")

        args_len = len(self.args)
        if args_len < expected_min:
            raise CommandError(f"Expected at least {expected_min} arguments, found {args_len}.")

    def validate_syntax(self, expected_char, position=None):
        """
        Validates the presence of a special character or sequence within a command's args.
        """
        if position:
            if expected_char != self.args[position]:
                raise CommandError(f"Expected '{expected_char}' in command, but didn't find it.")
        elif expected_char not in self.args:
            raise CommandError(f"Expected '{expected_char}' in command, but didn't find it.")

    @staticmethod
    def validate_args_len(args, expected_len):
        """
        Verify that the expected number of args are present.
        Note this is a static function to allow for varied inputs of args.
        """
        args_len = len(args)
        if args_len != expected_len:
            raise CommandError(f"Unexpected number of arguments. Found {args_len}, expected {expected_len}")


class SimpleCommand(BaseCommand):
    """
    Collection of static commands without any args
    """

    @staticmethod
    async def hello(ctx, bot):
        """
        Some helpful debug data to check if the bot is working properly.
        """
        await ctx.send('Hello!')

        user_name = f'{ctx.author.name}/{ctx.author.display_name}'
        print(f'"hello" command executed by {user_name}')
        print(f'bot.user.id: {bot.user.id}')
        print(f'bot.user.display_name: {bot.user.display_name}')
        print(f'bot.user.name: {bot.user.name}')
        print(f'bot.user.global_name: {bot.user.global_name}')
        print(f'user mentions: {ctx.message.mentions}')
        print(f'role mentions: {ctx.message.role_mentions}')
        print(f'channel mentions: {ctx.message.channel_mentions}')
