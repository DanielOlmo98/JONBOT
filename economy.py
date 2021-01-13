import json
from discord.ext import commands
from os import path
import asyncio
from tabulate import tabulate


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

        loop = asyncio.get_event_loop()
        loop.create_task(self.bank_autosave())

    @commands.command(name='balance', invoke_without_subcommand=True)
    async def balance(self, ctx, *, arg: str = None):
        await self.open_account(ctx)
        if ctx.message.mentions:
            mention = ctx.message.mentions[0].id
            balance = self.users[str(mention)]["Pocket"]
            await ctx.send(arg + " has " + str(balance) + "💰 jonbucks")

        if arg is None:
            print(":)")
            balance = self.users[str(ctx.author.id)]["Pocket"]
            await ctx.send("You have " + str(balance) + "💰 jonbucks")

        if str(arg).lower() == "all":
            sorted_user_balance_dict = dict()
            for user in self.users:
                username = await self.bot.fetch_user(user)
                sorted_user_balance_dict[username.display_name] = self.users[user]["Pocket"]

            sorted_user_balance_dict = sorted(sorted_user_balance_dict.items(),
                                              key=lambda kv: (kv[1], kv[0]), reverse=True)
            table = tabulate(sorted_user_balance_dict, headers=["User:", "Balance:"],
                             tablefmt="plain", numalign="right")
            await ctx.message.channel.send("```\n" + table + "\n```")

    async def open_account(self, ctx):
        user = ctx.author

        if str(user.id) in self.users:
            return False
        else:
            await ctx.message.channel.send("Creating account for " + str(ctx.author.nick))
            self.users[str(user.id)] = {"Pocket": 0}

        with open("bank.json", "w") as f:
            json.dump(self.users, f)
        return True

    @commands.command(name='fish', invoke_without_subcommand=True)
    async def fish(self, message):
        if str(message.author.id) in self.users:

            if message.author.id == 237541845557706752:
                return await message.channel.send("SFTU LOODLE")

            if self.users[str(message.author.id)]["Pocket"] < 10:
                await message.channel.send("get some more jonbucks man,"
                                           " ( you have " + str(self.users[str(message.author.id)]["Pocket"]) + " )")
            else:
                self.users[str(message.author.id)]["Pocket"] = self.users[str(message.author.id)]["Pocket"] - 10
                await message.channel.send("fishing.. ( -10💰 )")
        elif str(message.author.id) not in self.users:
            await message.channel.send("You need to create an account first (.balance)")

    @commands.command(name='award', invoke_without_subcommand=True)
    async def award(self, message, arg1, arg2):
        award_perms = [540175819033542666, 90182404404170752]

        if message.author.id not in award_perms:
            return await message.channel.send("Nice try")
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

    async def bank_autosave(self):
        while True:
            await asyncio.sleep(300)
            await self.bank_save()

    async def bank_save(self):
        with open("bank.json", "w") as f:
            json.dump(self.users, f)
