#!/usr/bin/env python3
from discord.ext import commands
from discord import app_commands
import re
from math import exp
import pathlib
import discord
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import imagetext_py
from random import choice
import requests
import re
from discord.utils import get
import os
import io


class LastFM(commands.Cog):
    def __init__(self, bot: commands.Bot, lastfm_api):
        self.bot = bot
        self.lasfm_api = lastfm_api

        self.request = requests.Request(method='GET',
                                        url='http://ws.audioscrobbler.com/2.0/',
                                        params={'api_key': self.lasfm_api,
                                                'format': 'json'})
        self.session = requests.Session()

    @app_commands.command(name="toptracks", description="Top 10 most listened tracks in a given period")
    @app_commands.choices(period=[
        app_commands.Choice(name='7 days', value='7day'),
        app_commands.Choice(name='Overall', value='overall'),
        app_commands.Choice(name='1 month', value='1month'),
        app_commands.Choice(name='3 month', value='3month'),
        app_commands.Choice(name='6 month', value='6month'),
        app_commands.Choice(name='12 month', value='12month'),
    ])
    async def userTopTracks(self, interaction: discord.Interaction, user: str, period: app_commands.Choice[str]):

        params = {'method': 'user.gettoptracks', 'user': user, 'period': period.value, 'limit': 10}
        prepared = self.request.prepare()
        prepared.prepare_url(prepared.url, params)
        r = self.session.send(prepared)

        top10 = [
                 f'{index}. {track["name"]} - {track["artist"]["name"]} `{track["playcount"]} plays`'
                 for index, track in enumerate(r.json()['toptracks']['track'])
                ]

        embed = discord.Embed(title=f'Top tracks - {period.name}', description='\n'.join(top10))
        await interaction.response.send_message(embed=embed)
