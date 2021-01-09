import json
from discord.ext import commands
import discord
from os import path

# cock
class Subscribe(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        if path.exists("subscribe.json"):
            with open("subscribe.json", "r") as self.f:
                self.users = json.load(self.f)
        else:
            self.users = list()
            with open("subscribe.json", "w") as self.f:
                json.dump(self.users, self.f)

    @commands.command()
    async def subscribe(self, ctx):
        if str(ctx.author.name) not in self.users:
            await ctx.send("Subscribed")
            await self.add_user(str(ctx.author.name))
        else:
            await ctx.send("Already subscribed")

        return await ctx.send(file=discord.File("assets/meme/subscribe.png"))

    @commands.command()
    async def subscribed(self, ctx):
        return await ctx.send("Subscribed users: " + ", ".join(self.users))

    @commands.command(name="subscribed?")
    async def check_if_sub(self, ctx):
        if str(ctx.author.name) in self.users:
            return await ctx.send("Yes")
        else:
            await ctx.send("NO. SMASH THAT SUBSCRIBE BUTTON")
            return await ctx.send(file=discord.File("assets/meme/subscribe.png"))

    async def add_user(self, user):
        self.users.append(user)
        with open("subscribe.json", "w") as self.f:
            json.dump(self.users, self.f)
