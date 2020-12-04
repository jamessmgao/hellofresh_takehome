from .auth import login_required

from flask import Blueprint, request, abort, jsonify, g
from flask_inputs import Inputs
from flask_inputs.validators import JsonSchema

from peewee import JOIN

bp = Blueprint("recipe", __name__, url_prefix="/recipe")

create_schema = {
    "type": "object",
    "required": [
        "name",
        "ingredients",
        "price",
        "cooking_time",
        "cooking_difficulty",
        "energy",
        "fat_total",
        "fat_saturates",
        "carbohydrate_total",
        "carbohydrate_sugars",
        "fiber",
        "protein",
        "cholesterol",
        "sodium",
    ],
    "properties": {
        "name": {"type": "string"},
        "ingredients": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["id", "amount", "unit"],
                "properties": {
                    "id": {"type": "integer"},
                    "amount": {"type": "number", "format": "float"},
                    "unit": {"type": "string"},
                },
            },
        },
        "price": {"type": "number", "format": "float"},
        "cooking_time": {
            "type": "integer",
        },
        "cooking_difficulty": {
            "type": "string",
        },
        "energy": {"type": "number", "format": "float"},
        "fat_total": {
            "type": "number",
            "format": "float",
        },
        "fat_saturates": {"type": "number", "format": "float"},
        "carbohydrate_total": {"type": "number", "format": "float"},
        "carbohydrate_sugars": {"type": "number", "format": "float"},
        "fiber": {"type": "number", "format": "float"},
        "protein": {"type": "number", "format": "float"},
        "cholesterol": {"type": "number", "format": "float"},
        "sodium": {"type": "number", "format": "float"},
    },
}


class CreateInputs(Inputs):
    json = [JsonSchema(schema=create_schema)]


def validate_create():
    inputs = CreateInputs(request)
    if inputs.validate():
        return None
    return inputs.errors


@bp.route("/create", methods=("POST",))
@login_required
def create():
    errors = validate_create()
    if errors is not None:
        print(errors)
        abort(400)
    from .models import Recipe, RecipeIngredient, Ingredient

    body = request.json
    ingredients = body.pop("ingredients")
    ingredient_ids = [x["id"] for x in ingredients]
    # convert price into integer amount of cents
    price = int(body.pop("price") * 100)
    # validate that ingredient ids are valid
    for ing_id in ingredient_ids:
        res = []
        selector = Ingredient.select().where(Ingredient.id == ing_id)
        for vals in selector:
            if res:
                abort(500)
            res.append(vals)
        if not res:
            print(f"id: {ing_id} not found")
            abort(400)
    try:
        # required as some fields are enforced to be unique
        recipe = Recipe.create(price=price, **body)
    except Exception as e:
        print(e)
        abort(400)
    recipe_id = recipe.id
    for ingredient in ingredients:
        ingredient_id = ingredient.pop("id")
        RecipeIngredient.create(
            recipe=recipe_id, ingredient=ingredient_id, **ingredient
        )
    return jsonify({"detail": "success", "id": recipe_id})


@bp.route("/list")
def list():
    from .models import Recipe

    # get all recipes names
    # useful as this will be the unique identifier in the url
    res = []
    selector = Recipe.select(Recipe.name).dicts()
    for vals in selector:
        res.append(vals["name"])
    return jsonify(res)


@bp.route("/info/<recipe_name>")
def info(recipe_name):
    from .models import Recipe, RecipeIngredient, Ingredient

    res = []
    info_selector = Recipe.select().where(Recipe.name == recipe_name).dicts()
    for vals in info_selector:
        if res:
            abort(500)
        vals.pop("id")
        res.append(vals)
    if not res:
        abort(400)
    response = res[0]
    ingredient_selector = (
        Ingredient.select()
        .join(RecipeIngredient, JOIN.INNER)
        .join(Recipe, JOIN.INNER)
        .where(Recipe.name == recipe_name)
        .dicts()
    )
    ingredients = []
    for vals in ingredient_selector:
        vals.pop("id")
        ingredients.append(vals)
    response["ingredients"] = ingredients
    return jsonify(response)
