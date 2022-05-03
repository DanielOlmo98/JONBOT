import json
import asyncio
import os.path
import discord
from random import choice
from random import random
import numpy as np
from numpy.random import default_rng
import embeds

from tabulate import tabulate
from dataclasses import dataclass
from discord.ext.commands import errors, bot
from discord.ext import commands
from os import path
from random import randint
from errors import ChatError
from discord.ext.commands import errors, bot


class NewFishingCog(commands.Cog):

    def __init__(self, bot: commands.Bot, inv_filename="fish"):
        self.bot = bot
        self.inventory = Inventory(inv_filename)

    def get_fishdict(self, split=True):
        common_fish = [{'Orange flopper': {'name': '<:flopper:970067116583702578>', 'size_lims': (10, 50), 'mean': 20}},
                       {'Green flopper': {'name': '<:green:971000839562993705>', 'size_lims': (10, 50), 'mean': 20}},
                       {'Blue flopper': {'name': '<:Blueflopper:971004859937611786>', 'size_lims': (10, 50),
                                         'mean': 20}},
                       {'Light blue Small fry': {'name': '<:LightblueSmallfry:971004859153285141>',
                                                 'size_lims': (10, 50), 'mean': 20}}
                       ]
        uncommon_fish = [{'Yellow sweetfin': {'name': '🐠 ', 'size_lims': (10, 30), 'mean': 15}},
                         {'Drift hop Flopper': {'name': '<:DrifthopFlopper:971004859270721537> ', 'size_lims': (10, 30),
                                                'mean': 15}},
                         {'Crab': {'name': '🦀', 'size_lims': (10, 30), 'mean': 15}},
                         {'Shrimp': {'name': '🦐', 'size_lims': (10, 30), 'mean': 15}},
                         {'Lobster': {'name': '🦞', 'size_lims': (10, 30), 'mean': 15}},
                         ]

        rare_fish = [{'Spicy Fish': {'name': '<:spicy:971001500300111883>', 'size_lims': (10, 40), 'mean': 20}},
                     {'Black and blue Shieldfish': {'name': '<:Blackandblueshieldfish:971004859648180244>',
                                                    'size_lims': (10, 40), 'mean': 20}},
                     {'Slurp Jellyfish': {'name': '<:SlurpJellyfish:971004859438481459>', 'size_lims': (10, 40),
                                          'mean': 20}},
                     {'Dolphin': {'name': '🐬', 'size_lims': (100, 250), 'mean': 150}},
                     {'Blowfish': {'name': '🐡', 'size_lims': (20, 40), 'mean': 25}},
                     ]

        epic_fish = [{'Cockfish': {'name': 'Cock fish', 'size_lims': (1, 10)}},
                     {'Squid': {'name': '🦑', 'size_lims': (20, 40), 'mean': 25}},
                     {'Ancient Scale': {'name': '<:Ancientscale:971004858805141504>', 'size_lims': (20, 70),
                                        'mean': 40}},
                     {'Devilfish': {'name': '<:DevilFish:971004859820171324>', 'size_lims': (20, 50), 'mean': 30}},
                     {'Blue Slurpfish': {'name': '<:Blueslurpfish:971004858939351110>', 'size_lims': (20, 50),
                                         'mean': 30}},
                     {'Stormfish': {'name': '<:Stormfish:971004859656585236>', 'size_lims': (20, 50), 'mean': 30}},
                     ]

        legendary_fish = [{'Thermal': {'name': '<:Thermalfish:970068788991107102>', 'size_lims': (30, 70), 'mean': 40}},
                          {'Whale': {'name': '🐳', 'size_lims': (2500, 3500), 'mean': 2900}},
                          {'Octopus': {'name': '🐙', 'size_lims': (40, 90), 'mean': 50}},
                          {'Stare': {'name': ' <:stare:956548708399452211>', 'size_lims': (1, 10), 'mean': 1}},
                          {'Crocodile': {'name': '🐊', 'size_lims': (400, 700), 'mean': 500}},
                          {'Shark': {'name': '🦈', 'size_lims': (100, 250), 'mean': 150}},
                          {'Seal': {'name': '🦭', 'size_lims': (150, 300), 'mean': 200}},

                          ]
        mythical_fish = [{'Midas Flopper': {'name': '', 'size_lims': (30, 70), 'mean': 40}},
                         ]
        if split:
            return {'common': common_fish, 'uncommon': uncommon_fish, 'rare': rare_fish, 'epic': epic_fish,
                    'legendary': legendary_fish, 'mythical': mythical_fish, }
        else:
            fishdict = {}
            for fish in (common_fish + uncommon_fish + rare_fish + epic_fish + legendary_fish + mythical_fish):
                fishdict.update(fish)
            return fishdict

    def get_fish(self):
        rarity = ['common', 'uncommon', 'rare', 'epic', 'legendary', 'mythical']
        chance = [0.5, 0.3, 0.1, 0.06, 0.025, 0.015]
        fish_dict = self.get_fishdict()
        fish = choice(fish_dict[np.random.choice(rarity, p=chance)])
        return fish

    @dataclass
    class Fish:
        name: str
        size_lims: (float, float)
        mean: float = None
        sigma: float = None

        def __post_init__(self):
            if self.mean is None:
                self.mean = (self.size_lims[0] + self.size_lims[1]) / 2
            if self.sigma is None:
                self.sigma = np.abs((self.mean - self.size_lims[1]) / 3)

        def get_fish_size(self):
            return np.clip(np.random.normal(self.mean, self.sigma), a_min=self.size_lims[0], a_max=self.size_lims[1])

        def __str__(self):
            return f'{self.name}'

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command(name='newfish')
    async def fish(self, ctx):
        fish_dict = self.get_fish()
        fish = self.Fish(**fish_dict[list(fish_dict)[0]])
        fishsize = fish.get_fish_size()
        userid = ctx.author.id

        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass

        await ctx.channel.send("fishing.. ", delete_after=5)
        await asyncio.sleep(5)
        await ctx.send(f'🎣 | <@{userid}>, you caught a {fishsize:.1f} cm {fish}', delete_after=10)
        await self.inventory.add_fish(userid, fish_dict, fishsize)

    @fish.error
    async def cd_error(self, error, ctx):
        if isinstance(error, errors.CommandOnCooldown):
            await ctx.send(str(error.retry_after))

    @commands.command(name='topfish')
    async def fish_leaderboard(self, ctx, fish: str = "flopper"):
        # inv = [inv[id] for id in inv.keys() if fish in inv[id]]
        inv = self.inventory.load_invs()
        filtered_inv = {k: v for k, v in inv.items() if fish in v}

        async with ctx.typing():
            sorted_user_level_dict = dict()
            sorted_user_id = sorted(filtered_inv.keys(),
                                    key=lambda x: (filtered_inv[x][fish]["largest"]), reverse=True)

            for user_id in sorted_user_id[:10]:
                username = await self.bot.fetch_user(user_id)
                sorted_user_level_dict[username.display_name] = (
                    filtered_inv[user_id][fish]["largest"], filtered_inv[user_id][fish]["count"])

        table = tabulate([(k,) + v for k, v in sorted_user_level_dict.items()],
                         headers=["User:", "Largest:", "Amount:"],
                         tablefmt="plain", numalign="right", floatfmt=".1f")

        name, _ = self.get_fishproperties(fish)

        await ctx.message.channel.send(f'{name} leaderboard')
        await ctx.message.channel.send("```\n" + table + "\n```")

    def get_fishproperties(self, fish=None):
        fishes = self.get_fishdict(split=False)
        if fish is not None:
            try:
                name = fishes[fish]["name"]
                size_lims = fishes[fish]["size_lims"]
            except KeyError:
                raise ChatError("Fish not found")

            return name, size_lims
        else:
            names = []
            size_lims = []
            for fish in fishes.values():
                names.append(fish["name"])
                size_lims.append(fish["size_lims"])
            return names, size_lims

    @commands.command(name='fishes')
    async def send_fishes(self, ctx, fish: str = None):
        if fish is not None:
            name, size_lim = self.get_fishproperties(fish)
            message = f'**{name}:** {size_lim[0]} - {size_lim[1]} cm'
        else:
            names, size_lims = self.get_fishproperties(None)
            message = ""
            for name, size_lim in zip(names, size_lims):
                message += f'**{name}:** {size_lim[0]} - {size_lim[1]} cm\n'
        await ctx.send(message)

    @commands.command(name='inv')
    async def send_inv(self, ctx, user: discord.User = None):
        userid = user.id if user is not None else ctx.message.author.id
        userinv = self.inventory.get_userinv(userid)
        fishes = self.get_fishdict(split=False)
        message = ""
        for fish, inv in userinv.items():
            message += f'{fishes[fish]["name"]}:\n Amount: {inv["count"]}\n Largest: {inv["largest"]:.1f}cm\n\n'

        await ctx.send(message)


