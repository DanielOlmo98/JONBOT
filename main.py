import os
import discord

from discord.utils import get
from replies import rick_reply
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

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


@rick.event  #command for deleting a message when a set amount of reactions have been added
async def on_raw_reaction_add(payload):
    channel = await rick.fetch_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    if payload.emoji.name == "❌":
        reaction = get(message.reactions, emoji=payload.emoji.name)
    if reaction and reaction.count == 4:
        await message.delete()


@rick.command()  #command for seeing quotes from specific people
async def quote(ctx, arg):
    personquote = arg

    await ctx.send("assets/quotes/loodle/loodle1.png")


rick.run(TOKEN)
