import os
import discord
from replies import rick_reply
from dotenv import load_dotenv
from discord.ext import commands
# from youtubesearchpython import VideosSearch
from youtube_api import YouTubeDataAPI
# from youtube_search import YoutubeSearch

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
YT_API = os.getenv('YT_API')

rick_server_id = 94440780738854912

rick = commands.Bot(command_prefix='rick ')


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


@rick.event
async def on_raw_reaction_add(payload):
    channel = await rick.fetch_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    await message.delete()


@rick.command()
async def yt(ctx, arg):
    yt = YouTubeDataAPI(YT_API)
    vid_search = yt.search(arg)
    await ctx.send("https://www.youtube.com/watch?v=" + vid_search[0]["video_id"])



rick.run(TOKEN)
