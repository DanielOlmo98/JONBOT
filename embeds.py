import discord
import random
import re

from discord.utils import get

colors = [0x00ffee, 0xfea601, 0x644fff, 0x206694]


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
        print(message.embeds[0].url)
        jump = message.jump_url
        if message.embeds[0].url.endswith(("jpg", "png", "gif")):
            embed = discord.Embed(description=re.sub(r'http\S+', '\n', message.content), colour=random.choice(colors))
            embed.set_author(name=message.author.name + " in " + "#" + message.channel.name,
                             icon_url=message.author.avatar_url)
            embedURL = message.embeds[0].url
            embed.set_image(url=embedURL)
            date = message.created_at.strftime("%Y-%m-%d at %H:%M")
            embed.add_field(name="​", value="[[Jump to message]](" + jump + ")", inline=False)
            embed.set_footer(text=str(get(message.reactions, emoji="📌").count) + "   |   " + str(date),
                            icon_url="https://cdn2.iconfinder.com/data/icons/objects-23/50/1F4CC-pushpin-128.png")
            print("e")
            return embed

    if message.attachments:
        jump = message.jump_url
        if message.attachments[0].url.endswith(("jpg", "png", "gif")):

            embed = discord.Embed(description=message.content +
                                  "\n\n" + "[[Jump to message]](" + jump + ")",
                                  colour=random.choice(colors))
            embed.set_author(name=message.author.name + " in " + "#" + message.channel.name,
                             icon_url=message.author.avatar_url)
            attachmentURL = message.attachments[0].url
            embed.set_image(url=attachmentURL)
            date = message.created_at.strftime("%Y-%m-%d at %H:%M")
            embed.set_footer(text=str(get(message.reactions, emoji="📌").count) + "   |   " + str(date),
                         icon_url="https://cdn2.iconfinder.com/data/icons/objects-23/50/1F4CC-pushpin-128.png")

            return embed
        else:
            print("file not image")
            jump = message.jump_url
            embed = discord.Embed(
                description="**Content**\n" + message.content + "\n\n**File**\n" + message.attachments[0].url,
                colour=random.choice(colors))
            embed.set_author(name=message.author.name + " in " + "#" + message.channel.name,
                             icon_url=message.author.avatar_url)
            date = message.created_at.strftime("%Y-%m-%d at %H:%M")
            embed.add_field(name="​", value="[[Jump to message]](" + jump + ")", inline=False)
            embed.set_footer(text=str(get(message.reactions, emoji="📌").count) + "   |   " + str(date),
                         icon_url="https://cdn2.iconfinder.com/data/icons/objects-23/50/1F4CC-pushpin-128.png")

            return embed
    else:
        print(message.jump_url)
        jump = message.jump_url
        embed = discord.Embed(
            description=message.content + "\n" + "[[Jump to message]](" + jump + ")",
            colour=random.choice(colors))
        embed.set_author(name=message.author.name + " in " + "#" + message.channel.name,
                         icon_url=message.author.avatar_url)
        date = message.created_at.strftime("%Y-%m-%d at %H:%M")
        embed.add_field(name="​", value="[[Jump to message]](" + jump + ")", inline=False)
        embed.set_footer(text=str(get(message.reactions, emoji="📌").count) + "   |   " + str(date),
                         icon_url="https://cdn2.iconfinder.com/data/icons/objects-23/50/1F4CC-pushpin-128.png")

        return embed
