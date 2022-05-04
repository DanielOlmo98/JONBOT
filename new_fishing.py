import json
import asyncio
import os.path
import discord
from random import choice
from random import random
import numpy as np
from numpy.random import default_rng
import embeds
import random

from tabulate import tabulate
from dataclasses import dataclass
from discord.ext.commands import errors
from discord.ext import commands
from os import path
from random import randint
from errors import ChatError
from discord.ext.commands import errors
from tinydb import TinyDB, Query, where
from tinydb.table import Document


class NewFishingCog(commands.Cog):

    def __init__(self, bot: commands.Bot, inv_filename="fish"):
        self.bot = bot
        self.db = TinyDB("test.json", indent=4)
        self.fish_table = self.db.table('fish')
        self.inventory = Inventory(self.db)

    def get_fishdict(self, split=True):
        common_fish = [
            {'orange flopper': {'name': '<:flopper:970067116583702578>', 'size_lims': (10, 50), 'mean': 20}},
            {'green flopper': {'name': '<:green:971000839562993705>', 'size_lims': (10, 50), 'mean': 20}},
            {'blue flopper': {'name': '<:Blueflopper:971004859937611786>', 'size_lims': (10, 50),
                              'mean': 20}},
            {'light blue Small fry': {'name': '<:LightblueSmallfry:971004859153285141>',
                                      'size_lims': (10, 50), 'mean': 20}},
            {'magikarp': {'name': '<:magikar: 971342209196654642>', 'size_lims': (10, 50), 'mean': 20}},
            {'feebas': {'name': '<:feebas: 971344403060903936> ', 'size_lims': (10, 50), 'mean': 20}},
            {'horsea': {'name': '<:horsea:971344402612117524> ', 'size_lims': (10, 50), 'mean': 20}},
            {'goldeen': {'name': '<:goldeen: 971344403270619156 > ', 'size_lims': (10, 50), 'mean': 20}},
        ]
        uncommon_fish = [
            {'yellow sweetfin': {'name': '🐠 ', 'size_lims': (10, 30), 'mean': 15}},
            {'drift hop flopper': {'name': '<:DrifthopFlopper:971004859270721537> ', 'size_lims': (10, 30),
                                   'mean': 15}},
            {'crab': {'name': '🦀', 'size_lims': (10, 30), 'mean': 15}},
            {'shrimp': {'name': '🦐', 'size_lims': (10, 30), 'mean': 15}},
            {'lobster': {'name': '🦞', 'size_lims': (10, 30), 'mean': 15}},
            {'seadra': {'name': '<:seadra:971344402544996362>', 'size_lims': (50, 80), 'mean': 60}},
            {'finneon': {'name': '<:finneon:971344403144794152>', 'size_lims': (50, 80), 'mean': 60}},
            {'carvanha': {'name': '<:carvanha:971344402687619072>', 'size_lims': (50, 80), 'mean': 60}},
        ]

        rare_fish = [
            {'spicyfish': {'name': '<:spicy:971001500300111883>', 'size_lims': (10, 40), 'mean': 20}},
            {'black and blue shieldfish': {'name': '<:Blackandblueshieldfish:971004859648180244>',
                                           'size_lims': (10, 40), 'mean': 20}},
            {'slurp jellyfish': {'name': '<:SlurpJellyfish:971004859438481459>', 'size_lims': (10, 40),
                                 'mean': 20}},
            {'dolphin': {'name': '🐬', 'size_lims': (100, 250), 'mean': 150}},
            {'blowfish': {'name': '🐡', 'size_lims': (20, 40), 'mean': 25}},
            {'seaking': {'name': '<:Seaking:971344403396456458>', 'size_lims': (170, 250), 'mean': 190}},
        ]

        epic_fish = [
            {'cockfish': {'name': 'Cock fish', 'size_lims': (1, 10)}},
            {'squid': {'name': '🦑', 'size_lims': (20, 40), 'mean': 25}},
            {'ancient Scale': {'name': '<:Ancientscale:971004858805141504>', 'size_lims': (20, 70),
                               'mean': 40}},
            {'devilfish': {'name': '<:DevilFish:971004859820171324>', 'size_lims': (20, 50), 'mean': 30}},
            {'blue slurpfish': {'name': '<:Blueslurpfish:971004858939351110>', 'size_lims': (20, 50),
                                'mean': 30}},
            {'stormfish': {'name': '<:Stormfish:971004859656585236>', 'size_lims': (20, 50), 'mean': 30}},
            {'kingdra': {'name': '<:kingdra:971345631325081680>', 'size_lims': (170, 210), 'mean': 180}},
            {'milotic': {'name': '<:milotic:971344402670825523>', 'size_lims': (190, 270), 'mean': 230}},
            {'gyarados': {'name': '<:gyarados:971344634196422686>', 'size_lims': (300, 400), 'mean': 420}},
            {'sharpedo': {'name': '<:sharpedo:971345161118425100>', 'size_lims': (210, 290), 'mean': 230}},
            {'nishikikoi': {'name': '<:koi:971353716739420230>', 'size_lims': (10, 30), 'mean': 15}},
        ]

        legendary_fish = [
            {'thermalfish': {'name': '<:Thermalfish:970068788991107102>', 'size_lims': (30, 70), 'mean': 40}},
            {'whale': {'name': '🐳', 'size_lims': (2500, 3500), 'mean': 2900}},
            {'octopus': {'name': '🐙', 'size_lims': (40, 90), 'mean': 50}},
            {'stare': {'name': ' <:stare:956548708399452211>', 'size_lims': (1, 10), 'mean': 1}},
            {'crocodile': {'name': '🐊', 'size_lims': (400, 700), 'mean': 500}},
            {'shark': {'name': '🦈', 'size_lims': (100, 250), 'mean': 150}},
            {'seal': {'name': '🦭', 'size_lims': (150, 300), 'mean': 200}},
            {'kyogre': {'name': '<:kyogre:971344403077677127>', 'size_lims': (400, 600), 'mean': 450}},
            {'tuna': {'name': '<:Tuna:971344403304185866>', 'size_lims': (40, 200), 'mean': 80}},
        ]
        mythical_fish = [
            {'midas Flopper': {'name': '<:MidasFlopper:971004859803398154>', 'size_lims': (30, 70),
                               'mean': 40}},
            {'dragon': {'name': 'DORAGON 🐉', 'size_lims': (800, 1500), 'mean': 1000}},
            {'tengu': {'name': 'japanese goburin 👺', 'size_lims': (130, 180), 'mean': 140}},
            {'majima': {'name': 'MAJIMA NO NII SAN?? <:majimbo:971356122822877234>', 'size_lims': (130, 180),
                        'mean': 140}},
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
        results = self.fish_table.search(where('chance') > random.random())
        smallest = 2
        fish = None
        for result in results:
            fish_chance = result['chance']
            if smallest > fish_chance:
                fish = result
                smallest = fish_chance
        return self.Fish(**fish)

    @dataclass
    class Fish:
        name: str
        chat_name: str
        size_lims: (float, float)
        chance: float = 0.5
        rarity: str = 'common'
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
            return f'{self.chat_name}'

    @commands.command(name='fishk')
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def fish(self, ctx):
        fish = self.get_fish()
        fishsize = fish.get_fish_size()
        userid = ctx.author.id
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass
        await ctx.channel.send("fishing.. ", delete_after=5)
        await self.inventory.add_fish(userid, fish.name, fishsize)
        await asyncio.sleep(5)
        await ctx.send(f'🎣 | <@{userid}>, you caught a {fishsize:.1f} cm {fish}', delete_after=10)

    @fish.error
    async def cd_error(self, error, ctx):
        if isinstance(error, errors.CommandOnCooldown):
            await ctx.send(str(error.retry_after))

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command(name='topfish')
    async def fish_leaderboard(self, ctx, *, fishname: str):

        fishname = fishname.lower()
        fish = self.fish_table.get(where('name') == fishname)
        if fish is None:
            raise ChatError('That fish does not exist.')
        chat_name = fish['chat_name']

        inv = self.inventory.fish_leaderboard(fishname)
        if not len(inv):
            raise ChatError('No one has this fish.')

        users_largest = []
        for userinv in inv:
            username = await self.bot.fetch_user(userinv.doc_id)
            users_largest.append([username, inv[0][fishname]['size']])

        sorted_sizelist = sorted(users_largest, key=lambda i: i[-1])

        table = tabulate(sorted_sizelist,
                         headers=["User:", "Largest:"],
                         tablefmt="plain", numalign="right", floatfmt=".1f")

        await ctx.send(f'{chat_name} leaderboard')
        await ctx.send("```\n" + table + "\n```")

    @commands.cooldown(1, 60 * 15, commands.BucketType.guild)
    @commands.command(name='fishes')
    async def send_fish_info(self, ctx, *, fishname: str = None):
        if fishname is None:
            fish_list = self.fish_table.all()
        else:
            fish_list = self.fish_table.get(where('name') == fishname)
            if fish_list is None:
                raise ChatError('That fish does not exist.')

        message = ''
        for fish in fish_list:
            size_lim = fish['size_lims']
            message += f'**{fish["chat_name"]}:** {size_lim[0]} - {size_lim[1]} cm\n'
        await ctx.send(message)

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command(name='inv')
    async def send_inv(self, ctx, user: discord.User = None):
        userid = user.id if user is not None else ctx.message.author.id
        userinv = self.inventory.inv_table.get(doc_id=userid)
        if userinv is None:
            raise ChatError('How bout you get some fishes.')
        message = ""
        for fishname in userinv:
            chat_name = self.fish_table.get(where('name') == fishname)['chat_name']
            inv_fish_dict = userinv.get(fishname)
            message += f'{chat_name}:\n Amount: {inv_fish_dict["amount"]}\n Largest: {inv_fish_dict["size"]:.1f}cm\n\n'

        await ctx.send(message)


class Inventory:

    def __init__(self, db):
        self.inv_table = db.table('inv')

    async def add_fish(self, userid, fishname, size):

        def _edit_inv(size, fishname):
            def transform(doc):
                inv_fish = doc.get(fishname)
                inv_fish['amount'] += 1
                if size > inv_fish['size']:
                    inv_fish['size'] = size

            return transform

        if not self.inv_table.contains(doc_id=userid):
            self.inv_table.insert(Document({fishname: {'amount': 1, 'size': size}}, doc_id=userid))
            return

        if self.inv_table.get(doc_id=userid).get(fishname) is None:
            self.inv_table.update({fishname: {'amount': 1, 'size': size}}, doc_ids=[userid])
            return

        self.inv_table.update(_edit_inv(size, fishname), where(fishname), doc_ids=[userid])

    def fish_leaderboard(self, fishname):
        return self.inv_table.search(where(fishname).exists())
