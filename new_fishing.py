import json
import asyncio
import os.path
import discord
from random import choice, random, shuffle
import numpy as np
from numpy.random import default_rng
import embeds
import random
import re
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
from typing import List


class Fishing:

    def __init__(self, fish_table):
        self.fish_table = fish_table

    def get_fish(self):
        results = self.fish_table.search(where('chance') > random.random())
        shuffle(results)
        smallest = 2
        fish = None
        for result in results:
            fish_chance = result['chance']
            if smallest > fish_chance:
                fish = result
                smallest = fish_chance

        if fish is None:
            raise ChatError('you caught nothing')

        return self.Fish(**fish)

    @dataclass
    class Fish:
        name: str
        chat_name: str
        size_lims: (float, float)
        catching_restrictions: List
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


class NewFishingCog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = TinyDB("database/fish_db.json", indent=4)
        self.fish_table = self.db.table('fish')
        self.inventory = Inventory(self.bot)
        self.equipment = Equipment(self.bot)

    async def get_chatname(self, fishname):
        return self.fish_table.get(where('name') == fishname).get('chat_name')

    @commands.command(name='fish')
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def fish(self, ctx):
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass

        userid = ctx.author.id

        try:
            fish = Fishing(self.fish_table).get_fish()
        except ChatError as e:
            await ctx.send(f'🎣 | <@{userid}>, {e}', delete_after=15)
            return

        fishsize = fish.get_fish_size()
        userid = ctx.author.id
        await ctx.channel.send("fishing.. ", delete_after=5)
        record_msg = await self.inventory.add_fish(userid, fish.name, fishsize)
        await asyncio.sleep(5)
        await ctx.send(f'🎣 | <@{userid}>, you caught a {fishsize:.1f} cm {fish}', delete_after=10)
        if record_msg:
            await ctx.send(f'{record_msg} {fish}')

    @fish.error
    async def cd_error(self, error, ctx):
        if isinstance(error, errors.CommandOnCooldown):
            await ctx.send(str(error.retry_after))

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command(name='topfish')
    async def fish_leaderboard(self, ctx, *, fishname: str):
        fish = self.fish_table.get(where('name') == fishname)
        if fish is None:
            raise ChatError('That fish does not exist.')

        sorted_sizelist = await self.inventory.fish_leaderboard(fishname)
        table = tabulate(sorted_sizelist,
                         headers=["User:", "Largest:"],
                         tablefmt="plain", numalign="right", floatfmt=".1f")

        chat_name = fish['chat_name']
        await ctx.send(f'{chat_name} leaderboard')
        await ctx.send("```\n" + table + "\n```")

    @commands.cooldown(1, 30, commands.BucketType.guild)
    @commands.command(name='fishes')
    async def send_fish_info(self, ctx, rarity: str = None):
        if rarity is None:
            raise ChatError('What rarity?')

        fish_list = self.fish_table.search(Query().rarity.matches(rarity, flags=re.IGNORECASE))
        if fish_list is None:
            raise ChatError('No fish found.')

        message = f'**{rarity.lower().title()} fishes:**\n'
        for fish in fish_list:
            size_lim = fish['size_lims']
            message += f'{fish["chat_name"]}: {size_lim[0]} - {size_lim[1]} cm\n'
        await ctx.send(message)

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command(name='inv')
    async def send_inv(self, ctx, rarity: str = None, user: discord.User = None):
        if rarity is None:
            raise ChatError('What rarity?')

        userid = user.id if user is not None else ctx.message.author.id
        userinv = self.inventory.inv_table.get(doc_id=userid)

        if userinv is None:
            raise ChatError('How bout you get some fishes.')

        message = ""
        for fishname in userinv:
            fish_dict = self.fish_table.get(where('name') == fishname)
            if fish_dict['rarity'].lower() == rarity.lower():
                chat_name = fish_dict['chat_name']
                inv_fish_dict = userinv.get(fishname)
                message += f'**{chat_name}:** Amount: {inv_fish_dict["amount"]}, Largest: {inv_fish_dict["size"]:.1f}cm\n'

        await ctx.send(message)

    @commands.cooldown(1, 10, commands.BucketType.guild)
    @commands.command(name='pricecheck')
    async def check_balance(self, ctx, itemname: str = None):
        userid = ctx.author.id
        price = await self.equipment.get_item_price(itemname)

        if price is None:
            raise ChatError('Item not found.')

        user_balance = await self.inventory.user_balance_check(userid, price)

        can_afford = True
        message = 'Balance:     |   Price:\n'
        for fishname in price.keys():
            chatname = await self.get_chatname(fishname)
            fish_price = price[fishname]
            balance = user_balance[fishname]

            if balance < fish_price:
                can_afford = False

            message += f'{chatname}:    {balance}   |   {fish_price}\n'

        await ctx.send(message)
        return can_afford

    @commands.cooldown(1, 10, commands.BucketType.guild)
    @commands.command(name='buyf')
    async def buy_item(self, ctx, itemname: str = None):
        userid = ctx.author.id
        price = await self.equipment.get_item_price(itemname)

        if price is None:
            raise ChatError('Item not found.')

        can_afford = await self.check_balance(ctx, itemname)

        if can_afford:
            for fishname, cost in price.items():
                await self.inventory.pay(userid, fishname, cost)
        else:
            raise ChatError('You cannot afford this.')

        await self.equipment.add_item(userid, itemname)
        await ctx.send('Item purchased.')

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command(name='equiped')
    async def send_inv(self, ctx, user: discord.User = None):
        userid = user.id if user is not None else ctx.message.author.id
        equiped = await self.equipment.get_equiped_items(userid)
        await ctx.send(equiped)

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command(name='equipment')
    async def equipment(self, ctx, user: discord.User = None):
        userid = user.id if user is not None else ctx.message.author.id
        equipment = await self.equipment.get_items(userid)
        await ctx.send(equipment)


