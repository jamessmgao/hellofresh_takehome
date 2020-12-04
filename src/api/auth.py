import os
import functools

from flask import Blueprint, request, abort, jsonify, g
from flask_inputs import Inputs
from flask_inputs.validators import JsonSchema

bp = Blueprint("auth", __name__, url_prefix="/auth")

from werkzeug.security import check_password_hash, generate_password_hash


register_schema = {
    "type": "object",
    "required": ["username", "password"],
    "properties": {"username": {"type": "string"}, "password": {"type": "string"}},
}


class RegisterInputs(Inputs):
    json = [JsonSchema(schema=register_schema)]


def validate_register():
    inputs = RegisterInputs(request)
    if inputs.validate():
        return None
    return inputs.errors()


@bp.route("/register", methods=("POST",))
def register():
    errors = validate_register()
    if errors is not None:
        abort(400)
    from .models import User

    body = request.json
    username = body["username"]
    password = body["password"]
    api_token = os.urandom(32).hex()
    try:
        User.create(
            username=username,
            password=generate_password_hash(password),
            api_token=api_token,
        )
    except Exception as e:
        abort(400)
    return jsonify({"detail": "success", "api_token": api_token})


login_schema = {
    "type": "object",
    "required": ["username", "password"],
    "properties": {"username": {"type": "string"}, "password": {"type": "string"}},
}


class LoginInputs(Inputs):
    json = [JsonSchema(schema=login_schema)]


def validate_login():
    inputs = LoginInputs(request)
    if inputs.validate():
        return None
    return inputs.errors()


@bp.route("/login", methods=("POST",))
def login():
    errors = validate_register()
    if errors is not None:
        abort(400)
    from .models import User

    body = request.json
    username = body["username"]
    password = body["password"]
    users = User.select().where(User.username == username).dicts()
    # there can exist a maximum of one user as the field
    # is asserted to be unique
    if len(users) != 1:
        abort(403)
    user = users[0]
    if not check_password_hash(user["password"], password):
        abort(403)
    return jsonify({"detail": "success", "api_token": user["api_token"]})


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        from .models import User

        api_token = request.args.get("api_token")
        if api_token is None:
            abort(403)
        users = User.select().where(User.api_token == api_token).dicts()
        if len(users) != 1:
            abort(403)
        g.user = users[0]
        return view(**kwargs)

    return wrapped_view
