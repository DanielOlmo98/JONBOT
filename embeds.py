import discord
import random
import re

from discord.utils import get

colors = [0x4ab224, 0xebac00, 0xff0544, 0xff00c8, 0x00ffee]


def help_embed():
    embed = discord.Embed(title="Commands and what they do", colour=random.choice(colors))
    embed.set_thumbnail(
        url="https://cdn.discordapp.com/attachments/118433598071242753/796436695519461396/13gpny7ajo961.png")
    embed.add_field(name="Yt", value="searches youtube for a specific video", inline=True)
    embed.add_field(name="Subscribe", value="lets you subscribe", inline=False)
    embed.add_field(name="Invite", value="Sends an invite for adding the bot to a server", inline=True)
    embed.add_field(name="Quote (arg)",
                    value="Sends out a message containing people with quotes or a quote of the specifed person.",
                    inline=False)
    embed.set_footer(text="Brought to you by reimu aka dav#3945 and IZpixl5#5264")
    return embed


def starboard_embed(message):
    if message.embeds:
        print("e")

        if message.embeds[0].url.endswith(("jpg", "png")):
            embed = discord.Embed(description=re.sub(r'http\S+', '', message.content), colour=random.choice(colors))
            embed.set_author(name=message.author.name + " in " + "#" + message.channel.name,
                             icon_url=message.author.avatar_url)
            embedURL = message.embeds[0].url
            embed.set_image(url=embedURL)
            embed.set_footer(text=":pushpin:" + str(get(message.reactions, emoji="❌").count))

            return embed

    if message.attachments:
        if message.attachments[0].url.endswith(("jpg", "png")):

            embed = discord.Embed(description=message.content, colour=random.choice(colors))
            embed.set_author(name=message.author.name + " in " + "#" + message.channel.name,
                             icon_url=message.author.avatar_url)
            attachmentURL = message.attachments[0].url
            embed.set_image(url=attachmentURL)
            embed.set_footer(text=":pushpin:" + str(get(message.reactions, emoji="❌").count))

            return embed
        else:
            print("file not image")
            embed = discord.Embed(
                description="**Content**\n" + message.content + "\n\n**File**\n" + message.attachments[0].url,
                colour=random.choice(colors))
            embed.set_author(name=message.author.name + " in " + "#" + message.channel.name,
                             icon_url=message.author.avatar_url)
            embed.set_footer(text=":pushpin:" + str(get(message.reactions, emoji="❌").count))

            return embed
    else:
        print("message")
        embed = discord.Embed(
            description=message.content,
            colour=random.choice(colors))
        embed.set_author(name=message.author.name + " in " + "#" + message.channel.name,
                         icon_url=message.author.avatar_url)
        date = message.created_at.strftime("%Y-%m-%d at %H:%M")
        embed.set_footer(text=str(get(message.reactions, emoji="❌").count) + "   |   " + str(date),
                         icon_url="https://cdn2.iconfinder.com/data/icons/objects-23/50/1F4CC-pushpin-128.png")

        return embed
