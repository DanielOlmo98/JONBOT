from discord.ext import commands
import discord
from random import choice
import random

# TODO add image thingin
class Shipping(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name='ship')
    async def ship(self, ctx):
        if ctx.message.mentions:
            if len(ctx.message.mentions) > 2:
                await ctx.send("Sorry I am an ardent supporter of monogamy")
                return

            mention_id_1 = ctx.message.mentions[0].id
            if len(ctx.message.mentions) == 2:
                mention_id_2 = ctx.message.mentions[1].id
            else:
                mention_id_2 = ctx.message.author.id

            random.seed(abs(mention_id_1 - mention_id_2))
            ship_percent = random.randint(0, 100)

            response = self.love_response(ship_percent)
            await ctx.send(response)
            return


        else:
            await ctx.send("Yeah but who")
            return

    def love_response(self, ship_percent):
        if ship_percent == 0:
            return str(ship_percent) + "%❤ FIGHT"

        if ship_percent < 16:
            return str(ship_percent) + "%❤ uh oh"

        if ship_percent < 34:
            return str(ship_percent) + "%❤ sorry buddy"

        if ship_percent < 51:
            return str(ship_percent) + "%❤ yeah maybe not"

        if ship_percent < 71:
            return str(ship_percent) + "%❤ sex?"

        if ship_percent < 90:
            return str(ship_percent) + "%❤ SEX"

        if ship_percent < 99:
            return str(ship_percent) + "%❤ COCK AND BALL TORTURE"

        if ship_percent == 100:
            return str(ship_percent) + "%❤ mmgmhnhffhngmfhxbfngmvhfhfhmgmggjhhhhh"
