import os
import pprint
import re

import discord

from fact import aggregate
from fact import make_prod_report
from fact import RECIPES


client = discord.Client()
INVOCATION = "!factobot"


def parse_command(command):
    tokens = command.split()
    if any([token.startswith("--") for token in tokens]):
        return "Define options with -, not --"
    if tokens[0] in ["build", "summarize"]:
        material = tokens[1]
        beacons = produles = 0
        target_rate = 1
        if material not in RECIPES:
            return f"I don't have a recipe for '{material}'"
        for switch, value in zip(tokens[2::2], tokens[3::2]):
            if switch == "-b":
                beacons = int(value)
            elif switch == "-p":
                produles = int(value)
            elif switch == "-n":
                target_rate = int(value)

        r = make_prod_report(material, beacons, produles, target_rate=target_rate)
        if tokens[0] == "summarize":
            r = aggregate(r)
        m = f"{material} [ B{beacons} / P{produles} ]\n"
        return m + pprint.pformat(r)


@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if not re.match(rf"^{INVOCATION}", message.content):
        return

    command = message.content.split(INVOCATION)[-1]
    response = parse_command(command)
    if response:
        await message.channel.send(response)


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    TOKEN = os.getenv("BOT_TOKEN")
    client.run(TOKEN)
