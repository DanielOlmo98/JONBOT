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
        "gura",
        "korone",
        "coco",
        "rushia",
        "hololive",
        "watame",
        "watson-amelia",
        "ころね"

        ]

sick = [
    "vtuber",
    "poop"
]


def rick_reply(message):
    from random import random, choice

    try:
        reply = reply_dict[message.content]
    except KeyError:
        if random() < 0.01:
            return choice(random_replies)
        else:
            if random() < 0.00001:
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
