import json
from discord.ext import commands
from os import path
import asyncio
import discord
from tabulate import tabulate
from discord.ext.commands import errors

trash_array = ['📎', '🛒', '👞', '🔋', '🔧', '📰']
rare_array = ['🐳', '🐧', '🦑', '🐙', '🐬', '🐢', '🦀', '🦐', '🦈', '🐊',]
secret_array = ['alien', 'elder_god', 'dragon']


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

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send('Wait %.2fs ' % error.retry_after, delete_after=error.retry_after)

        elif isinstance(error, commands.CommandNotFound, ):
            return
        elif isinstance(error, discord.ext.commands.errors.BadArgument):
            await ctx.send("huh")
        else:
            raise error

    @commands.command(name='balance', invoke_without_subcommand=True)
    async def balance(self, ctx, *, arg: str = None):
        await self.open_account(ctx)
        if ctx.message.mentions:
            mention = ctx.message.mentions[0].id
            balance = self.users[str(mention)]["Pocket"]
            await ctx.send(arg + " has " + str(balance) + "💰 jonbucks")

        if arg is None:
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
            self.users[str(user.id)] = {"Pocket": 500, "trash": 0, "🐳": 0, "🐧": 0, "🦑": 0, "🐙": 0, "🐉": 0,
                                        "🐬": 0, "🐢": 0, "🦀": 0, "🦐": 0, "🦈": 0, "🐡": 0, "🦞": 0,
                                        "🐊": 0, "common": 0, "uncommon": 0, "alien": 0, "elder_god": 0}

        with open("bank.json", "w") as f:
            json.dump(self.users, f)
        return True

    @commands.cooldown(1, 15.0, commands.BucketType.user)
    @commands.command(name='fish', invoke_without_subcommand=True)
    async def fish(self, message):
        from random import choice
        from random import random
        rarity = random()

        if str(message.author.id) not in self.users:
            return await message.channel.send("You need to create an account first (.balance)")

        if self.users[str(message.author.id)]["Pocket"] >= 10:
            print(rarity)
            self.users[str(message.author.id)]["Pocket"] = self.users[str(message.author.id)]["Pocket"] - 10

            if rarity < 0.55:
                await message.channel.send("fishing.. ( -10💰 )", delete_after=5)
                await asyncio.sleep(5)
                await message.channel.send("🎣 | <@" + str(message.author.id) + ">, you caught: " + choice(trash_array))
                self.users[str(message.author.id)]["trash"] = self.users[str(message.author.id)]["trash"] + 1
            elif rarity < 0.89:
                await message.channel.send("fishing.. ( -10💰 )", delete_after=5)
                await asyncio.sleep(5)
                await message.channel.send("🎣 | <@" + str(message.author.id) + ">, you caught: 🐟")
                self.users[str(message.author.id)]["common"] = self.users[str(message.author.id)]["common"] + 1
            elif rarity < 0.99:
                await message.channel.send("fishing.. ( -10💰 )", delete_after=5)
                await asyncio.sleep(5)
                await message.channel.send("🎣 | <@" + str(message.author.id) + ">, you caught: 🐠")
                self.users[str(message.author.id)]["uncommon"] = self.users[str(message.author.id)]["uncommon"] + 1
            elif rarity < 0.9950:
                rare_fish = choice(rare_array)
                await message.channel.send("fishing.. ( -10💰 )", delete_after=5)
                await asyncio.sleep(5)
                await message.channel.send(f'🎣 | <@{str(message.author.id)}>, you caught: {rare_fish} \n nice')
                self.users[str(message.author.id)][rare_fish] = self.users[str(message.author.id)][rare_fish] + 1
            elif rarity < 0.9960:
                await message.channel.send("fishing.. ( -10💰 )", delete_after=5)
                await asyncio.sleep(5)
                await message.channel.send("🎣 | <@" + str(message.author.id) + ">, you caught: 👽 ayy lmao!")
                self.users[str(message.author.id)]["alien"] = self.users[str(message.author.id)]["alien"] + 1
            elif rarity < 0.9965:
                await message.channel.send("fishing.. ( -10💰 )", delete_after=5)
                await asyncio.sleep(5)
                await message.channel.send("huh?")
                await asyncio.sleep(5)
                await message.channel.send("🎣 | <@" + str(message.author.id) +
                                           ">, you caught: <:jontron1:568424285027303434> "
                                           "<:jontron2:568424284947480586>")
                await asyncio.sleep(3)
                await message.channel.send("<:r_tentacle:799786836595048469>"
                                           "<:jontron1:568424285027303434> <:jontron2:568424284947480586>"
                                           "<:l_tentacle:799786690864349204>"
                                           " nwngluii ot nilgh'ri mgr'luh shuggoth!")
                await asyncio.sleep(4)
                await message.channel.send("<:r_tentacle:799786836595048469>"
                                           "<:jontron1:568424285027303434> <:jontron2:568424284947480586>"
                                           "<:l_tentacle:799786690864349204>"
                                           "S'uhnnyth hlirgh ooboshu hafh'drn ch' shuggnyth y-geb ch' orr'eagl grah'n,")
                await asyncio.sleep(4)
                await message.channel.send("<:r_tentacle:799786836595048469>"
                                           "<:jontron1:568424285027303434> <:jontron2:568424284947480586>"
                                           "<:l_tentacle:799786690864349204>"
                                           " zhro sgn'wahl llll syha'h uln hrii phlegeth uh'e ch',"
                                           " R'lyeh llll bug f'vulgtm shogg y-llll uaaahog hrii.")

                self.users[str(message.author.id)]["elder_god"] = self.users[str(message.author.id)]["elder_god"] + 1
            else:
                await message.channel.send("throw longer retard", delete_after=5)
        else:
            await message.channel.send(f'get some more jonbucks man,'
                                       f' ( you have {str(self.users[str(message.author.id)]["Pocket"])} )',
                                       delete_after=5)

    @fish.error
    async def cd_error(self, error, ctx):
        if isinstance(error, errors.CommandOnCooldown):
            await ctx.send(str(error.retry_after))

    @commands.command(name='fishinv', invoke_without_subcommand=True)
    async def fishinv(self, message):
        if str(message.author.id) not in self.users:
            return await message.channel.send("You need to create an account first (.balance)")

        def fishinv_embed():
            embed = discord.Embed(title="Your fishes", colour=0x5AD0CB)
            embed.set_thumbnail(url=message.author.avatar_url)
            embed.add_field(name=" 📰 Trash", value=str(self.users[str(message.author.id)]["trash"]))
            embed.add_field(name=" 🐟 Common", value=str(self.users[str(message.author.id)]["common"]))
            embed.add_field(name=" 🐠 Uncommon", value=str(self.users[str(message.author.id)]["uncommon"]))
            embed.set_footer(text="Brought to you by reimu aka dav#3945 and IZpixl5#5264")
            return embed

        await message.channel.send(embed=fishinv_embed())

    @commands.command(name='rarefish', invoke_without_subcommand=True)
    async def rarefish(self, message):

        if str(message.author.id) not in self.users:
            return await message.channel.send("You need to create an account first (.balance)")

        def rarefish_embed():
            rarefish = ""
            for x in rare_array:
                if self.users[str(message.author.id)][x] > 0:
                    rarefish = rarefish + " " + x
            embed = discord.Embed(colour=0x5AD0CB,
                                  description=rarefish)
            embed.set_author(name="Your rare collection", icon_url="https://pngimg.com/uploads/star/star_PNG41471.png")
            embed.set_thumbnail(url=message.author.avatar_url)
            embed.set_footer(text="Brought to you by reimu aka dav#3945 and IZpixl5#5264")
            return embed

        await message.channel.send(embed=rarefish_embed())

    @commands.command(name='secretfish', invoke_without_subcommand=True)
    async def secret_fish(self, message):

        if str(message.author.id) not in self.users:
            return await message.channel.send("You need to create an account first (.balance)")

        def secret_fish_embed():
            secret_fish = ""
            for x in secret_array:
                if self.users[str(message.author.id)][x] > 0:
                    secret_fish = secret_fish + " " + x + self.users[str(message.author.id)][x]
            embed = discord.Embed(colour=0x5AD0CB,
                                  description=secret_fish)
            embed.set_author(name="Your super secret hauls",
                             icon_url="http://vignette2.wikia.nocookie.net/mariokart/"
                                      "images/f/fc/ItemBoxMK8.png/revision/latest?cb=20140520032019")
            embed.set_thumbnail(url=message.author.avatar_url)
            embed.set_footer(text="Brought to you by reimu aka dav#3945 and IZpixl5#5264")
            return embed

        await message.channel.send(embed=secret_fish_embed())

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
            self.users[str(message.author.id)]["Pocket"] = self.users[str(message.author.id)]["Pocket"] + 2

    async def bank_autosave(self):
        while True:
            await asyncio.sleep(100)
            await self.bank_save()

    async def bank_save(self):
        with open("bank.json", "w") as f:
            json.dump(self.users, f)
