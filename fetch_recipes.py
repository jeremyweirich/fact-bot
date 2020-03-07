import glob
import json
import os
import re


OUTPUT_DIR = "recipes"


def get_recipes(recipe_path):

    for file in glob.glob(rf"{recipe_path}\*.lua"):
        print(file)

        with open(file, "r") as f:
            content = f.read()

        content = re.sub(r"(\w+) =", r'"\1": ', content)
        content = re.sub(r"amount=", r"", content)
        content = re.sub(r"type=\"\w+\", name=", r"", content)
        content = re.sub(r"{(\"[\w-]+\"), (\d+)}", r"\1: \2", content)
        content = re.sub(r" -- .*", r"", content)
        content = content.replace("false", "False")
        content = content.replace("true", "True")

        content = content.replace("data:extend(\n{", "a = [")
        content = content.replace("}\n)", "]")

        # print(content)
        if not os.path.isdir(OUTPUT_DIR):
            os.mkdir(OUTPUT_DIR)
        p = os.path.join(OUTPUT_DIR, os.path.basename(file)).replace(".lua", ".py")
        with open(p, "w") as f:
            f.write(content)


def make_clean_recipes():
    from recipes.recipe import r
    from recipes.demo_recipe import demo_recipe
    from recipes.module import modules
    from recipes.demo_furnace_recipe import demo_furnace

    all_recipes = {}

    for recipe in r + demo_recipe + modules + demo_furnace:
        try:
            ingredients = recipe["ingredients"]
        except KeyError:
            ingredients = recipe["normal"]["ingredients"]

        all_recipes[recipe["name"]] = {
            "craft_time": 1,
            "items_per_craft": recipe.get("result_count", 1),
            "materials": ingredients,
        }

    with open("recipes.json", "w") as f:
        f.write(json.dumps(all_recipes))


if __name__ == "__main__":
    recipe_dir = r"C:\Program Files (x86)\Steam\steamapps\common\Factorio\data\base\prototypes\recipe"
    make_clean_recipes()
