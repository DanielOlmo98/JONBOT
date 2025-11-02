from discord.ext import commands
import re
from math import exp
import pathlib
import discord
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import imagetext_py
from random import choice
import requests
import re
from discord.utils import get
import os
import io
from shipping import center_coords


class ImgProcessing(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # self.load_fonts()

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        channel = await self.bot.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        reaction = get(message.reactions, emoji=payload.emoji.name)
        if channel in (discord.utils.get(payload.member.guild.text_channels, name="banter")
                       , discord.utils.get(payload.member.guild.text_channels, name="lewd")
                       , discord.utils.get(payload.member.guild.text_channels, name="general")
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

                        if too_fast:
                            await message.channel.send("SLOW DOWN COWBOY ✋🤠🚫")
                        await send_pil_img(channel, gif)
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
                        react_img = react_img.resize((200, 310), Image.LANCZOS)
                        react_img = react_img.convert("RGBA")
                        new_image = Image.new('RGBA', (mmgm.size), (255, 0, 255, 0))
                        new_image.paste(react_img, (332, 9), react_img)
                        new_image.paste(mmgm, (0, 0), mmgm)

                        await send_pil_img(channel, new_image)

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

        if "server" in ctx.message.content:
            member = ctx.guild.get_member(mention_id)
            pfp_url = str(member.guild_avatar.url)
        else:
            pfp_url = str(usr.avatar.url)
        pfp = Image.open(requests.get(pfp_url, stream=True).raw)
        await ctx.channel.send(pfp_url)


    def load_fonts(self):
        imagetext_py.FontDB.SetDefaultEmojiOptions(imagetext_py.EmojiOptions(parse_discord_emojis=True))
        font_folder_path = pathlib.Path('/', 'usr', 'share', 'fonts', 'noto')
        font_list = list(font_folder_path.glob('*.ttf'))
        for font_path in font_list:
            imagetext_py.FontDB.LoadFromPath(font_path.name, str(font_path))
        # imagetext_py.FontDB.LoadFromDir(str(font_folder_path))
        # imagetext_py.FontDB.LoadFromDir("/usr/share/fonts/")


        # cjk_font_list = list(font_folder_path.glob('*.ttc'))
        # for font_path in cjk_font_list:
        #     imagetext_py.FontDB.LoadFromPath(font_path.name, str(font_path))
        # imagetext_py.FontDB.LoadFromDir(str(cjk_font_folder_path))

        print("loaded fonts")

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(name='smug')
    async def smug(self, ctx, *args):
        async with ctx.typing():
            img_text = ""
            if args:
                img_text = " ".join(args)

            imagetext_py.FontDB.SetDefaultEmojiOptions(imagetext_py.EmojiOptions(parse_discord_emojis=True))
            smug_list = os.listdir("assets/smug")
            smug_anime_girl = Image.open(f"assets/smug/{choice(smug_list)}")
            img_w, img_h = smug_anime_girl.size

            imagetext_py.FontDB.LoadFromPath('notosans', '/usr/share/fonts/noto/NotoSans-Regular.ttf')
            imagetext_py.FontDB.LoadFromPath('notosansemoji', '/usr/share/fonts/noto/NotoColorEmoji.ttf')
            font = imagetext_py.FontDB.Query('notosans')
            # font = imagetext_py.FontDB.Query("NotoSansCuneiform-Regular.ttf")

            drawing = ImageDraw.Draw(smug_anime_girl)
            # txt_w, txt_h = drawing.textsize(img_text, font=font)
            # txt_x, txt_y = center_coords(img_w, img_h, txt_w, txt_h)

            black = imagetext_py.Paint.Color((0, 0, 0, 255))
            white = imagetext_py.Paint.Color((255,255,255,255))
            if (mention := re.search(r'<@(!*&*[0-9]+)>', img_text)):
                try:
                    username = self.bot.get_user(int(mention.group(1))).display_name
                except AttributeError:
                    username = 'yo mama'
                img_text = re.sub(r'<@!*&*[0-9]+>', username , img_text )

            text_len = len(re.sub(r'<:\w+:[0-9]+>', ' ',img_text))

            with smug_anime_girl.convert("RGBA") as draw:
                with imagetext_py.Writer(draw) as w:
                    w.draw_text_wrapped(
                        width = img_w,
                        x = img_w//2, y = img_h - ( img_h // 6 ),
                        # x = 0, y = 0,
                        ax = 0.5, ay = 0.5,
                        size = (img_w / 8) * (1 + (5 / exp(text_len))) * (img_h / (img_w * 1.3)),
                        text = img_text,
                        align = imagetext_py.TextAlign.Center,
                        font = font,
                        draw_emojis = True,
                        stroke = img_w // (15*8),
                        stroke_color=black,
                        fill=white,
                        wrap_style=imagetext_py.WrapStyle.Word
                    )


                await send_pil_img(ctx.channel, draw)


async def send_pil_img(channel, image, filetype='png'):
    with io.BytesIO() as image_binary:
                    image.save(image_binary, f'{filetype.upper()}')
                    image_binary.seek(0)
                    await channel.send(file=discord.File(fp=image_binary, filename=f'temp.{filetype}'))
