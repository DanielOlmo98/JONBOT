reply_dict = {
    "cock": "cock",
    "cock and ball": "torture"
}


def rick_reply(message):
    try:
        reply = reply_dict[message.content]
    except KeyError:
        return None
    return reply
