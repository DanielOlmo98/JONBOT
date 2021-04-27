import json
import asyncio
import discord
import embeds

from tabulate import tabulate
from discord.ext.commands import errors
from discord.ext import commands
from os import path
from random import randint

trash_array = ['📎', '🛒', '👞', '🔋', '🔧', '📰']
rare_array = ['🐳', '🐧', '🦑', '🐙', '🐬', '🐢', '🦀', '🦐', '🦈', '🐊', ]
secret_array = ['👽', '<:r_tentacle:799786836595048469> <:jontron1:568424285027303434>'
                      ' <:jontron2:568424284947480586> <:l_tentacle:799786690864349204>', '🐉']
rick = commands.Bot(command_prefix='.', help_command=None, case_insensitive=True)


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

        super().__init__()  # whatever here
        self.cd_mapping = commands.CooldownMapping.from_cooldown(1, 30, commands.BucketType.user)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            all_words = ctx.message.content.split()
            first_word = all_words[0]
            await ctx.send('Wait %.2fs ' % error.retry_after + 'before using ' + first_word + " again",
                           delete_after=error.retry_after)

        elif isinstance(error, commands.CommandNotFound, ):
            return
        elif isinstance(error, discord.ext.commands.errors.BadArgument):
            await ctx.send("huh")
        else:
            raise error

    @commands.Cog.listener()
    async def on_message(self, message):
        bucket = self.cd_mapping.get_bucket(message)
        retry_after = bucket.update_rate_limit()
        if retry_after:
            return
        else:
            if message.author.bot:
                return
            if str(message.author.id) not in self.users:
                self.users[str(message.author.id)] = {"Exp": 100, "Level": 1, "Pocket": 500}
            if "Level" not in self.users[str(message.author.id)]:
                self.users[str(message.author.id)].update({"Exp": 100, "Level": 1})
            if str(message.author.id) in self.users:
                self.users[str(message.author.id)]["Pocket"] = self.users[str(message.author.id)]["Pocket"] + 2
                self.users[str(message.author.id)]["Exp"] = self.users[str(message.author.id)]["Exp"] - randint(10, 20)
            if self.users[str(message.author.id)]["Exp"] <= 0:
                level_exp = (self.users[str(message.author.id)]["Level"] + 1) ** 2 * 35
                print(level_exp)
                await message.channel.send("Level up pog")
                self.users[str(message.author.id)]["Exp"] = self.users[str(message.author.id)]["Exp"] + int(level_exp)

                self.users[str(message.author.id)]["Level"] = self.users[str(message.author.id)]["Level"] + 1
                await asyncio.sleep(1)
                await message.channel.send(f"You're now level {self.users[str(message.author.id)]['Level']} "
                                           f"{message.author.mention}")

    @commands.command(name='level', invoke_without_subcommand=True)
    async def level(self, ctx):
        level_up_exp = self.users[str(ctx.message.author.id)]['Exp']
        await ctx.send(f"Level: {self.users[str(ctx.message.author.id)]['Level']}\n"
                       f"Exp to next level: {level_up_exp}")

    @commands.cooldown(1, 30)
    @commands.command(name='leaderboard')
    async def leaderboard(self, ctx):
        async with ctx.typing():
            sorted_user_level_dict = dict()
            sorted_user_id = sorted(self.users.keys(),
                                    key=lambda x: (self.users[x]["Level"]), reverse=True)

            for user_id in sorted_user_id[:10]:
                username = await self.bot.fetch_user(user_id)
                sorted_user_level_dict[username.display_name] = self.users[user_id]["Level"]

        table = tabulate(sorted_user_level_dict.items(), headers=["User:", "Level:", ],
                         tablefmt="plain", numalign="right")
        await ctx.message.channel.send("```\n" + table + "\n```")

    @rick.group()
    async def balance(self, ctx):
        await self.open_account(ctx)

        if ctx.message.mentions:
            mention_id = ctx.message.mentions[0].id
            mention_nick = ctx.message.mentions[0].nick
            balance = self.users[str(mention_id)]["Pocket"]
            return await ctx.send(str(mention_nick) + " has " + str(balance) + "💰 jonbucks")

        if ctx.invoked_subcommand is None:
            balance = self.users[str(ctx.author.id)]["Pocket"]
            return await ctx.send("You have " + str(balance) + "💰 jonbucks")

    @balance.command()
    async def top(self, ctx):

        async with ctx.typing():
            sorted_user_balance_dict = dict()
            sorted_user_id = sorted(self.users.keys(),
                                    key=lambda x: (self.users[x]["Pocket"]), reverse=True)

            for user_id in sorted_user_id[:10]:
                username = await self.bot.fetch_user(user_id)
                sorted_user_balance_dict[username.display_name] = self.users[user_id]["Pocket"]

            table = tabulate(sorted_user_balance_dict.items(), headers=["User:", "Balance:"],
                             tablefmt="plain", numalign="right")
            await ctx.message.channel.send("```\n" + table + "\n```")

    async def open_account(self, ctx):
        user = ctx.author

        if str(user.id) in self.users:
            return False
        else:
            await ctx.message.channel.send("Creating account for " + str(ctx.author.nick))
            self.users[str(user.id)] = {"Pocket": 500, "Exp": 0}

        with open("bank.json", "w") as f:
            json.dump(self.users, f)
        return True

    @commands.cooldown(1, 57600, commands.BucketType.user)
    @commands.command(name='daily')
    async def daily(self, ctx):
        self.users[str(ctx.author.id)]["Pocket"] = self.users[str(ctx.author.id)]["Pocket"] + 300
        await ctx.send("Payday claimed ( + 300 💰 ) ")

    @commands.cooldown(1, 10)
    @commands.command(name='beg')
    async def beg(self, ctx):
        amount = randint(3, 7)
        print(amount)
        self.users[str(ctx.author.id)]["Pocket"] = self.users[str(ctx.author.id)]["Pocket"] + amount
        await ctx.send(f'A kind stranger gave you {amount} 💰 ..')

    @commands.command(name='give', invoke_without_subcommand=True)
    async def payday(self, ctx, user: str = None, amount: str = None):
        mention = ctx.message.mentions[0]
        if user is None or amount is None:
            return await ctx.send(".give (user) (amount)")
        else:
            self.users[str(ctx.author.id)]["Pocket"] = self.users[str(ctx.author.id)]["Pocket"] - int(amount)
            self.users[str(mention.id)]["Pocket"] = self.users[str(mention.id)]["Pocket"] + int(amount)
            await ctx.send(f'Gave {amount} to {mention.mention}')

    @commands.cooldown(1, 15.0, commands.BucketType.user)
    @commands.command(name='fish', invoke_without_subcommand=True)
    async def fish(self, message):
        from random import choice
        from random import random
        rarity = random()
        try:
            self.users[str(message.author.id)]["trash"]

        except KeyError:
            self.users[str(message.author.id)].update(
                {"trash": 0, "common": 0, "uncommon": 0, '🐳': 0, '🐧': 0, '🦑': 0,
                 '🐙': 0, '🐬': 0, '🐢': 0, '🦀': 0, '🦐': 0, '🦈': 0, '🐊': 0, '👽': 0,
                 "<:r_tentacle:799786836595048469> <:jontron1:568424285027303434> <:jontron2:568424284947480586> <:l_tentacle:799786690864349204>": 0,
                 '🐉': 0, })
        if str(message.author.id) not in self.users:
            return await message.channel.send("You need to fish first (.fish)")

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
                self.users[str(message.author.id)]["👽"] = self.users[str(message.author.id)]["👽"] + 1
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
                self.users[str(message.author.id)]["<:r_tentacle:799786836595048469> "
                                                   "<:jontron1:568424285027303434> "
                                                   "<:jontron2:568424284947480586> "
                                                   "<:l_tentacle:799786690864349204>"] = \
                    self.users[str(message.author.id)]["<:r_tentacle:799786836595048469> "
                                                       "<:jontron1:568424285027303434> "
                                                       "<:jontron2:568424284947480586> "
                                                       "<:l_tentacle:799786690864349204>"] + 1
            elif rarity < 0.9975:
                await message.channel.send("fishing.. ( -10💰 )", delete_after=5)
                await asyncio.sleep(5)
                await message.channel.send("huh?")
                await asyncio.sleep(5)
                await message.channel.send("🎣 | <@" + str(message.author.id) +
                                           ">, you caught: 🐉 ")
                await asyncio.sleep(1)
                await message.channel.send("DORAGON??")
                await message.channel.send("https://media.tenor.com/images/8f8216b3462c7ddfbe29001a0e91d6a2/tenor.gif")
                self.users[str(message.author.id)]["🐉"] = self.users[str(message.author.id)]["🐉"] + 1
            elif rarity < 0.9977:
                await message.channel.send("fishing.. ( -10💰 )", delete_after=5)
                await asyncio.sleep(5)
                await message.channel.send("🎣 | <@" + str(message.author.id) +
                                           ">, you caught:  ")
                await message.channel.send("Damn man that's a pretty cute cow")
                self.users[str(message.author.id)]["<:cute_cow:836681439541985330>"] = \
                    self.users[str(message.author.id)]["<:cute_cow:836681439541985330>"] + 1
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

    @rick.group(name='fishinv', invoke_without_subcommand=True)
    async def fishinv(self, ctx):
        if ctx.invoked_subcommand is None:
            if str(ctx.message.author.id) not in self.users:
                return await ctx.message.channel.send("You need to create an account first (.balance)")

            def fishinv_embed():
                author_id = ctx.message.author.id
                embed = discord.Embed(title="Your fishes", colour=0x5AD0CB)
                embed.set_thumbnail(url=ctx.message.author.avatar_url)
                embed.add_field(name=" 📰 Trash", value=str(self.users[str(author_id)]["trash"]))
                embed.add_field(name=" 🐟 Common", value=str(self.users[str(author_id)]["common"]))
                embed.add_field(name=" 🐠 Uncommon", value=str(self.users[str(author_id)]["uncommon"]))
                embed.set_footer(text="Brought to you by reimu aka dav#3945 and IZpixl5#5264")
                return embed

            await ctx.message.channel.send(embed=fishinv_embed())

    @fishinv.command(name='rare')
    async def rare(self, message):

        if str(message.author.id) not in self.users:
            return await message.channel.send("You need to create an account first (.balance)")

        def rarefish_embed():
            rarefish = ""

            for x in rare_array:
                fish_count = self.users[str(message.author.id)][x]
                string = ""
                if fish_count > 0:

                    for _ in range(fish_count):
                        string = string + x + " "
                rarefish = rarefish + string

            embed = discord.Embed(colour=0x5AD0CB,
                                  description=rarefish)
            embed.set_author(name="Your rare collection", icon_url="https://pngimg.com/uploads/star/star_PNG41471.png")
            embed.set_thumbnail(url=message.author.avatar_url)
            embed.set_footer(text="Brought to you by reimu aka dav#3945 and IZpixl5#5264")
            return embed

        await message.channel.send(embed=rarefish_embed())

    @fishinv.command(name='secret')
    async def secret_fish(self, message):

        if str(message.author.id) not in self.users:
            return await message.channel.send("You need to create an account first (.balance)")

        def secret_fish_embed():
            secret_fish = ""
            for x in secret_array:
                fish_count = self.users[str(message.author.id)][x]
                string = ""
                if fish_count > 0:

                    for _ in range(fish_count):
                        string = string + x + " "
                secret_fish = secret_fish + string

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
    async def award(self, message, user, amount):
        award_perms = [540175819033542666, 90182404404170752]

        if message.author.id not in award_perms:
            return await message.channel.send("Nice try")
        if message.author.id == message.message.mentions[0].id:
            mention = message.message.mentions[0].id
            self.users[str(mention)]["Pocket"] = self.users[str(mention)]["Pocket"] + int(amount)
            await message.channel.send("you gave " + str(amount) + "💰 jonbucks to yourself")
        else:
            mention = message.message.mentions[0].id
            self.users[str(mention)]["Pocket"] = self.users[str(mention)]["Pocket"] + int(amount)
            await message.channel.send("you gave " + str(amount + "💰 jonbucks to " + str(user)))

    @commands.command(name='sell')
    async def sell(self, ctx, fish: str = None, amount: str = None):
        author = ctx.author.id
        if fish is None:
            return await ctx.send(embed=embeds.sell_embed())
        if amount is None:
            return await ctx.send(embed=embeds.sell_embed())
        if fish and amount:

            if fish == "common":
                if amount == "all":
                    amount = self.users[str(author)]["common"]
                    self.users[str(author)]["common"] = self.users[str(author)]["common"] - amount
                    self.users[str(author)]["Pocket"] = self.users[str(author)]["Pocket"] + 25 * amount
                    return await ctx.send(f'Sold {amount} {fish} for {int(amount) * 25} 💰')
                if int(amount) < 0:
                    return await ctx.send("Are you dumb?")
                if int(amount) > self.users[str(author)][fish]:
                    return await ctx.send("do you really have that many fish?")
                self.users[str(author)]["Pocket"] = self.users[str(author)]["Pocket"] + 25 * int(amount)
                self.users[str(author)]["common"] = self.users[str(author)]["common"] - int(amount)
                await ctx.send(f'Sold {amount} {fish} for {int(amount) * 25} 💰')

            elif fish == "trash":
                if amount == "all":
                    amount = self.users[str(author)]["trash"]
                    self.users[str(author)]["trash"] = self.users[str(author)]["trash"] - amount
                    self.users[str(author)]["Pocket"] = self.users[str(author)]["Pocket"] + 6 * amount
                    return await ctx.send(f'Sold {amount} {fish} for {int(amount) * 6} 💰')
                if int(amount) > self.users[str(author)][fish]:
                    return await ctx.send("do you really have that many fish?")
                if int(amount) < 0:
                    return await ctx.send("Are you dumb?")
                self.users[str(author)]["Pocket"] = self.users[str(author)]["Pocket"] + 6 * int(amount)
                self.users[str(author)]["trash"] = self.users[str(author)]["trash"] - int(amount)
                await ctx.send(f'Sold {amount} {fish} for {int(amount) * 6} 💰')

            elif fish == "uncommon":
                if amount == "all":
                    amount = self.users[str(author)]["uncommon"]
                    self.users[str(author)]["uncommon"] = self.users[str(author)]["uncommon"] - amount
                    self.users[str(author)]["Pocket"] = self.users[str(author)]["Pocket"] + 55 * amount
                    return await ctx.send(f'Sold {amount} {fish} for {int(amount) * 55} 💰')
                if int(amount) < 0:
                    return await ctx.send("Are you dumb?")
                if int(amount) > self.users[str(author)][fish]:
                    return await ctx.send("do you really have that many fish?")
                self.users[str(author)]["Pocket"] = self.users[str(author)]["Pocket"] + 55 * int(amount)
                self.users[str(author)]["uncommon"] = self.users[str(author)]["uncommon"] - int(amount)
                await ctx.send(f'Sold {amount} {fish} for {int(amount) * 55} 💰')
            elif fish != "uncommon" or "common" or "trash":
                await ctx.send("I don't want that 😡")

    @commands.command(name='fishupdate')
    async def fishupdate(self, ctx):
        if ctx.author.id not in (90182404404170752, 540175819033542666):
            return await ctx.send("no u DONT")
        for x in self.users:
            self.users[str(x)].update(
                {'<:cute_cow:836681439541985330>': 0, })
        return await ctx.send("it is done.")

    async def bank_autosave(self):
        while True:
            await asyncio.sleep(100)
            await self.bank_save()

    async def bank_save(self):
        with open("bank.json", "w") as f:
            json.dump(self.users, f)
