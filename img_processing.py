from discord.ext import commands
import discord
from PIL import Image
import requests
import re
from discord.utils import get


class ImgProcessing(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        channel = await self.bot.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        reaction = get(message.reactions, emoji=payload.emoji.name)

        if payload.emoji.name == "⏩":
            if reaction.count == 1:
                await self.gif_speedup(message, channel)

    async def gif_speedup(self, message, channel):
        async with channel.typing():

            # html = BeautifulSoup(message.content, 'html.parser')
            # urls = [a['href'] for a in html.find_all('a')]

            urls = re.findall(r'(?:http\:|https\:)?\/\/.*\.(?:gif)', message.content)

            if message.attachments:
                urls = message.attachments[0].url
            for url in urls:
                if ".gif" in url:
                    gif = Image.open(requests.get(url, stream=True).raw)
                    gif_len = gif.n_frames
                    frame_time = []
                    for i in range(gif_len):
                        frame_time.append(gif.info['duration'] / 2)

                    gif.save("temp.gif", save_all=True, duration=frame_time)
                    await channel.send(file=discord.File("temp.gif"))
