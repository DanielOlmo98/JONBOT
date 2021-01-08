import json
from discord.ext import commands


class Economy(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        with open("bank.json", "r") as f:
            self.users = json.load(f)

    @commands.command(name='balance', invoke_without_subcommand=True)
    async def balance(self, ctx):

        await self.open_account(ctx.author)

        balance = self.users[str(ctx.message.author.id)]["Pocket"]
        await ctx.send("You have " + str(balance) + "💰")

    async def open_account(self, user):

        if str(user.id) in self.users:
            return False
        else:
            self.users[str(user.id)] = {"Pocket": 0}

        with open("bank.json", "w") as f:
            json.dump(self.users, f)
        return True

    @commands.Cog.listener()
    async def on_message(self, message):
        if str(message.author.id) in self.users:
            self.users[str(message.author.id)]["Pocket"] = self.users[str(message.author.id)]["Pocket"] + 1

