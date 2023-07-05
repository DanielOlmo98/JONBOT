from random import random, choice
import os
reply_dict = {
    "cock": "cock",
    "test": "icles",
    "cock and ball": "torture",
    "based": ["based on what?", 0.1],
    "vtubers": ["cringe", 0.5],
    "party rockers in the hou": "se tonight",
    "party rock is in the hou": "se tonight"
}

random_replies = ["cringe",
                  "yikes",
                  "based",
                  "thats kinda cringe bro",
                  "ok buddy",
                  "post bench",
                  "nice",
                  "lmao",
                  "hot",
                  "kek",

                  ]

sick = ["vtuber",
        "virtual youtuber",
        "v-tuber",
        "v-tuber",
        "vtyber",
        "vtiber",
        "btuber",
        "ctuber",
        "pekora",
        "korone",
        "coco",
        "rushia",
        "hololive",
        "watame",
        "watson-amelia",
        "ころね"

        ]


async def rick_reply(message, ctx):

    if stfu_alba(message):
        await message.reply("stfu alba")
        return None

    try:
        # any(word in message.content for word in reply_dict)
        reply = reply_dict[(message.content.lower())]
    except KeyError:
        rand = random()
        if rand < 0.005:
            return choice(random_replies)
        elif rand < 0.001:
            await say_meme(ctx)
        elif rand < 0.0001:
            return "<@" + str(message.author.id) + "> I LOVE YOU"
        return None

    if type(reply) is list:
        if random() < reply[1]:
            return reply[0]
        else:
            reply = None



    return reply


def listToString(s):
    str1 = ""

    for ele in s:
        str1 += ele

    return str1


def stfu_alba(message):
    if message.author.id == 306597250774204416:
        if message.content == ("-daily" or "- daily"):
            return True
    return False

async def say_meme(ctx):
    say_list = os.listdir("assets/say")
    await ctx.send(f"assets/say/{choice(say_list)}")
