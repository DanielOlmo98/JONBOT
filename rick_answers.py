from discord.ext import commands
import discord
from random import choice


class RickAnswers(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.replies = ['It is certain', 'It is decidedly so', 'Without a doubt', 'Yes – definitely',
                        'You may rely on it', 'As I see it, yes', 'Most likely', 'Outlook good',
                        'Yes Signs point to yes', 'Reply hazy', 'try again', 'Ask again later',
                        'Better not tell you now', 'Cannot predict now', 'Concentrate and ask again',
                        'Dont count on it', 'My reply is no', 'My sources say no', 'Outlook not so good',
                        'Very doubtful', 'No', 'Yes', 'Cock and balls', "Who's to say"]

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        else:
            message_lower = message.content.lower()
            if message_lower[0:4] == "rick" and message_lower[-1] == "?":
                reply = choice(self.replies)
                await message.channel.send(reply)
