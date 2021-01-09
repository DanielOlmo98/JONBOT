import json
from discord.ext import commands
from os import path


class Economy(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        if path.exists("bank.json"):
            with open("bank.json", "r") as f:
                self.users = json.load(f)
        else:
            self.users = dict()
            with open("bank.json", "w") as self.f:
                json.dump(self.users, self.f)

    @commands.command(name='balance', invoke_without_subcommand=True)
    async def balance(self, ctx, *, arg: str = None):
        await self.open_account(ctx.author)
        if ctx.message.mentions:
            mention = ctx.message.mentions[0].id
            balance = self.users[str(mention)]["Pocket"]
            await ctx.send(arg + " has " + str(balance) + "💰 jonbucks")

        if arg is None:
            print(":)")
            balance = self.users[str(ctx.author.id)]["Pocket"]
            await ctx.send("You have " + str(balance) + "💰 jonbucks")

    async def open_account(self, user):

        if str(user.id) in self.users:
            return False
        else:
            self.users[str(user.id)] = {"Pocket": 0}

        with open("bank.json", "w") as f:
            json.dump(self.users, f)
        return True

    @commands.command(name='fish', invoke_without_subcommand=True)
    async def fish(self, message):

        if self.users[str(message.author.id)]["Pocket"] < 10:
            await message.channel.send("get some more jonbucks man,"
                                       " ( you have " + str(self.users[str(message.author.id)]["Pocket"]) + " )")
        else:
            self.users[str(message.author.id)]["Pocket"] = self.users[str(message.author.id)]["Pocket"] - 10
            await message.channel.send("fishing.. ( -10💰 )")

    @commands.command(name='award', invoke_without_subcommand=True)
    async def award(self, message, arg1, arg2):
        if message.author.id != 540175819033542666:
            return "Nice try"
        if message.author.id == message.message.mentions[0].id:
            mention = message.message.mentions[0].id
            self.users[str(mention)]["Pocket"] = self.users[str(mention)]["Pocket"] + int(arg2)
            await message.channel.send("you gave " + str(arg2) + "💰 jonbucks to yourself")
        else:
            mention = message.message.mentions[0].id
            self.users[str(mention)]["Pocket"] = self.users[str(mention)]["Pocket"] + int(arg2)
            await message.channel.send("you gave " + str(arg2) + "💰 jonbucks to " + str(arg1))



    @commands.Cog.listener()
    async def on_message(self, message):
        if str(message.author.id) in self.users:
            self.users[str(message.author.id)]["Pocket"] = self.users[str(message.author.id)]["Pocket"] + 1