class Inventory:

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = TinyDB("database/fish_inv.json", indent=4)
        self.inv_table = self.db.table('inv')

    async def add_fish(self, userid, fishname, size):
        async def check_record():
            try:
                sorted_usrlist = await self.fish_leaderboard(fishname)
                if sorted_usrlist[0][-1] < size:
                    return f'\n🎣 | New record! {size:.1f}cm'
            except ChatError:
                return f'\n🎣 | You are the first person to catch a'

            return ''

        def _edit_inv(size, fishname):
            def transform(doc):
                inv_fish = doc.get(fishname)
                inv_fish['amount'] += 1
                if size > inv_fish['size']:
                    inv_fish['size'] = size

            return transform

        if not self.inv_table.contains(doc_id=userid):
            self.inv_table.insert(Document({fishname: {'amount': 1, 'size': size}}, doc_id=userid))
            record = await check_record()
            return f'🎣 | Welcome to the fishing paradise{record}'

        user_fish_inv = self.inv_table.get(doc_id=userid).get(fishname)
        if user_fish_inv is None:
            self.inv_table.update({fishname: {'amount': 1, 'size': size}}, doc_ids=[userid])
            record = await check_record()
            return f'🎣 | New fish!{record}'

        record = ''
        if user_fish_inv['size'] < size:
            pb = f'🎣 | Personal best! {size:.1f}cm'
            record = await check_record()
            record = record if record else pb

        self.inv_table.update(_edit_inv(size, fishname), where(fishname), doc_ids=[userid])
        return record

    async def user_balance_check(self, userid, price):
        user_balance = {}
        for fishname, cost in price.items():
            user_fish_amount = self.inv_table.get(doc_id=userid).get(fishname)['amount']
            user_balance[fishname] = user_fish_amount

        return user_balance

    async def pay(self, userid, fishname, cost):
        def _edit_inv(cost, fishname):
            def transform(doc):
                inv_fish = doc.get(fishname)
                inv_fish['amount'] -= cost

            return transform

        self.inv_table.update(_edit_inv(cost, fishname), where(fishname), doc_ids=[userid])

    async def fish_leaderboard(self, fishname):
        fishname = fishname.lower()
        inv = self.inv_table.search(where(fishname).exists())
        if not len(inv):
            raise ChatError('No one has this fish.')

        users_largest = []
        for userinv in inv:
            username = await self.bot.fetch_user(userinv.doc_id)
            users_largest.append([username.display_name, userinv[fishname]['size']])
        return sorted(users_largest, key=lambda i: i[-1], reverse=True)


class Equipment:

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.items_db = TinyDB("database/items.json", indent=4)
        self.items_inv_db = TinyDB("database/items_inv.json", indent=4)
        self.items_table = self.items_db.table('items')
        self.equiped_table = self.items_inv_db.table('equiped')
        self.item_inv_table = self.items_inv_db.table('items_inv')

        # self.items_table.insert(
        #     {'name': 'cock bait',
        #      'type': 'bait',
        #      'price': {'green flopper': 1, 'orange flopper': 2},
        #      'stats': {'nothing chance': 0.1}
        #      })
        # self.items_table.insert(
        #     {'name': 'cock lure',
        #      'type': 'lure',
        #      'price': {'green flopper': 1, 'orange flopper': 2},
        #      'stats': {'rarity chance modifier': {'epic': 0.2, 'legendary': -0.2}}
        #      })
        # self.items_table.insert(
        #     {'name': 'cock rod',
        #      'type': 'rod',
        #      'price': {'green flopper': 1},
        #      'stats': {'cooldown': -5}
        #      })
        #

    async def get_equiped_items(self, userid):
        equiped = self.equiped_table.get(doc_id=userid)
        if equiped is None:
            empty_inv = {'rod': None, 'lure': None, 'bait': None}
            self.equiped_table.insert(Document(empty_inv, doc_id=userid))
            return empty_inv
        return equiped

    async def get_items(self, userid):
        if not self.item_inv_table.contains(doc_id=userid):
            self.item_inv_table.insert(Document({'rod': [], 'lure': [], 'bait': []}, doc_id=userid))
            raise ChatError('Empy inventory')
        equiped = self.item_inv_table.get(doc_id=userid)
        return equiped

    async def add_item(self, userid, itemname):
        def _edit_inv(itemname, item_category):
            def transform(doc):
                doc[item_category].append(itemname)

            return transform

        item_category = self.items_table.get(where('name') == itemname)['type']
        self.item_inv_table.update(_edit_inv(itemname, item_category), doc_ids=[userid])
        # self.inv_table.upsert(Document({item_category: []}, doc_id=userid))

    async def get_item_price(self, itemname):
        item_price = self.items_table.get(where('name') == itemname)['price']

        return item_price
