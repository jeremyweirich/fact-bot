import pprint
import re
import string

import discord

from fact import aggregate
from fact import ALIASES
from fact import make_prod_report
from fact import RECIPES


client = discord.Client()
INVOCATION = "!factobot"


def parse_craft(tokens):
    material = tokens[1]
    beacons = produles = 0
    target_rate = 1

    if material not in RECIPES and material not in ALIASES:
        return f"I don't have a recipe for '{material}'"

    for option, value in zip(tokens[2::2], tokens[3::2]):
        try:
            if option == "-b":
                beacons = int(value)
            elif option == "-p":
                produles = int(value)
            elif option == "-n":
                target_rate = int(value)
            else:
                return f"I don't understand this option: '{option}'"
        except ValueError:
            return f"I don't understand this value: '{value}'"

    r = make_prod_report(material, beacons, produles, target_rate=target_rate)
    if tokens[0] == "summarize":
        r = aggregate(r)
    m = f"{material} [ B{beacons} / P{produles} ]\n"
    return m + pprint.pformat(r)


def parse_recipes(tokens):
    known_recipes = sorted(list(RECIPES.keys()))

    for option, value in zip(tokens[1::2], tokens[2::2]):
        try:
            if option == "-f":
                if value not in string.ascii_lowercase:
                    return "Only letters are valid filter values"
                known_recipes = [i for i in known_recipes if i.startswith(value)]
            elif option == "-s":
                if not isinstance(value, str):
                    return "Only strings are valid search values"
                known_recipes = [i for i in known_recipes if value in i]
            else:
                return f"I don't understand this option: '{option}'"
        except ValueError:
            return f"I don't understand this value: '{value}'"

    return known_recipes


def parse_help(tokens):
    if len(tokens) > 2:
        return f"I only understand '{INVOCATION} help' or '{INVOCATION} help <command>'"
    elif len(tokens) == 2:
        command = tokens[1]
        if command not in COMMANDS:
            return f"I can't help with this command: '{command}'"
        info = COMMANDS[command]
        message = f"Help for '{command}':\n{info['helptext']}\n"
        for option, help in info.get("options", {}).items():
            message += f"\t-{option}: {help}\n"
        return message
    else:
        message = "The commands I understand are:\n"
        return message + "\n".join(
            [
                f" - {command}: {info.get('helptext', '')}"
                for command, info in COMMANDS.items()
            ]
        )


COMMANDS = {
    "craft": {
        "func": parse_craft,
        "options": {
            "b": "Number of speed beacons [default=0]",
            "n": "How many items/s to make [default=1]",
            "p": "Number of productivity modules [default=0]",
        },
        "helptext": "Recursively calculate requirements for crafting an item",
    },
    "summarize": {
        "func": parse_craft,
        "options": {
            "b": "Number of speed beacons [default=0]",
            "n": "How many items/s to make [default=1]",
            "p": "Number of productivity modules [default=0]",
        },
        "helptext": "Get total assemblers and raw materials needed to craft an item",
    },
    "recipes": {
        "func": parse_recipes,
        "options": {"f": "Filter by letter", "s": "Search by string"},
        "helptext": "Get a list of recipes I know how to make",
    },
    "help": {"func": parse_help},
}


def parse_command(command_str):
    tokens = command_str.split()
    print(tokens)
    if any([token.startswith("--") for token in tokens]):
        return "Define options with -, not --"

    command = tokens[0]
    if command in COMMANDS:
        return COMMANDS[command]["func"](tokens)
    print(f"Unknown command {command}")


@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if not re.match(rf"^{INVOCATION}", message.content):
        return

    try:
        command_str = message.content.split(INVOCATION)[-1].lower()
        response = parse_command(command_str)
        if response:
            await message.channel.send(response)
        else:
            await message.channel.send(
                "Sorry, I don't understand that command!  Try !factobot help"
            )
    except Exception as e:
        error = "Jeremy didn't think this would go wrong:\n"
        error += str(e)
        import traceback

        print(traceback.format_exc())
        await message.channel.send(error)


if __name__ == "__main__":
    # import os
    # from dotenv import load_dotenv
    #
    # load_dotenv()
    # TOKEN = os.getenv("BOT_TOKEN")
    # client.run(TOKEN)
    print(parse_command("help recipes"))
