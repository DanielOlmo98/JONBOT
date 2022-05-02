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

class NewFishingCog(commands.Cog):

    def __init__(self, bot: commands.Bot, inv_filename="fish"):
        self.bot = bot
        self.inventory = Inventory(inv_filename)

    def get_fishdict(self, split=True):
        common_fish = [{'flopper': {'name': '<:flopper:970067116583702578>', 'size_lims': (10, 50), 'mean': 20}},
                       {'green flopper': {'name': 'Green flopper', 'size_lims': (10, 50), 'mean': 20}},
                       ]

        rare_fish = [{'squid': {'name': 'Squid', 'size_lims': (20, 40)}},
                     ]

        epic_fish = [{'cockfish': {'name': 'Cock fish', 'size_lims': (1, 10)}},
                     ]

        legendary_fish = [{'thermal': {'name': 'Thermal fish', 'size_lims': (10, 60)}},
                          ]
        if split:
            return {'common': common_fish, 'rare': rare_fish, 'epic': epic_fish, 'legendary': legendary_fish}
        else:
            fishdict = {}
            for fish in (common_fish + rare_fish + epic_fish + legendary_fish):
                fishdict.update(fish)
            return fishdict

    def get_fish(self):
        rarity = ['common', 'rare', 'epic', 'legendary']
        chance = [0.5, 0.3, 0.15, 0.05]
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

    @commands.command(name='newfish')
    async def fish(self, ctx):
        fish_dict = self.get_fish()
        fish = self.Fish(**fish_dict[list(fish_dict)[0]])
        fishsize = fish.get_fish_size()
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass
        await ctx.send(f'You caught a {fishsize:.1f} cm {fish}', delete_after=5)
        await self.inventory.add_fish(ctx.message.author.id, fish_dict, fishsize)

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
                raise ValueError("Fish not found")

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
    # print('aa')
