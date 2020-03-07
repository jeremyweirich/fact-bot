from pprint import pprint


CRAFT_SPEEDS = {1: 0.5, 2: 0.75, 3: 1.25}
SPEED_MODULE_BONUS = 0.5
PROD_BONUS = 0.1
PROD_SPEED_PENALTY = 0.15
RECIPES = {
    "wire": {"craft_time": 0.5, "items_per_craft": 2, "materials": {"copper": 1}},
    "green-circuit": {
        "craft_time": 0.5,
        "items_per_craft": 1,
        "materials": {"wire": 3, "iron": 1},
    },
    "red-circuit": {
        "craft_time": 6,
        "items_per_craft": 1,
        "materials": {"green-circuit": 2, "wire": 4, "plastic": 2},
    },
}
RAW = ["iron", "copper", "plastic"]


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
    r = make_prod_report(
        target_product="red-circuit", target_rate=10, beacons=0, produles=0,
    )
    pprint(r)
    print()
    print(aggregate(r))
