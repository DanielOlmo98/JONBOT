import os
import discord
from replies import rick_reply
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

rick_server_id = 94440780738854912

rick = commands.Bot(command_prefix='rick')
client = discord.Client

@rick.event
async def on_message(message):
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
async def on_message(message):
    args = message.content.split(" ")[1:]
    if message.content.startswith("say"):
        await message.delete(message)
        await rick.send_message(message.channel, " ".join(args))






rick.run(TOKEN)
