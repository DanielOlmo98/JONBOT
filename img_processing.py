from discord.ext import commands
import discord
from PIL import Image
import requests
import re
from discord.utils import get


class ImgProcessing(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        channel = await self.bot.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        reaction = get(message.reactions, emoji=payload.emoji.name)

        if payload.emoji.name == "⏩":
            if reaction.count == 1:
                await self.gif_speedup(message, channel)

    async def gif_speedup(self, message, channel):

        urls = []
        urls = re.findall(r'(?:http\:|https\:)?\/\/.*\.(?:gif)', message.content)

        if message.attachments:
            urls.append(message.attachments[0].url)
        for url in urls:
            async with channel.typing():
                if ".gif" in url:
                    too_fast = False
                    gif = Image.open(requests.get(url, stream=True).raw)
                    gif_len = gif.n_frames
                    frame_time = []
                    for i in range(gif_len):
                        f_time = gif.info['duration'] / 2
                        if f_time < 20:
                            f_time = 20
                            too_fast = True
                        frame_time.append(f_time)

                    print(frame_time)
                    gif.save("assets/temp.gif", save_all=True, duration=frame_time)
                    if too_fast:
                        await message.channel.send("SLOW DOWN COWBOY ✋🤠🚫")
                    await channel.send(file=discord.File("assets/temp.gif"))
