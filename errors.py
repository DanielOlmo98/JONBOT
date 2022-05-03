from discord.ext.commands import errors, bot
from discord.ext import commands


class ErrorCog(commands.Cog):
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error.original, ChatError):
            await ctx.send(str(error.original))
            return

        if isinstance(error, commands.CommandOnCooldown):
            all_words = ctx.message.content.split()
            first_word = all_words[0]

            await ctx.send(f'Wait {error.retry_after:2fs} before using {first_word} again',
                           delete_after=error.retry_after)
            return

        if isinstance(error, commands.CommandNotFound):
            return
        
        if isinstance(error, commands.errors.BadArgument):
            await ctx.send("huh")
            return

        await ctx.send(str(error))
        raise error


class ChatError(Exception):
    pass
