import argparse
import re
import traceback

import discord

from fact import aggregate as make_aggregate
from fact import ALIASES
from fact import make_prod_report
from fact import RECIPES


client = discord.Client()
INVOCATION = "!factobot "


def make_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")

    craft_parser = subparsers.add_parser("craft")
    craft_parser.add_argument("recipe")
    craft_parser.add_argument("-n", "--number", type=int, default=1)
    craft_parser.add_argument("-b", "--beacons", type=int, default=0)
    craft_parser.add_argument("-p", "--produles", type=int, default=0)
    craft_parser.add_argument("-a", "--aggregate", action="store_true")

    recipe_parser = subparsers.add_parser("recipe")
    recipe_parser.add_argument("recipe", nargs="?", default="*")
    recipe_parser.add_argument("-f", "--filter")
    recipe_parser.add_argument("-s", "--search")
    recipe_parser.add_argument("-r", "--regex")

    return parser


def do_craft(recipe, beacons, produles, number, aggregate=False):
    report = make_prod_report(recipe, beacons, produles, target_rate=number)
    if aggregate:
        return make_aggregate(report)
    return report


def do_recipe(recipe, filter, search, regex):
    if recipe in ALIASES:
        recipe = ALIASES[recipe]
    if recipe != "*":
        return RECIPES.get(recipe, f"No recipe found for '{recipe}'")
    recipes = sorted(list(RECIPES.keys()) + list(ALIASES.keys()))
    if filter:
        recipes = [i for i in recipes if i.startswith(filter)]
    if search:
        recipes = [i for i in recipes if search in i]
    if regex:
        recipes = [i for i in recipes if re.match(regex, i)]
    return recipes


def delegate(params):
    command = params.pop("command")
    funcs = {
        "craft": do_craft,
        "recipe": do_recipe,
    }
    return funcs[command](**params)


def parse_command(command_str):
    print(f"> {command_str}")
    parser = make_parser()
    try:
        params = parser.parse_args(command_str.split(" "))
        return delegate(vars(params))
    except SystemExit as e:
        print(str(e))


def chunker(seq, size):
    return (seq[pos : pos + size] for pos in range(0, len(seq), size))


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

        # handle comment length
        for chunk in chunker(str(response), 2000):
            await message.channel.send(chunk)
    except Exception as e:
        error = str(e)
        print(error)

        print(traceback.format_exc())
        await message.channel.send(error)


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    load_dotenv()
    TOKEN = os.getenv("BOT_TOKEN")
    client.run(TOKEN)
