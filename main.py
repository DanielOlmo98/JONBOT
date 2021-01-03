import os
from replies import rick_reply
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

rick_server_id = 94440780738854912

rick = commands.Bot(command_prefix='rick')


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


rick.run(TOKEN)
