from discord.ext import commands
import json
from os import path


def has_jonbot_perms():

    def check_if_jon_admin(ctx):
        if path.exists("admins.json"):
            with open("admins.json", "r") as f:
                admins = json.load(f)
        else: 
            return False

        return ctx.message.author.id in admins

    return commands.check(check_if_jon_admin) or commands.has_permissions(manage_guild=True)
