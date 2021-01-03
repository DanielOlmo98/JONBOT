

reply_dict = {
    "cock": "cock",
    "cock and ball": "torture",
    "based": ["based on what?", 1]
}


def rick_reply(message):
    import random
    try:
        reply = reply_dict[message.content]
    except KeyError:
        return None

    if type(reply) is list:
        if random() < reply[1]:
            return reply[0]
        else:
            reply = None

    return reply


