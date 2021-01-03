reply_dict = {
    "cock": "cock",
    "cock and ball": "torture",
    "based": ["based on what?", 0.1],
    "vtubers": ["cringe", 0.5],
}

random_replies = ["cringe",
                  "yikes",
                  "based",
                  "thats kinda cringe bro",
                  "ok buddy",
                  "cock"
                  ]


def rick_reply(message):
    from random import random, choice
    try:
        reply = reply_dict[message.content]
    except KeyError:
        if random() < 0.1:
            return choice(random_replies)
        else:
            if random() < 0.01:
                return "<@" + str(message.author.id) + "> I LOVE YOU"
            return None

    if type(reply) is list:
        if random() < reply[1]:
            return reply[0]
        else:
            reply = None

    return reply

