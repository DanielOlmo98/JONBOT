import os

import discord
import json
import embeds
import time
import asyncio
import TenGiphPy
# import tenor_api
import re

from tenorscrap import Tenor  # https://github.com/suarasiy/tenorscrap
from reverse_img_search import get_vtuber, img_extensions
from subscribe import Subscribe
from economy import Economy
from music import Music
from rick_answers import RickAnswers
from img_processing import ImgProcessing
from shipping import Shipping
from main_cog import MainCog
from discord.utils import get
from replies import rick_reply
from replies import listToString
from replies import sick
from dotenv import load_dotenv
from discord.ext import commands
from discord.ext.commands.errors import MissingRequiredArgument
from discord.ext.commands.errors import CommandInvokeError
from youtube_api import YouTubeDataAPI

# os.chdir("C:\\Users\\test2\\PycharmProjects\\JONBOT")
# ffmpeg_path = "C:/Users/test2/PycharmProjects/JONBOT/venv/Lib/site-packages/ffmpeg-binaries/bin/ffmpeg.exe"

print("Starting JONBOT...")
load_dotenv()
envs = {
    'TOKEN': os.getenv('DISCORD_TOKEN'),
    'YT_API': os.getenv('YT_API'),
    'TENOR_API': os.getenv('TENOR_API'),
    'daily_verse_channel_id': int(os.getenv('daily_verse_channel_id', default=0)),
    'jonbot_logs_bots': int(os.getenv('jonbot_logs_bots', default=0)),
    'jonbot_logs': int(os.getenv('jonbot_logs', default=0)),
    'rick_server_id': int(os.getenv('rick_server_id', default=0))
}

env_var_exception = None
missing_envs = []
try:
    for key in envs:
        if envs[key] == 0 or envs[key] is None:
            missing_envs.append(key)

    if missing_envs:
        raise ValueError("Missing enviroment variables: " + ', '.join(missing_envs))
except ValueError as x:
    env_var_exception = x
    pass

# rick_server_id = 94440780738854912
intents = discord.Intents.default()
intents.members = True
rick = commands.Bot(command_prefix='.', help_command=None, case_insensitive=True, intents=intents)


@rick.event
async def on_ready():
    print('Logged in as:\n{0.user.name}\n{0.user.id}'.format(rick))
    await rick.change_presence(activity=discord.Activity(type=discord.ActivityType.watching,
                                                         name=".help  🌶️"))

    if env_var_exception is not None:
        channel = rick.get_channel(envs['rick_server_id'])
        await channel.send(env_var_exception)


rick.add_cog(
    MainCog(rick, envs['TENOR_API'], envs['YT_API'], envs['jonbot_logs_bots'], envs['jonbot_logs'],
            envs['rick_server_id']))
rick.add_cog(Music(rick))
rick.add_cog(Subscribe(rick))
rick.add_cog(Economy(rick))
rick.add_cog(RickAnswers(rick, envs['daily_verse_channel_id']))
rick.add_cog(ImgProcessing(rick))
rick.add_cog(Shipping(rick))

rick.run(envs['TOKEN'])
