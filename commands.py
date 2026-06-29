async def hello(ctx, bot, args):
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
