from .auth import login_required

from flask import Blueprint, request, abort, jsonify, g
from flask_inputs import Inputs
from flask_inputs.validators import JsonSchema

from peewee import JOIN

bp = Blueprint("ingredient", __name__, url_prefix="/ingredient")

create_schema = {
    "type": "object",
    "required": ["name"],
    "properties": {"name": {"type": "string"}},
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
    from .models import Ingredient

    body = request.json
    name = body["name"]
    ingredient = Ingredient.create(name=name)
    return jsonify({"detail": "success", "id": ingredient.id})


@bp.route("/list")
def list():
    from .models import Ingredient

    ingredients_gen = Ingredient.select(Ingredient.name, Ingredient.id).dicts()
    ingredients = []
    for res in ingredients_gen:
        ingredients.append(res)
    return jsonify(ingredients)


@bp.route("/info/<int:ingredient_id>")
def info(ingredient_id):
    from .models import Ingredient

    ingredients = Ingredient.select().where(Ingredient.id == ingredient_id).dicts()
    if len(ingredients) != 1:
        abort(404)
    ingredient = ingredients[0]
    ingredient.pop("id")
    return jsonify(ingredient)
