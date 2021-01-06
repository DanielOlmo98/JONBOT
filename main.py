import os
import discord
from music import commands
from discord.utils import get
import music
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


@rick.event  # Starboard command
async def on_raw_reaction_add(payload):
    channel = await rick.fetch_channel(payload.channel_id)
    starboardChannel = await rick.fetch_channel(795797646119141377)
    message = await channel.fetch_message(payload.message_id)
    if payload.emoji.name == "❌":
        reaction = get(message.reactions, emoji=payload.emoji.name)
    if reaction and reaction.count == 1:
        await starboardChannel.send(
            message.content + "\n Sent by " + str(message.author) + " in " + message.channel.name + "\n this message had " + str(reaction.count) + " reactions")


@rick.command()
async def yt(ctx, arg):
    yt = YouTubeDataAPI(YT_API)
    vid_search = yt.search(arg)
    await ctx.send("https://www.youtube.com/watch?v=" + vid_search[0]["video_id"])


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
async def subscribe(ctx):
    return await ctx.send(file=discord.File("assets/meme/subscribe.png"))


@rick.command()
async def gamers(ctx):
    gamer_path = "assets/gamers/"
    gamerimages = os.listdir(gamer_path)
    from random import choice
    filename = choice(gamerimages)
    await ctx.send(file=discord.File(gamer_path + filename))









@rick.event
async def on_ready():
    print('Logged in as:\n{0.user.name}\n{0.user.id}'.format(rick))

rick.run(TOKEN)


