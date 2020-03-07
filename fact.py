import json

CRAFT_SPEEDS = {1: 0.5, 2: 0.75, 3: 1.25}
SPEED_MODULE_BONUS = 0.5
PROD_BONUS = 0.1
PROD_SPEED_PENALTY = 0.15
RAW = [
    "iron-plate",
    "copper-plate",
    "plastic-bar",
    "sulfuric-acid",
    "lubricant",
    "water",
    "coal",
    "sulfur",
    "steel-plate",
    "stone",
    "wood",
    "iron-ore",
    "copper-ore",
    "solid-fuel",
    "light-oil",
    "uranium-ore",
    "uranium-235",
    "uranium-238",
    "used-up-uranium-fuel-cell",
]
ALIASES = {
    "green-circuit": "electronic-circuit",
    "red-circuit": "advanced-circuit",
    "blue-circuit": "processing-unit",
}

with open(r"recipes.json") as f:
    RECIPES = json.loads(f.read())


def scale(mats, multiplier):
    output = {}
    for key, value in mats.items():
        if isinstance(value, dict):
            output[key] = scale(mats, multiplier)
        elif isinstance(value, str):
            output[key] = value
        else:
            output[key] = round(value * multiplier, 2)
    return output


def prod_rate(recipe, beacons, produles, machines=1, machine_tier=3):
    craft_speed = machine_craft_speed(beacons, produles, machine_tier=machine_tier)
    productivity = 1 + (produles * PROD_BONUS)
    base_rate = (machines * craft_speed) / recipe["craft_time"]
    rate = base_rate * productivity * recipe["items_per_craft"]
    material_requirements = scale(recipe["materials"], machines * base_rate)
    return rate, material_requirements


def machine_craft_speed(beacons, produles, machine_tier=3):
    craft_speed = CRAFT_SPEEDS[machine_tier]
    modifier = 1 + (SPEED_MODULE_BONUS / 2 * beacons) - (PROD_SPEED_PENALTY * produles)
    return craft_speed * modifier


def make_prod_report(target_product, beacons, produles, target_rate=1):
    target_product = ALIASES.get(target_product, target_product)
    production_rate, production_reqs = prod_rate(
        RECIPES[target_product], beacons, produles
    )
    ratio = assemblers_needed = round(target_rate / production_rate, 2)
    final_production_reqs = scale(production_reqs, ratio)
    for material, required in final_production_reqs.items():
        if material in RAW:
            pass
        elif material in RECIPES:
            final_production_reqs[material] = make_prod_report(
                material, beacons, produles, target_rate=required,
            )
        else:
            raise Exception(
                f"'{target_product}' requires material with no recipe: '{material}'"
            )
    return {
        "material": target_product,
        "assemblers": assemblers_needed,
        "inputs": final_production_reqs,
    }


def aggregate(prod_report):
    output = {
        "assemblers": {prod_report["material"]: prod_report["assemblers"]},
        "raw": {},
    }

    queue = [prod_report.pop("inputs")]
    while queue:
        inputs = queue.pop()
        for material, required in inputs.items():
            if material in RAW:
                output["raw"].setdefault(material, 0)
                output["raw"][material] += required
            else:
                output["assemblers"].setdefault(material, 0)
                output["assemblers"][material] += required["assemblers"]
                queue.append(required.pop("inputs"))
    return output


if __name__ == "__main__":
    for recipe in RECIPES:
        r = make_prod_report(
            target_product=recipe, target_rate=10, beacons=0, produles=0,
        )
        # pprint(r)
        # print()
        # print(aggregate(r))
