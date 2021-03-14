from discord.ext import commands
import discord
from PIL import Image
import requests
import re


class RickAnswers(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        channel = await self.bot.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        if payload.emoji.name == "⏩":
            await self.gif_speedup(message, channel)

    async def gif_speedup(self, message, channel):
        url = re.sub(r'http\S+', '\n', message.content)
        if message.attachments:
            url = message.attachments[0].url

        if ".gif" in url[-4:]:
            gif = Image.open(requests.get(url, stream=True).raw)
            gif_len = gif.n_frames
            frame_time = []
            for i in range(gif_len):
                frame_time.append(gif.info['duration'] / 2)

            gif.save("temp.gif", save_all=True, duration=frame_time)

        await channel.send(file=discord.File("temp.gif"))
