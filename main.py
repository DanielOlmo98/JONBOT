import os
from replies import rick_reply
import discord
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

rick_server_id = 94440780738854912

rick = commands.Bot(command_prefix='rick')


# @client.event
# async def on_ready():
#     print(f'{client.user} has connected to Discord!')
#
#     guild = client.guilds[0]
#
#     members = '\n - '.join([member.name for member in guild.members])
#     print(f'Guild Members:\n - {members}')


@rick.event
async def on_message(message):
    if message.author.bot:
        return
    else:
        reply = rick_reply(message)
        await message.channel.send(reply)
        # await rick.process_commands(message)


# @rick.listen()
# async def on_message(message):
#     if message.content == "cock":
#         await message.channel.send("cock")




rick.run(TOKEN)
