import os
import discord
import json
import embeds
import time
import asyncio
import TenGiphPy
# import tenor_api
import re

from tenorscrap import Tenor
from reverse_img_search import get_vtuber, img_extensions
from subscribe import Subscribe
from economy import Economy
from music import Music
from discord.utils import get
from replies import rick_reply
from replies import listToString
from replies import sick
from dotenv import load_dotenv
from discord.ext import commands
from discord.ext.commands.errors import MissingRequiredArgument
from discord.ext.commands.errors import CommandInvokeError

#
# os.chdir("C:\\Users\\test2\\PycharmProjects\\JONBOT")
# ffmpeg_path = "C:/Users/test2/PycharmProjects/JONBOT/venv/Lib/site-packages/ffmpeg-binaries/bin/ffmpeg.exe"

# from youtubesearchpython import VideosSearch
from youtube_api import YouTubeDataAPI

# from youtube_search import YoutubeSearch

load_dotenv()
ffmpeg_path = str(os.getenv('FFMPEG'))
TOKEN = os.getenv('DISCORD_TOKEN')
YT_API = os.getenv('YT_API')
TENOR_API = os.getenv('TENOR_API')

rick_server_id = 94440780738854912

rick = commands.Bot(command_prefix='.', help_command=None, case_insensitive=True)


@rick.event
async def on_ready():
    print('Logged in as:\n{0.user.name}\n{0.user.id}'.format(rick))


@rick.event
async def on_message(message):
    await rick.process_commands(message)
    if message.author.bot:
        return
    else:
        if any(word in message.content.lower() for word in sick):
            await message.add_reaction("🤢")

        if message.attachments:
            if any(word in message.attachments[0].url.lower() for word in sick):
                await message.add_reaction("🤢")

            elif any(word in message.attachments[0].url for word in img_extensions):
                if await get_vtuber(message.attachments[0].url):
                    await message.add_reaction("🤢")

        if message.embeds:
            if message.embeds[0].url is str:
                if any(word in message.embeds[0].url.lower() for word in sick):
                    await message.add_reaction("🤢")

            elif any(word in message.embeds[0].url for word in img_extensions):
                if await get_vtuber(message.embeds[0].url):
                    await message.add_reaction("🤢")

        if any(word in message.content for word in img_extensions):
            if await get_vtuber(message.content):
                await message.add_reaction("🤢")

        reply = rick_reply(message)
        if reply is None:
            return
        else:
            await message.channel.send(reply)
    # await rick.process_commands(message)


@rick.event  # Starboard command
async def on_raw_reaction_add(payload):
    channel = await rick.fetch_channel(payload.channel_id)
    starboard_channel = discord.utils.get(payload.member.guild.text_channels, name="pins")
    message = await channel.fetch_message(payload.message_id)
    if payload.emoji.name == "📌":
        reaction = get(message.reactions, emoji=payload.emoji.name)
        if reaction.count == 4:
            await asyncio.sleep(10)
            message = await channel.fetch_message(payload.message_id)
            await starboard_channel.send(embed=embeds.starboard_embed(message))
            await message.add_reaction("🌟")


@rick.command()
async def yt(ctx, *, arg):
    yt = YouTubeDataAPI(YT_API)
    vid_search = yt.search(arg)
    await ctx.send("https://www.youtube.com/watch?v=" + vid_search[0]["video_id"])


@rick.command()
async def roll(ctx, arg1: str = None, arg2: str = None):
    from random import randint
    if arg2 is None and arg1 is None:
        return await ctx.send("```.roll 1000 would roll 1-1000\n.roll 100 1000 would roll 100-1000```")
    if arg2 is None:
        end = randint(1, int(arg1))
        await ctx.send(end)
    else:
        end = randint(int(arg1), int(arg2))
        await ctx.send(end)


@rick.command()
async def tenor2(ctx, arg1):
    t = TenGiphPy.Tenor(token=TENOR_API)
    g = TenGiphPy.Giphy(token=TENOR_API)
    # print()t.random(arg)
    await ctx.send(t.random(tag=arg1))


@rick.command()  # command for seeing quotes from specific people
async def quote(ctx, *, arg: str = None):
    quote_path = "assets/quotes/"
    if arg is None:
        quotable_user_list = os.listdir(quote_path)
        return await ctx.send(
            "The current available quotes are: " + (", ".join(quotable_user_list)))
    try:
        quote_list = os.listdir(quote_path + arg)
        from random import choice
        filename = choice(quote_list)
        await ctx.send(file=discord.File(quote_path + arg + "/" + filename))
    except FileNotFoundError:
        return await ctx.send(arg + " is not a quotable person, buddy")


# Alternate no quote arg solution
# @quote.error
# async def hello_error(ctx, error):
#     if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
#         await ctx.send("say something after !hello")


@rick.command()  # Command for adding the bot to your own server
async def invite(ctx):
    return await ctx.send(
        "https://discord.com/oauth2/authorize?client_id=795358168946442294&permissions=8&scope=bot"
    )


@rick.command()
async def gamers(ctx):
    gamer_path = "assets/gamers/"
    gamer_images = os.listdir(gamer_path)
    from random import choice
    filename = choice(gamer_images)
    await ctx.send(file=discord.File(gamer_path + filename))


@rick.command()
async def tenor(ctx, arg):
    tenor = Tenor()
    search = tenor.search(arg, limit=1)
    result = search.result(mode='dict')
    await ctx.send(result[0]['src'])


@rick.command()
async def sound(ctx, *, arg: str = None):
    sounds_path = "assets/sounds/"
    if arg is None:
        sounds_list = os.listdir(sounds_path)
        return await ctx.send(
            "The current available sounds are: " + (", ".join(sounds_list).replace('/(.*)\.[^.]+$/', '')))

    voice_channel = ctx.author.voice.channel
    # Check if user is in a voice channel
    channel = voice_channel.name

    if ctx.author.voice.channel() is not None:
        voice_channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            vc = await voice_channel.connect()
            print(f"Voice Channel: {voice_channel}")

        elif voice_channel is not ctx.voice_client.channel:
            await ctx.voice_client.move_to(voice_channel)
            vc = ctx.voice_client

        else:
            vc = ctx.voice_client
            print(f"Voice Channel: {voice_channel}")

        try:
            sounds_list = os.listdir(sounds_path + arg)
            from random import choice
            filename = choice(sounds_list)
        except FileNotFoundError:
            return await ctx.send(arg + " is not a sound buddy")
        except commands.errors.CommandInvokeError:
            return await ctx.send("join a vc pls")
        await asyncio.sleep(2)
        vc.play(discord.FFmpegPCMAudio("assets/sounds/" + arg + "/" + filename), after=lambda e: print('done'))

    else:
        await ctx.send("join a channel retard")


@rick.command()
async def help(ctx):
    await ctx.send(embed=embeds.help_embed())


rick.add_cog(Music(rick))
rick.add_cog(Subscribe(rick))
rick.add_cog(Economy(rick))

rick.run(TOKEN)