@dataclass
class Inventory:

    def __init__(self, inv_filename):
        if not os.path.exists(f'{inv_filename}.json'):
            with open(f'{inv_filename}.json', 'w') as file:
                json.dump({}, file)
        self.inv_filename = inv_filename

    def load_invs(self):
        with open(f'{self.inv_filename}.json', 'r') as file:
            return json.load(file)

    def save_inv(self, inv):
        with open(f'{self.inv_filename}.json', 'w') as file:
            json.dump(inv, file, indent=4)

    async def add_fish(self, userid, fish, size):
        userid = str(userid)
        fishname = str(list(fish)[0])
        inv = self.load_invs()
        newcount = 1
        largest = size
        try:
            userinv = inv[userid]
        except KeyError:
            inv.update({userid: {fishname: {"count": newcount, "largest": largest}}})
            self.save_inv(inv)
            return

        try:
            newcount = userinv[fishname]["count"] + 1
            largest = size if size > userinv[fishname]["largest"] else userinv[fishname]["largest"]
            userinv.update({fishname: {"count": newcount, "largest": largest}})
        except KeyError:
            userinv.update({fishname: {"count": newcount, "largest": largest}})
        self.save_inv(inv)

    def get_userinv(self, userid):
        try:
            return self.load_invs()[str(userid)]
        except KeyError:
            raise ChatError("User not found")
