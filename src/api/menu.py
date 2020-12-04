from .auth import login_required

from flask import Blueprint, request, abort, jsonify, g
from flask_inputs import Inputs
from flask_inputs.validators import JsonSchema

from peewee import JOIN

bp = Blueprint("menu", __name__, url_prefix="/menu")

create_schema = {
    "type": "object",
    "required": ["name", "recipe_names"],
    "properties": {
        "name": {"type": "string"},
        "recipe_names": {"type": "array", "items": {"type": "string"}},
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
    from .models import Menu, Recipe, MenuRecipe

    body = request.json
    name = body["name"]
    recipe_names = body["recipe_names"]
    # validate that recipe names correspond to recipes
    # also store ids such that no subsequent requests are required
    recipe_ids = []
    for n in recipe_names:
        res = []
        selector = Recipe.select().where(Recipe.name == n)
        for vals in selector:
            if res:
                abort(500)
            res.append(vals)
        if not res:
            print(f"name: {n} not found")
            abort(400)
        recipe_ids.append(res[0].id)
    menu = Menu.create(name=name)
    menu_id = menu.id
    for recipe_id in recipe_ids:
        MenuRecipe.create(menu=menu_id, recipe=recipe_id)
    return jsonify({"detail": "success", "id": menu_id})


@bp.route("/list")
def list():
    from .models import Menu

    # get all menu names
    # useful as this will be the unique identifier in the url
    res = []
    selector = Menu.select(Menu.name).dicts()
    for vals in selector:
        res.append(vals["name"])
    return jsonify(res)


@bp.route("/info/<menu_name>")
def info(menu_name):
    from .models import Menu, MenuRecipe, Recipe

    res = []
    info_selector = Menu.select().where(Menu.name == menu_name).dicts()
    for vals in info_selector:
        if res:
            abort(500)
        vals.pop("id")
        res.append(vals)
    if not res:
        abort(404)
    response = res[0]
    recipe_selector = (
        Recipe.select(Recipe.name)
        .join(MenuRecipe, JOIN.INNER)
        .join(Menu, JOIN.INNER)
        .where(Menu.name == menu_name)
        .dicts()
    )
    recipe_names = []

    for vals in recipe_selector:
        recipe_names.append(vals["name"])

    response["recipe_names"] = recipe_names
    return jsonify(response)
