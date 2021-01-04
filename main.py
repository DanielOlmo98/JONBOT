import os
import discord

from discord.utils import get
from replies import rick_reply
from dotenv import load_dotenv
from discord.ext import commands
from discord.ext.commands.errors import MissingRequiredArgument

# from youtubesearchpython import VideosSearch
from youtube_api import YouTubeDataAPI

# from youtube_search import YoutubeSearch

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
YT_API = os.getenv('YT_API')

rick_server_id = 94440780738854912

rick = commands.Bot(command_prefix='-')


@rick.event
async def on_message(message):
    await rick.process_commands(message)
    if message.author.bot:
        return
    else:
        reply = rick_reply(message)
        if reply is None:
            return
        else:
            await message.channel.send(reply)
        # await rick.process_commands(message)


@rick.event  # command for deleting a message when a set amount of reactions have been added
async def on_raw_reaction_add(payload):
    channel = await rick.fetch_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    if payload.emoji.name == "❌":
        reaction = get(message.reactions, emoji=payload.emoji.name)
    if reaction and reaction.count == 4:
        await message.delete()


@rick.command()
async def yt(ctx, arg):
    yt = YouTubeDataAPI(YT_API)
    vid_search = yt.search(arg)
    await ctx.send("https://www.youtube.com/watch?v=" + vid_search[0]["video_id"])


@rick.command()  # command for seeing quotes from specific people
async def quote(ctx, *, arg: str = None):
    if arg is None:
        return await ctx.send(
            "The current available quotes are Reimu, Nibba, Zenith, Pseunition, Shini, GabrielB, Zack, Surd, Shoujo, Pseu and Kuuko")
    try:
        folder = os.listdir("assets/quotes/" + arg)
    except FileNotFoundError:
        return await ctx.send(arg + " is not a quotable person, buddy")

    finally:
        from random import choice
        filename = choice(folder)
        await ctx.send(file=discord.File(r'assets/quotes/' + arg + "/" + filename))


# Alternate no quote arg solution
# @quote.error
# async def hello_error(ctx, error):
#     if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
#         await ctx.send("say something after !hello")


rick.run(TOKEN)
