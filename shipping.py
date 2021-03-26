from discord.ext import commands
import discord
from random import choice
import random
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import requests


# TODO add image thingin
class Shipping(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name='ship')
    async def ship(self, ctx):
        if ctx.message.mentions:
            if len(ctx.message.mentions) > 2:
                await ctx.send("Sorry I am an ardent supporter of monogamy")
                return

            mention_id_1 = ctx.message.mentions[0].id
            if len(ctx.message.mentions) == 2:
                mention_id_2 = ctx.message.mentions[1].id
            else:
                mention_id_2 = ctx.message.author.id

            random.seed(abs(mention_id_1 - mention_id_2))
            ship_percent = random.randint(0, 100)

            response = self.love_response(ship_percent)
            self.img_gen(ship_percent, mention_id_1, mention_id_2)
            await ctx.channel.send(file=discord.File('assets/shipping_temp.png'))
            await ctx.send(response)
            return

        else:
            await ctx.send("Yeah but who")
            return

    def love_response(self, ship_percent):
        if ship_percent == 0:
            return str(ship_percent) + "%❤ FIGHT"

        if ship_percent < 16:
            return str(ship_percent) + "%❤ uh oh"

        if ship_percent < 34:
            return str(ship_percent) + "%❤ sorry buddy"

        if ship_percent < 51:
            return str(ship_percent) + "%❤ yeah maybe not"

        if ship_percent < 71:
            return str(ship_percent) + "%❤ sex?"

        if ship_percent < 90:
            return str(ship_percent) + "%❤ SEX"

        if ship_percent < 99:
            return str(ship_percent) + "%❤ COCK AND BALL TORTURE"

        if ship_percent == 100:
            return str(ship_percent) + "%❤ mmgmhnhffhngmfhxbfngmvhfhfhmgmggjhhhhh"

    def center_coords(self, w_1, h_1, w_2, h_2):
        w = w_1 // 2 - w_2 // 2
        h = h_1 // 2 - h_2 // 2
        return w, h

    def img_gen(self, ship_percent, mention_id_1, mention_id_2):

        usr1 = self.bot.get_user(mention_id_1)
        usr2 = self.bot.get_user(mention_id_2)
        pfp_url_1 = usr1.avatar_url
        pfp_url_2 = usr2.avatar_url

        heart = Image.open("assets/heart.png")
        heart_size = (8 * ship_percent + 1, 8 * ship_percent + 1)
        heart = heart.resize(heart_size, Image.ANTIALIAS)
        font = ImageFont.truetype("assets/Verdana.ttf", 2 * ship_percent + 1)

        pfp_1 = Image.open(requests.get(pfp_url_1, stream=True).raw)
        pfp_2 = Image.open(requests.get(pfp_url_2, stream=True).raw)

        pfp_1 = pfp_1.resize((1024, 1024), Image.ANTIALIAS)
        pfp_2 = pfp_2.resize((1024, 1024), Image.ANTIALIAS)

        width_1, height_1 = pfp_1.size
        width_heart, height_heart = heart.size

        new_image = Image.new('RGBA', (2 * width_1, height_1), (255, 0, 255, 0))

        new_image.paste(pfp_1, (0, 0))
        new_image.paste(pfp_2, (width_1, 0))

        img_w, img_h = new_image.size

        new_image.paste(heart, self.center_coords(img_w, img_h, width_heart, height_heart), heart)

        drawing = ImageDraw.Draw(new_image)
        txt_w, txt_h = drawing.textsize(str(ship_percent) + "%", font=font)
        txt_x, txt_y = self.center_coords(img_w, img_h, txt_w, txt_h)
        drawing.text((txt_x, txt_y - ship_percent + 1), str(ship_percent) + "%", (255, 255, 255), font=font)

        new_image.save('assets/shipping_temp.png', 'PNG')
