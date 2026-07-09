from __future__ import annotations


class CommandError(Exception):
    pass


class BaseCommand:
    """
    Handles an incoming command.
    Note that Discord doc recommends using args with @bot.command-wrapped
    functions, but args is available from the context object. The first
    index of the ctx.args list is always a command object, the rest is
    the user's input.
    """
    def __init__(self, ctx, allowed_roles, allowed_channels):
        self.ctx = ctx
        self.allowed_roles = allowed_roles
        self.allowed_channels = allowed_channels

    async def validate_permissions(self):
        """
        Verifies various attributes of a command to ensure the author has permission to use it.
        """
        self.validate_context()
        await self.validate_channel()
        self.validate_author()

    def validate_context(self):
        if not self.ctx:
            raise CommandError("No context object provided.")

    def validate_author(self):
        member_roles = [r.name for r in self.ctx.author.roles]
        for role in self.allowed_roles:
            if role in member_roles:
                return
        else:
            raise CommandError("Sorry, but you do not have the required role to use that command.")

    async def validate_channel(self):
        """
        Verifies that the command has been sent from the expected channel.
        """
        channel_str = ", ".join(self.allowed_channels) if len(self.allowed_channels) > 1 else self.allowed_channels[0]

        if self.ctx.message.channel.name.lower() not in self.allowed_channels:
            raise CommandError(
                f"Whoops! This is in invalid Channel for that command."
                f"Try any of these channels instead: **{channel_str}**"
            )


class CommandWithArgs(BaseCommand):
    def __init__(self, ctx, allowed_roles, allowed_channels):
        super().__init__(ctx, allowed_roles, allowed_channels)

    def validate_args(self, expected: int = 1):
        """
        Validates the presence and expected amount of args.
        """
        if not self.ctx.args:
            raise CommandError("No args provided.")

        args_len = len(self.ctx.args)
        if args_len != expected:
            url = "https://github.com/Doctor-Ew-MD/ParkRanger5000/wiki/Quickstart"
            raise CommandError(
                f"I expected at least {expected} arguments, but only found {args_len}."
                f"Check out the commands doc if you need some guidance! {url}"
            )

    def validate_args_len(self, expected_len):
        """
        Verify that the expected number of args are present.
        Remember that the first arg of ctx.args is a Context object, not the user's input.
        """
        if len(self.ctx.args[1:]) != expected_len:
            raise CommandError(f"That's an unexpected number of arguments: {len(self.ctx.args) - 1} were found, but I expected {expected_len}.")

    def validate_syntax(self, expected_char, position=None):
        """
        Validates the presence of a special character or sequence within a command's args.
        """
        if position:
            if expected_char != self.ctx.args[position]:
                raise CommandError(f"I expected **{expected_char}** in command, but didn't find it.")
        elif expected_char not in self.ctx.args:
            raise CommandError(f"I expected **{expected_char}** in that command, but didn't find it.")


class SimpleCommand:
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
