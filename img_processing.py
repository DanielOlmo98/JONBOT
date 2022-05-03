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
        if channel in (discord.utils.get(payload.member.guild.text_channels, name="banter")
                       , discord.utils.get(payload.member.guild.text_channels, name="lewd")
                       , discord.utils.get(payload.member.guild.text_channels, name="bible-study")):

            if payload.emoji.name == "⏩":
                if reaction.count == 1:
                    await self.gif_speedup(message, channel)

            elif payload.emoji.name == "🤤":
                if reaction.count == 1:
                    await self.mmgmhnhffhngmfhxbfngmvhfhfhmgmggjhhhhh(message, channel)
        else:
            return

    async def gif_speedup(self, message, channel):
        try:
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

                        gif.save("assets/temp.gif", save_all=True, duration=frame_time)
                        if too_fast:
                            await message.channel.send("SLOW DOWN COWBOY ✋🤠🚫")
                        await channel.send(file=discord.File("assets/temp.gif"))
        except requests.exceptions.MissingSchema:
            return

    async def mmgmhnhffhngmfhxbfngmvhfhfhmgmggjhhhhh(self, message, channel):
        try:

            urls = []
            urls = re.findall(r"(?:http\:|https\:)?\/\/.*\.(?:jpg|png|jpeg)", message.content)
            if message.attachments:
                urls.append(message.attachments[0].url)
            for url in urls:
                async with channel.typing():
                    if ".png" or ".jpeg" or ".jpg" in url:
                        mmgm = Image.open("assets/mmgm.png")
                        # thinkbubble size 200x310, center 458x174, upper corner (332,9)
                        react_img = Image.open(requests.get(url, stream=True).raw)
                        react_img = react_img.resize((200, 310), Image.ANTIALIAS)
                        react_img = react_img.convert("RGBA")
                        new_image = Image.new('RGBA', (mmgm.size), (255, 0, 255, 0))
                        new_image.paste(react_img, (332, 9), react_img)
                        new_image.paste(mmgm, (0, 0), mmgm)
                        new_image.save('assets/mmgm_temp.png', 'PNG')

                        await channel.send(file=discord.File("assets/mmgm_temp.png"))

        except requests.exceptions.MissingSchema:
            return

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(name='pfp')
    async def pfp(self, ctx):
        if len(ctx.message.mentions) > 1:
            await ctx.send("One at the time")
            return
        elif len(ctx.message.mentions) == 1:
            mention_id = ctx.message.mentions[0].id

        elif len(ctx.message.mentions) == 0:
            mention_id = ctx.message.author.id

        else:
            await ctx.send("Something weird happen")
            return
        usr = await self.bot.fetch_user(mention_id)
        pfp_url = str(usr.avatar_url)
        pfp = Image.open(requests.get(pfp_url, stream=True).raw)
        await ctx.channel.send(pfp_url)
