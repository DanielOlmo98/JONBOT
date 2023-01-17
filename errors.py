from discord.ext.commands import errors, bot
from discord.ext import commands
import discord

class ErrorCog(commands.Cog):

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):


        if isinstance(error, commands.CommandOnCooldown):
            all_words = ctx.message.content.split()
            first_word = all_words[0]

            try:
                await ctx.message.delete()
            except discord.Forbidden:
                pass

            await ctx.send(f'Wait {int(error.retry_after)}s before using {first_word} again',
                           delete_after=error.retry_after)
            return

        if isinstance(error, commands.CommandNotFound):
            return
        
        if isinstance(error, commands.errors.BadArgument):
            await ctx.send("huh")
            return

        try:
            if isinstance(error.original, ChatError):
                await ctx.send(str(error.original))
                return
        except AttributeError:
            pass

        await ctx.send(str(error))
        raise error


class ChatError(Exception):
    pass
